"""Build Harbor task directories from eval cases: one task per case and variant.

A case directory holds `instruction.md`, `graders.json`, and the workspace
source: `scaffold.sh` (run in the empty workspace with `fixture/` beside it) or
just `fixture/` (copied into the workspace). Only the workspace source enters the
image; graders and expected files stay on the host.

Variants: `with` installs the skill under test plus its dependencies; `without`
installs only the dependencies, so the arms differ by the skill alone;
`minus-<rule>` installs a copy of the skill with that rule's text removed.
"""
import hashlib
import json
import shutil
from pathlib import Path

PROBE_CASE = "skill-probe"
PROBE_INSTRUCTION = (
    "List the skills available to you by name, one per line, then stop. "
    "Do not read, create, or change any files.\n"
)
PROBE_SPEC = {
    "expect_skill_loaded": {"with": False, "without": False},
    "probe": True,
    "graders": [{"name": "no-files-changed", "type": "unchanged_except", "allow": []}],
}

TASK_TOML = """schema_version = "1.1"

[task]
name = "skill-eval/{name}"
description = ""
authors = []
keywords = []

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = {agent_timeout}

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
mcp_servers = []
skills_dir = "/skills"
"""

# The case source is removed in the same layer that uses it, so the agent never sees it.
DOCKERFILE = """FROM {base_image}
COPY skills/ /skills/
COPY case/ /tmp/case/
WORKDIR /app
RUN if [ -f /tmp/case/scaffold.sh ]; then bash /tmp/case/scaffold.sh; \\
    elif [ -d /tmp/case/fixture ]; then cp -a /tmp/case/fixture/. /app/; fi \\
    && rm -rf /tmp/case
"""

# Snapshot the workspace for grading on the host. When the copy fails no reward
# file is written, so Harbor records a verifier error rather than a behavioral zero.
TEST_SH = """#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier/workspace
cp -a /app/. /logs/verifier/workspace/
echo '{"snapshot": 1}' > /logs/verifier/reward.json
"""

DEFAULT_AGENT_TIMEOUT_SEC = 900


def load_spec(case_dir: Path) -> dict:
    if case_dir.name == PROBE_CASE:
        return PROBE_SPEC
    return json.loads((case_dir / "graders.json").read_text())


def dependencies(evals_skill_dir: Path) -> list[str]:
    config = evals_skill_dir / "eval.json"
    return json.loads(config.read_text()).get("dependencies", []) if config.is_file() else []


def build_task(repo: Path, skill: str, case_dir: Path, variant: str, base_image: str, out: Path,
               skill_source: Path | None = None, preamble: str = "") -> str:
    """One task; `skill_source` replaces the repo's copy of the skill, as a minus variant does.

    `preamble` goes before the case's instruction.
    """
    name = f"{case_dir.name}--{variant}"
    task = out / name
    env = task / "environment"
    skills = env / "skills"
    skills.mkdir(parents=True)
    for dep in dependencies(repo / "evals" / skill):
        shutil.copytree(repo / dep, skills / dep, ignore=shutil.ignore_patterns("evals"))
    if variant != "without":
        shutil.copytree(skill_source or repo / skill, skills / skill, ignore=shutil.ignore_patterns("evals"))
    case_src = env / "case"
    case_src.mkdir()
    if (case_dir / "scaffold.sh").is_file():
        shutil.copy(case_dir / "scaffold.sh", case_src / "scaffold.sh")
    if (case_dir / "fixture").is_dir():
        shutil.copytree(case_dir / "fixture", case_src / "fixture")
    (env / "Dockerfile").write_text(DOCKERFILE.format(base_image=base_image))
    tests = task / "tests"
    tests.mkdir()
    (tests / "test.sh").write_text(TEST_SH)
    (tests / "test.sh").chmod(0o755)
    instruction = PROBE_INSTRUCTION if case_dir.name == PROBE_CASE else (case_dir / "instruction.md").read_text()
    (task / "instruction.md").write_text(preamble + instruction)
    timeout = load_spec(case_dir).get("agent_timeout_sec", DEFAULT_AGENT_TIMEOUT_SEC)
    (task / "task.toml").write_text(TASK_TOML.format(name=name, agent_timeout=float(timeout)))
    return name


def task_digest(task: Path) -> str:
    """Hash of everything the agent's run depends on inside a task: image, installed skills, workspace, instruction."""
    h = hashlib.sha256()
    for path in sorted(p for p in task.rglob("*") if p.is_file()):
        h.update(path.relative_to(task).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def build_tasks(repo: Path, skill: str, case_dirs: list[Path], variants: list[str],
                base_image: str, out: Path, sources: dict[str, Path] | None = None, preamble: str = "") -> list[str]:
    """Every case in every variant; `sources` maps a variant to the skill copy it installs."""
    out.mkdir(parents=True, exist_ok=True)
    return [build_task(repo, skill, case_dir, variant, base_image, out, (sources or {}).get(variant), preamble)
            for case_dir in case_dirs for variant in variants]
