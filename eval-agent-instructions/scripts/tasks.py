"""Build Harbor task directories from eval cases: one task per case and variant.

A suite is `evals/<suite>/`. Its `eval.json` names the artifact under test and
the skills both arms install:

    {"artifact": {"type": "skill", "path": "<skill folder>"}
              | {"type": "instruction-file", "path": "<file>", "as": "AGENTS.md"}
              | {"type": "prompt", "path": "<file>", "role": "system" | "user", "runner": "harness" | "api"},
     "dependencies": ["<skill folder>", ...]}

Without an artifact entry, the suite tests the skill in the folder of its own name.
A skill is installed where each harness finds skills; an instruction file is
placed in the workspace under its `as` name. A system prompt is written to the
task's `prompt/system.md` for the runner to pass on; a user prompt goes before
the case's instruction. A prompt's `{{name}}` placeholders are filled from the
case's `vars.json`.

A case directory holds `instruction.md`, `graders.json`, and the workspace
source: `scaffold.sh` (run in the empty workspace with `fixture/` beside it) or
just `fixture/` (copied into the workspace). Only the workspace source enters the
image; graders and expected files stay on the host.

Variants: `with` delivers the artifact plus the dependencies; `without` only the
dependencies, so the arms differ by the artifact alone; `minus-<rule>` delivers a
copy of the artifact with that rule's text removed.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

PROBE_CASE = "probe"
PROBE_INSTRUCTION = {
    "skill": "List the skills available to you by name, one per line, then stop. "
             "Do not read, create, or change any files.\n",
    "instruction-file": "Without reading, creating, or changing any files, say whether your context holds "
                        "project instructions from a file such as AGENTS.md or CLAUDE.md. If it does, quote "
                        "their first line exactly; otherwise say there are none.\n",
    "prompt": "Without reading, creating, or changing any files, say whether your instructions include text "
              "added by whoever set you up, beyond your defaults. If they do, quote its first line exactly; "
              "otherwise say there is none.\n",
}
PROBE_SPEC = {
    "expect_skill_loaded": {"with": False, "without": False},
    "probe": True,
    "graders": [{"name": "no-files-changed", "type": "unchanged_except", "allow": []}],
}

TASK_TOML = """schema_version = "1.1"

[task]
name = "eval-agent-instructions/{name}"
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
# A delivered instruction file lands in the workspace after the case's own files.
INSTRUCTIONS_LAYER = "COPY instructions/ /app/\n"

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
    if case_dir.name in (PROBE_CASE, "skill-probe"):
        return PROBE_SPEC
    return json.loads((case_dir / "graders.json").read_text())


def load_suite(repo: Path, name: str) -> dict:
    """The suite's artifact, with `name` (a skill's folder name) or `as` (a file's workspace name) filled in."""
    path = repo / "evals" / name / "eval.json"
    config = json.loads(path.read_text()) if path.is_file() else {}
    artifact = dict(config.get("artifact") or {"type": "skill", "path": name})
    if artifact["type"] == "skill":
        artifact.setdefault("name", Path(artifact["path"]).name)
    elif artifact["type"] == "instruction-file":
        artifact.setdefault("as", Path(artifact["path"]).name)
    elif artifact["type"] == "prompt":
        artifact.setdefault("role", "system")
        artifact.setdefault("runner", "harness")
        if artifact["role"] not in ("system", "user") or artifact["runner"] not in ("harness", "api"):
            raise SystemExit(f"{path}: a prompt's role is system or user, and its runner harness or api")
    else:
        raise SystemExit(f"{path}: artifact type must be skill, instruction-file or prompt")
    return {"name": name, "artifact": artifact, "dependencies": config.get("dependencies", [])}


def artifact_root(repo: Path, artifact: dict) -> Path:
    """The folder that rules.json paths are relative to: the skill folder, or the file's folder."""
    path = repo / artifact["path"]
    return path if artifact["type"] == "skill" else path.parent


def render(text: str, case_dir: Path) -> str:
    """Fill `{{name}}` placeholders from the case's vars.json; a placeholder left unfilled stops the build.

    The probe has no case, so it sees the placeholders as written.
    """
    if case_dir.name == PROBE_CASE:
        return text
    path = case_dir / "vars.json"
    values = json.loads(path.read_text()) if path.is_file() else {}
    rendered = re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: str(values.get(m.group(1), m.group(0))), text)
    unfilled = sorted(set(re.findall(r"\{\{\s*(\w+)\s*\}\}", rendered)))
    if unfilled:
        raise SystemExit(f"{case_dir}: vars.json has no value for {unfilled}")
    return rendered


def build_task(repo: Path, suite: dict, case_dir: Path, variant: str, base_image: str, out: Path,
               source: Path | None = None, preamble: str = "") -> str:
    """One task; `source` replaces the repo's copy of the artifact, as a minus variant does.

    `preamble` goes before the case's instruction.
    """
    artifact = suite["artifact"]
    name = f"{case_dir.name}--{variant}"
    task = out / name
    env = task / "environment"
    skills = env / "skills"
    skills.mkdir(parents=True)
    for dep in suite["dependencies"]:
        shutil.copytree(repo / dep, skills / Path(dep).name, ignore=shutil.ignore_patterns("evals"))
    dockerfile = DOCKERFILE.format(base_image=base_image)
    if variant != "without" and artifact["type"] == "skill":
        shutil.copytree(source or repo / artifact["path"], skills / artifact["name"],
                        ignore=shutil.ignore_patterns("evals"))
    elif variant != "without" and artifact["type"] == "prompt":
        prompt = render((source or repo / artifact["path"]).read_text(), case_dir)
        if artifact["role"] == "system":
            (task / "prompt").mkdir(parents=True)
            (task / "prompt" / "system.md").write_text(prompt)
        else:
            preamble = prompt.rstrip("\n") + "\n\n" + preamble
    elif variant != "without":
        if (case_dir / "fixture" / artifact["as"]).exists():
            raise SystemExit(f"{case_dir}: the fixture already has {artifact['as']}, which the artifact replaces")
        (env / "instructions").mkdir()
        shutil.copy(source or repo / artifact["path"], env / "instructions" / artifact["as"])
        dockerfile += INSTRUCTIONS_LAYER
    case_src = env / "case"
    case_src.mkdir()
    if (case_dir / "scaffold.sh").is_file():
        shutil.copy(case_dir / "scaffold.sh", case_src / "scaffold.sh")
    if (case_dir / "fixture").is_dir():
        shutil.copytree(case_dir / "fixture", case_src / "fixture")
    (env / "Dockerfile").write_text(dockerfile)
    tests = task / "tests"
    tests.mkdir()
    (tests / "test.sh").write_text(TEST_SH)
    (tests / "test.sh").chmod(0o755)
    probe = case_dir.name == PROBE_CASE
    if probe and artifact["type"] == "prompt" and (artifact["role"] == "user" or artifact["runner"] == "api"):
        raise SystemExit("a user prompt or an API call passes the text straight into the request, so it has no "
                         "probe; check its effect with a case")
    instruction = PROBE_INSTRUCTION[artifact["type"]] if probe else (case_dir / "instruction.md").read_text()
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


def build_tasks(repo: Path, suite: dict, case_dirs: list[Path], variants: list[str],
                base_image: str, out: Path, sources: dict[str, Path] | None = None, preamble: str = "") -> list[str]:
    """Every case in every variant; `sources` maps a variant to the artifact copy it delivers."""
    out.mkdir(parents=True, exist_ok=True)
    return [build_task(repo, suite, case_dir, variant, base_image, out, (sources or {}).get(variant), preamble)
            for case_dir in case_dirs for variant in variants]
