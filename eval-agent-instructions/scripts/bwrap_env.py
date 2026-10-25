"""Harbor environment that runs each trial in a bubblewrap sandbox instead of a Docker container.

Loaded by Harbor through `--env bwrap_env:BwrapEnvironment --ek toolchain=<dir>`;
this module imports Harbor, so it runs only inside Harbor's environment.

A trial's writable top-level directories (/app, /root, /tmp, /installed-agent,
/tests, /skills, /logs) live under one scratch directory in memory and are bound
into every exec, so state persists across execs as it does in a container. Each
exec is a fresh sandbox; no adapter keeps a process running between execs.
Harbor's output mounts (/logs/agent, /logs/verifier, /logs/artifacts) bind the
trial's own directories.
"""
import asyncio
import os
import re
import shutil
import signal
from pathlib import Path, PurePosixPath

from harbor.environments.base import BaseEnvironment, ExecResult
from harbor.environments.capabilities import EnvironmentCapabilities

import sandbox
from tasks import DOCKERFILE, INSTRUCTIONS_LAYER, WORKSPACE_SETUP

WORKDIR = "/app"
TOP_DIRS = ("app", "root", "tmp", "installed-agent", "tests", "skills", "logs")
# Paths the sandbox takes from the host or the toolchain, never from an upload.
SYSTEM_DIRS = {"usr", "bin", "lib", "lib64", "sbin", "etc", "proc", "dev"}


class BwrapEnvironment(BaseEnvironment):
    def __init__(self, *args, toolchain: str, **kwargs):
        self._toolchain = Path(toolchain)
        super().__init__(*args, **kwargs)
        self._scratch = sandbox.SCRATCH / self.session_id

    @staticmethod
    def type() -> str:
        return "bwrap"

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(mounted=True)

    def _validate_definition(self):
        """Accept only the Dockerfile tasks.py writes, since start() rebuilds its steps by hand."""
        dockerfile = self.environment_dir / "Dockerfile"
        text = dockerfile.read_text()
        base = re.match(r"FROM (\S+)\n", text)
        expected = DOCKERFILE.format(base_image=base.group(1)) if base else None
        if text not in (expected, f"{expected}{INSTRUCTIONS_LAYER}"):
            raise ValueError(f"{dockerfile} is not a task Dockerfile from tasks.py")
        if not (self._toolchain / "versions.txt").is_file():
            raise FileNotFoundError(f"no toolchain at {self._toolchain}")

    async def start(self, force_build: bool) -> None:
        shutil.rmtree(self._scratch, ignore_errors=True)
        for name in TOP_DIRS:
            (self._scratch / name).mkdir(parents=True)
        (self._scratch / "owner.pid").write_text(str(os.getpid()))
        env_dir = self.environment_dir
        shutil.copytree(env_dir / "skills", self._scratch / "skills", dirs_exist_ok=True, symlinks=True)
        shutil.copytree(env_dir / "case", self._scratch / "tmp" / "case", symlinks=True)
        result = await self.exec(WORKSPACE_SETUP, cwd=WORKDIR)
        if result.return_code != 0:
            raise RuntimeError(f"workspace setup failed: {result.stdout}\n{result.stderr}")
        if (env_dir / "instructions").is_dir():
            shutil.copytree(env_dir / "instructions", self._scratch / "app", dirs_exist_ok=True)

    async def stop(self, delete: bool):
        # Always: the scratch directory may hold a key an adapter wrote to /tmp.
        shutil.rmtree(self._scratch, ignore_errors=True)

    def _binds(self) -> list[tuple[Path, str, bool]]:
        binds = [(d, f"/{d.name}", False) for d in self._scratch.iterdir() if d.is_dir()]
        binds += sandbox.toolchain_binds(self._toolchain)
        for mount in self._mounts:
            Path(mount["source"]).mkdir(parents=True, exist_ok=True)
            binds.append((Path(mount["source"]), mount["target"], bool(mount.get("read_only"))))
        return binds

    def _host_path(self, path: str) -> tuple[Path, Path]:
        """(root, host path): where a sandbox path lives on the host, under its output mount or the scratch directory."""
        target = PurePosixPath(path)
        if not target.is_absolute() or ".." in target.parts:
            raise ValueError(f"not an absolute sandbox path: {path}")
        mounts = [m for m in self._mounts if target.is_relative_to(m["target"])]
        if mounts:
            mount = max(mounts, key=lambda m: len(PurePosixPath(m["target"]).parts))
            root = Path(mount["source"])
            host = root / target.relative_to(mount["target"])
        elif len(target.parts) < 2 or target.parts[1] in SYSTEM_DIRS:
            raise ValueError(f"cannot transfer system path {path}")
        else:
            root = self._scratch
            host = root.joinpath(*target.parts[1:])
        return root, host

    def _readable(self, path: str) -> Path:
        """The host path to read for a sandbox path; a symlink the agent made could point anywhere on the host."""
        root, host = self._host_path(path)
        if not host.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"{path} leads outside the sandbox")
        return host

    async def exec(self, command: str, cwd: str | None = None, env: dict[str, str] | None = None,
                   timeout_sec: int | None = None, user: str | int | None = None) -> ExecResult:
        # Every exec runs as the namespace's root, as in the task image; `user` changes nothing.
        args = sandbox.bwrap_args(self._binds(), cwd or WORKDIR) + ["bash", "-c", command]
        process = await asyncio.create_subprocess_exec(
            *args, env=sandbox.sandbox_env(self._merge_env(env)), stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, start_new_session=True)
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_sec)
        except asyncio.TimeoutError:
            await _kill(process)
            raise RuntimeError(f"Command timed out after {timeout_sec} seconds")
        except asyncio.CancelledError:
            await _kill(process)
            raise
        return ExecResult(stdout=stdout.decode(errors="replace") or None,
                          stderr=stderr.decode(errors="replace") or None, return_code=process.returncode)

    async def upload_file(self, source_path: Path | str, target_path: str):
        root, dest = self._host_path(target_path)
        _clear_links(dest, root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest)

    async def upload_dir(self, source_dir: Path | str, target_dir: str):
        root, dest = self._host_path(target_dir)
        for dirpath, dirnames, filenames in os.walk(source_dir):
            target = dest / Path(dirpath).relative_to(source_dir)
            _clear_links(target, root)
            target.mkdir(parents=True, exist_ok=True)
            for name in dirnames + filenames:
                source, copy = Path(dirpath, name), target / name
                if source.is_symlink() or name in filenames:
                    _clear_links(copy, root)
                if source.is_symlink():
                    os.symlink(os.readlink(source), copy)
                elif name in filenames:
                    shutil.copy2(source, copy)

    async def download_file(self, source_path: str, target_path: Path | str):
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._readable(source_path), target_path)

    async def download_dir(self, source_dir: str, target_dir: Path | str):
        shutil.copytree(self._readable(source_dir), target_dir, dirs_exist_ok=True, symlinks=True)


def _clear_links(path: Path, root: Path) -> None:
    """Remove every symlink from `root` down to `path`, so a host-side write lands in the sandbox
    rather than wherever a link the agent made points."""
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            current.unlink()


async def _kill(process: asyncio.subprocess.Process) -> None:
    """Kill bwrap's session; its PID namespace takes every sandboxed process with it."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await process.wait()
