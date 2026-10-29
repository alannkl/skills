"""Build Harbor task directories from eval cases: one task per case and variant, and for an
instruction file, per workspace name the run's setups read.

A suite is `evals/<suite>/`. Its `eval.json` names the artifact under test and
the skills both arms install:

    {"artifact": {"type": "skill", "path": "<skill folder>"}
              | {"type": "instruction-file", "path": "<file>", "as": "AGENTS.md"}
              | {"type": "prompt", "path": "<file>", "role": "system" | "user", "runner": "harness" | "api"},
     "dependencies": ["<skill folder>", ...],
     "setups": {"run": [<preset name or setup spec>, ...], "full": [...]}}

`setups` names the setups the artifact must support, replacing the defaults in
configs.json: `run` for a plain run, `full` for --full and --minus.

Without an artifact entry, the suite tests the skill in the folder of its own name.
A skill is installed where each harness finds skills; an instruction file is
placed in the workspace under its `as` name, else the name the setup's harness
reads, without a leading YAML frontmatter block, and below the harness's own starter
text when the harness seeds that file. A system prompt is written to the
task's `prompt/system.md` for the runner to pass on; a user prompt goes before
the case's instruction. A prompt's `{{name}}` placeholders are filled from the
case's `vars.json`.

A case directory holds `instruction.md`, `graders.json`, and the workspace
source: `scaffold.sh` (run in the empty workspace with `fixture/` beside it) or
just `fixture/` (copied into the workspace). Only the workspace source enters the
image; graders and expected files stay on the host.

Variants: `with` delivers the artifact plus the dependencies; `without` only the
dependencies, so the arms differ by the artifact alone; `minus-<rule>` delivers a
copy of the artifact with that rule's text removed. A pinned build tells the agent
in the `with` and minus arms to use the skill by path, so a run measures the
skill's text rather than whether its description triggers.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

from graders import spec_problems

PROBE_CASE = "probe"
PROBE_INSTRUCTION = {
    "skill": "List the skills available to you by name, one per line, then stop. "
             "Do not read, create, or change any files.\n",
    "instruction-file": "Without reading, creating, or changing any files, say whether your context holds "
                        "project instructions from a file such as AGENTS.md or CLAUDE.md. If it does, quote "
                        "their first line and every top-level heading exactly; otherwise say there are none. "
                        "End with a line `TRUNCATED: yes` if your context says any of those files was truncated "
                        "or shortened, otherwise `TRUNCATED: no`.\n",
    "prompt": "Without reading, creating, or changing any files, say whether your instructions include text "
              "added by whoever set you up, beyond your defaults. If they do, quote its first line exactly; "
              "otherwise say there is none.\n",
}
# Names the installed copy by path: a harness may ship a built-in skill with the same name.
USE_SKILL = "Use the skill at /skills/{skill}/SKILL.md for this task.\n\n"
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

[environment]{docker_image}
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
mcp_servers = []
skills_dir = "/skills"
"""

# Builds the workspace in /app from the case source at /tmp/case. The source is
# removed in the same step that uses it, so the agent never sees it.
WORKSPACE_SETUP = ("if [ -f /tmp/case/scaffold.sh ]; then bash /tmp/case/scaffold.sh; \\\n"
                   "    elif [ -d /tmp/case/fixture ]; then cp -a /tmp/case/fixture/. /app/; fi \\\n"
                   "    && rm -rf /tmp/case")
DOCKERFILE = """FROM {base_image}
COPY skills/ /skills/
COPY case/ /tmp/case/
WORKDIR /app
RUN """ + WORKSPACE_SETUP.replace("{", "{{").replace("}", "}}") + "\n"
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
    spec = json.loads((case_dir / "graders.json").read_text())
    problems = spec_problems(spec["graders"])
    if problems:
        raise SystemExit(f"{case_dir.name}/graders.json: " + "; ".join(problems))
    return spec


def load_suite(repo: Path, name: str) -> dict:
    """The suite's artifact, with `name` (a skill's folder name) filled in."""
    path = repo / "evals" / name / "eval.json"
    config = json.loads(path.read_text()) if path.is_file() else {}
    artifact = dict(config.get("artifact") or {"type": "skill", "path": name})
    if artifact["type"] == "skill":
        artifact.setdefault("name", Path(artifact["path"]).name)
    elif artifact["type"] == "prompt":
        artifact.setdefault("role", "system")
        artifact.setdefault("runner", "harness")
        if artifact["role"] not in ("system", "user") or artifact["runner"] not in ("harness", "api"):
            raise SystemExit(f"{path}: a prompt's role is system or user, and its runner harness or api")
    elif artifact["type"] != "instruction-file":
        raise SystemExit(f"{path}: artifact type must be skill, instruction-file or prompt")
    setups = config.get("setups", {})
    if set(setups) - {"run", "full"}:
        raise SystemExit(f"{path}: setups takes run and full")
    return {"name": name, "artifact": artifact, "dependencies": config.get("dependencies", []), "setups": setups}


def workspace_name(artifact: dict, harness_file: str) -> str:
    """The name an instruction file takes in the workspace: its `as`, else the file the harness reads."""
    return artifact.get("as") or harness_file


# A YAML frontmatter block: a `---` line first, through the next `---` line.
FRONTMATTER = re.compile(r"---[ \t]*\r?\n.*?^---[ \t]*(\r?\n|\Z)", re.S | re.M)


def without_frontmatter(text: str) -> str:
    """An instruction file's text as delivered: a leading frontmatter block and the blank lines after it dropped."""
    found = FRONTMATTER.match(text)
    return text[found.end():].lstrip("\r\n") if found else text


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
               source: Path | None = None, pin: bool = False, instruction_file: str | None = None,
               template: str | None = None, prebuilt: bool = False) -> str:
    """One task; `source` replaces the repo's copy of the artifact, as a minus variant does.

    `pin` names a skill artifact in the instruction of every arm that installs it;
    `instruction_file` is the workspace name an instruction-file artifact takes, and `template` the
    harness's own starter text it goes under. With `prebuilt`, task.toml names the image
    `environment_image` gives the environment, for the caller to build before Harbor runs.
    """
    artifact = suite["artifact"]
    probe = case_dir.name == PROBE_CASE
    preamble = USE_SKILL.format(skill=artifact["name"]) if (
        pin and not probe and variant != "without" and artifact["type"] == "skill") else ""
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
        if (case_dir / "fixture" / instruction_file).exists():
            raise SystemExit(f"{case_dir}: the fixture already has {instruction_file}, which the artifact replaces")
        (env / "instructions").mkdir()
        text = without_frontmatter((source or repo / artifact["path"]).read_bytes().decode())
        if template:
            text = template.rstrip("\n") + "\n\n" + text
        (env / "instructions" / instruction_file).write_bytes(text.encode())
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
    if probe and artifact["type"] == "prompt" and (artifact["role"] == "user" or artifact["runner"] == "api"):
        raise SystemExit("a user prompt or an API call passes the text straight into the request, so it has no "
                         "probe; check its effect with a case")
    instruction = PROBE_INSTRUCTION[artifact["type"]] if probe else (case_dir / "instruction.md").read_text()
    (task / "instruction.md").write_text(preamble + instruction)
    timeout = load_spec(case_dir).get("agent_timeout_sec", DEFAULT_AGENT_TIMEOUT_SEC)
    image = f'\ndocker_image = "{environment_image(env)}"' if prebuilt else ""
    (task / "task.toml").write_text(TASK_TOML.format(name=name, agent_timeout=float(timeout), docker_image=image))
    return name


def environment_image(env: Path) -> str:
    """Docker tag for a task's environment folder, named by its content. Harbor names the image it
    builds after the task, which is the same in every setup, so setups that run at once and deliver
    different files, such as CLAUDE.md and AGENTS.md, would overwrite each other's image."""
    h = hashlib.sha256()
    for path in sorted(p for p in env.rglob("*") if p.is_file()):
        h.update(path.relative_to(env).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return f"eval-agent-instructions-task:{h.hexdigest()[:16]}"


def task_digest(task: Path) -> str:
    """Hash of everything the agent's run depends on inside a task: image, installed skills, workspace, instruction."""
    h = hashlib.sha256()
    for path in sorted(p for p in task.rglob("*") if p.is_file()):
        h.update(path.relative_to(task).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def build_tasks(repo: Path, suite: dict, case_dirs: list[Path], variants: list[str],
                base_image: str, out: Path, sources: dict[str, Path] | None = None, pin: bool = False,
                instruction_file: str | None = None, template: str | None = None,
                prebuilt: bool = False) -> list[str]:
    """Every case in every variant; `sources` maps a variant to the artifact copy it delivers."""
    out.mkdir(parents=True, exist_ok=True)
    return [build_task(repo, suite, case_dir, variant, base_image, out, (sources or {}).get(variant), pin,
                       instruction_file, template, prebuilt)
            for case_dir in case_dirs for variant in variants]
