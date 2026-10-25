"""Harbor agent overrides, loaded by Harbor through `--agent harbor_agents:<Class>`.

This module imports Harbor, so it runs only inside Harbor's environment. It uses
Harbor internals (`_nvm24`, `self._version`); recheck them when the pinned Harbor
commit in configs.json changes.
"""
import re

from harbor.agents.installed.codex import Codex
from harbor.agents.installed.openclaw import OpenClaw, _nvm24
from harbor.environments.base import BaseEnvironment

# OpenClaw keeps sessions in a database and reports a session key, so the upstream
# adapter's transcript copy finds nothing. Export the trajectory bundle instead,
# outside the task workspace so the export is not among the graded files.
_EXPORT_TRAJECTORY = (
    "rm -rf /tmp/oc-export && mkdir -p /tmp/oc-export && "
    "openclaw sessions export-trajectory --session-key agent:main:main "
    "--workspace /tmp/oc-export --output trial --json "
    "> /logs/agent/openclaw.export.json 2>/logs/agent/openclaw.export.err; "
    "cp -r /tmp/oc-export/.openclaw/trajectory-exports/trial /logs/agent/openclaw-trajectory 2>/dev/null; "
    "true"
)


class PreinstalledOpenClaw(OpenClaw):
    """OpenClaw that uses the base image's pinned install and exports its trajectory.

    Upstream reinstalls nvm, Node and openclaw on every trial, which exceeds the
    setup timeout on a local Docker engine.
    """

    async def install(self, environment: BaseEnvironment) -> None:
        result = await environment.exec(command=_nvm24("openclaw --version"))
        if result.return_code == 0 and self._version and self._version in (result.stdout or ""):
            return
        await super().install(environment)

    async def run(self, instruction, environment, context) -> None:
        try:
            await super().run(instruction, environment, context)
        finally:
            await self.exec_as_agent(environment, command=_nvm24(_EXPORT_TRAJECTORY))


class PreinstalledCodex(Codex):
    """Codex that finds the base image's pinned install.

    In Docker, `codex --version` first warns on stderr, which Harbor's exec merges
    into stdout; upstream reads the first line as the version, finds a mismatch, and
    reinstalls nvm, Node and Codex on every trial.
    """

    def parse_version(self, stdout: str) -> str:
        found = re.search(r"^codex-cli (\S+)", stdout, re.M)
        return found.group(1) if found else super().parse_version(stdout)
