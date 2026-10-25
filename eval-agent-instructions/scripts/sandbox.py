"""Bubblewrap sandboxes built from the host's /usr and a pinned agent toolchain, without Docker.

A sandbox sees the host's system files, the toolchain, and the directories the
caller binds; never the host's home, user config, or installed skills. It shares
the host network, so a proxy on the host or the LAN stays reachable. Commands
run as root inside a user namespace, which maps to the invoking user on the host.

The toolchain mirrors base.Dockerfile: nvm with Node 24 and the pinned agent
CLIs, plus ripgrep, which the host may lack. It is built once per version set.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "eval-agent-instructions"
# Per-sandbox writable directories live in memory: an adapter may write a key to /tmp.
SCRATCH = Path("/dev/shm/eval-agent-instructions")
# Ubuntu's default for root, as in the Docker image.
PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
# What a shell, git, curl and Node need from /etc; nothing user-specific.
ETC = ["passwd", "group", "hosts", "resolv.conf", "nsswitch.conf", "host.conf", "ssl", "ca-certificates",
       "ca-certificates.conf", "localtime", "alternatives", "ld.so.cache", "ld.so.conf", "ld.so.conf.d",
       "os-release", "lsb-release"]

RIPGREP = "14.1.1"
MARKER = "== versions"
TOOLCHAIN_SCRIPT = f"""set -eo pipefail
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | PROFILE=/dev/null bash
. "$NVM_DIR/nvm.sh"
nvm install 24 && nvm alias default 24
npm install -g "@anthropic-ai/claude-code@$CLAUDE_CODE_VERSION" "@openai/codex@$CODEX_VERSION" \\
  "openclaw@$OPENCLAW_VERSION"
for bin in node npm npx claude codex openclaw; do ln -sf "$(command -v $bin)" /opt/toolbin/$bin; done
curl -fsSL https://github.com/BurntSushi/ripgrep/releases/download/{RIPGREP}/ripgrep-{RIPGREP}-x86_64-unknown-linux-musl.tar.gz \\
  | tar -xz --no-same-owner -C /tmp
cp /tmp/ripgrep-{RIPGREP}-x86_64-unknown-linux-musl/rg /opt/toolbin/rg
export PATH=/opt/toolbin:$PATH
echo "{MARKER}"
node --version && claude --version && codex --version && openclaw --version && rg --version | head -1
"""


def sweep_scratch() -> None:
    """Remove scratch directories whose Harbor process is gone, as after a crash: they may hold a key."""
    for scratch in SCRATCH.glob("*/"):
        try:
            os.kill(int((scratch / "owner.pid").read_text()), 0)
        except (FileNotFoundError, ValueError, ProcessLookupError):
            shutil.rmtree(scratch, ignore_errors=True)
        except PermissionError:  # alive, under another user
            pass


def bwrap_args(binds: list[tuple[Path, str, bool]], cwd: str) -> list[str]:
    """bwrap arguments up to the command: system files, then each (host path, sandbox path, read-only) bind.

    Binds apply parents first, so a bind can sit inside another.
    """
    args = ["bwrap", "--unshare-user", "--uid", "0", "--gid", "0", "--unshare-pid", "--unshare-ipc",
            "--unshare-uts", "--unshare-cgroup-try", "--die-with-parent", "--new-session",
            "--ro-bind", "/usr", "/usr", "--tmpfs", "/usr/local",
            "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
            "--symlink", "usr/lib64", "/lib64", "--symlink", "usr/sbin", "/sbin",
            "--proc", "/proc", "--dev", "/dev"]
    for name in ETC:
        args += ["--ro-bind-try", f"/etc/{name}", f"/etc/{name}"]
    for source, target, read_only in sorted(binds, key=lambda b: len(Path(b[1]).parts)):
        args += ["--ro-bind" if read_only else "--bind", str(source), target]
    return args + ["--chdir", cwd]


def sandbox_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """The whole environment a sandboxed command gets. Passed to bwrap as its own environment,
    never as arguments, so keys stay out of process listings."""
    return {"PATH": PATH, "HOME": "/root", "NVM_DIR": "/root/.nvm", **(extra or {})}


def toolchain_binds(toolchain: Path) -> list[tuple[Path, str, bool]]:
    return [(toolchain / "nvm", "/root/.nvm", True), (toolchain / "bin", "/usr/local/bin", True)]


def toolchain(versions: dict[str, str]) -> Path:
    """The toolchain directory for these CLI versions, built when missing."""
    key = hashlib.sha256((TOOLCHAIN_SCRIPT + json.dumps(versions, sort_keys=True)).encode()).hexdigest()[:12]
    dest = CACHE / f"toolchain-{key}"
    if (dest / "versions.txt").is_file():
        return dest
    CACHE.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix=f"toolchain-{key}-", dir=CACHE))
    for sub in ("nvm", "bin", "home", "tmp"):
        (build / sub).mkdir()
    binds = [(build / "home", "/root", False), (build / "nvm", "/root/.nvm", False),
             (build / "bin", "/opt/toolbin", False), (build / "tmp", "/tmp", False)]
    env = sandbox_env({"CLAUDE_CODE_VERSION": versions["claude-code"], "CODEX_VERSION": versions["codex"],
                       "OPENCLAW_VERSION": versions["openclaw"]})
    result = subprocess.run(bwrap_args(binds, "/root") + ["bash", "-c", TOOLCHAIN_SCRIPT],
                            env=env, capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(build, ignore_errors=True)
        raise SystemExit(f"toolchain build failed:\n{result.stderr[-3000:]}")
    shutil.rmtree(build / "home")
    shutil.rmtree(build / "tmp")
    (build / "versions.txt").write_text(result.stdout.rsplit(MARKER + "\n", 1)[-1])
    try:
        build.rename(dest)
    except OSError:  # built concurrently by another run
        shutil.rmtree(build, ignore_errors=True)
    return dest


def environment_id(toolchain_dir: Path) -> str:
    """Names everything a sandboxed run depends on besides the task: the toolchain as built and the sandbox code.

    The installed versions count, not just the recipe: rebuilding the same recipe can pick up a newer Node 24.
    """
    h = hashlib.sha256((toolchain_dir / "versions.txt").read_bytes())
    for name in ("sandbox.py", "bwrap_env.py"):
        h.update((HERE / name).read_bytes())
    return f"eval-agent-instructions-bwrap:{h.hexdigest()[:12]}"
