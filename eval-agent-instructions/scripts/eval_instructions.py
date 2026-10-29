#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tiktoken"]
# ///
"""Evaluate agent instructions with and without them across agent harnesses and models, through Harbor.

Run from the root of the repository that holds the artifact and its `evals/<suite>/`.

  eval_instructions.py run <suite> [--config NAME... | --full] [--harness H --model M [--effort E] [--provider P]]
                           [--case NAME]... [--rule RULE]... [--all-cases] [--attempts N] [--probe] [--fresh]
                           [--env bwrap|docker] [--concurrency N] [--concurrency CONFIG=N]...
  eval_instructions.py run <suite> --minus RULE [--config NAME]... [--harness H --model M ...]
  eval_instructions.py run <suite> --trigger [--config NAME... | --full] [--case NAME]...
  eval_instructions.py run <suite> --artifact DRAFT --variants with [--rule RULE]... [--full]
  eval_instructions.py grade <run-dir>... [--judge MODEL]...
  eval_instructions.py report <run-dir>
  eval_instructions.py compare --baseline <run-dir>... --candidate <run-dir>... [--pairwise JUDGE]
  eval_instructions.py rules <suite> [--all-versions | --min-set [--gaps]]

`run` builds one Harbor task per case and variant, runs each configuration as a
Harbor job, then grades and reports. An instruction file, less any leading YAML
frontmatter block, goes in the workspace under its `as` name from eval.json, else
the name each setup's harness reads (`instruction_file` in configs.json); a run
builds its tasks once per such name. `run` also records the tokens of each text
the with arm loads, per setup, which the report lists; models other than
Anthropic's get an estimate. A skill under test is named by path in the
instruction of every arm that installs it, so the run measures its text; cases
marked `trigger_only` are left out, and so are those marked `integration` or `reserve` unless
--all-cases is set. `--rule` runs only the cases whose graders test the named rules,
as an edit round does. Every arm reuses earlier graded trials when
its task directory, configuration, Harbor version and agent arguments all match,
so only what changed, and the attempts earlier runs lack, run. Results go to evals/<suite>/results/<run-id>/. Grading reads only saved artifacts and
the run's own copy of its cases, so `grade` reruns with other judges, or with
the repo's current graders through --graders-from-repo, without rerunning any agent.

`--minus RULE` runs the full artifact against a copy lacking that rule's text
from evals/<suite>/rules.json, three times each by default, on the cases whose
graders test the rule and on the --full setups unless --config names others; for a skill, both arms are told to use it. `rules` checks
the map and tabulates each rule's grader results over every run of the current
artifact text.

`--trigger` checks a skill's description instead: the with arm only, the skill
left to trigger on its own, on every case including `trigger_only` ones, and the
report counts how often should-trigger cases (`expect_skill_loaded.with` true)
and near-misses loaded it.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
REPO = Path.cwd()
sys.path.insert(0, str(HERE))

from compare import acceptance_graders, compare, describe_work, work  # noqa: E402
from evidence import EXTRACTORS  # noqa: E402
from graders import judge_pending, run_graders, temporary_initial_workspace  # noqa: E402
from rules import (EARLIER, MINUS, arm, artifact_digest, check_rules, guard_refs, load_rules, min_set,  # noqa: E402
                   minus_artifact, rule_cases, tabulate)
from tasks import (PROBE_CASE, USE_SKILL, artifact_root, build_tasks, load_spec, load_suite, task_digest,  # noqa: E402
                   without_frontmatter, workspace_name)
from token_counts import loaded_texts, loaded_tokens  # noqa: E402
from api_runner import run_api_job  # noqa: E402
import sandbox  # noqa: E402
import setups  # noqa: E402

SETTINGS = json.loads((HERE / "configs.json").read_text())
SETTINGS["configs"] = setups.catalog(SETTINGS)
# bubblewrap sandboxes start faster and cost less memory than containers; Docker covers hosts without it.
DEFAULT_ENV = "bwrap" if sys.platform == "linux" and shutil.which("bwrap") else "docker"
# Sessions at once: under bwrap at most 32 across all setups, fewer when the host's memory cannot hold
# them, each session counted at its harness's SESSION_GB; under Docker per setup, the setups running one
# at a time, each container capped at 2 GB. A harness's `max_sessions` in configs.json caps each of its setups.
DEFAULT_SLOTS = {"bwrap": 32, "docker": 6}
# Memory a session holds midway through a run, in GB. OpenClaw's Node heap grows over a session, from
# about 0.3 GB to 1-1.9 GB; Claude Code and Codex sessions stayed near 0.3 GB.
SESSION_GB = {"openclaw": 1.0, "claude-code": 0.3, "codex": 0.3, "api": 0.0}
# Kept free for the host, so sessions never push it into swap.
RESERVE_GB = 2.0
# Each harness ships skills of its own, such as Claude Code's code-review and the
# skill-creator in Codex and OpenClaw. They compete with the skill under test and
# can share its name, so they are off unless a configuration sets builtin_skills;
# OpenClaw's switch lives in openclaw_model_config. Claude Code also needs an
# environment variable; doctor and plugin-authoring survive it, so they are turned off by name.
BLOCK_BUILTIN_SKILLS = {
    "claude-code": {"skillOverrides": {"doctor": "off", "plugin-authoring": "off"}},
    "codex": {"skills": {"bundled": {"enabled": False}}},
}
HARBOR_AGENT = {"claude-code": "claude-code", "codex": "harbor_agents:PreinstalledCodex",
                "openclaw": "harbor_agents:PreinstalledOpenClaw"}
API = "api"


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines into the environment without overriding variables already set."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value.strip().strip('"').strip("'"))


def task_environment(kind: str) -> tuple[str, list[str], str]:
    """(image name for the task Dockerfiles, Harbor environment arguments, description) for `kind`.

    The image name lands in every task's Dockerfile, so it keys baseline reuse:
    trials from another environment or toolchain never stand in for this one's.
    """
    if kind == "docker":
        image = base_image()
        return image, [], image
    sandbox.sweep_scratch()
    toolchain = sandbox.toolchain(SETTINGS["cli_versions"])
    image = sandbox.environment_id(toolchain)
    versions = ", ".join((toolchain / "versions.txt").read_text().split())
    return image, ["--env", "bwrap_env:BwrapEnvironment", "--ek", f"toolchain={toolchain}"], f"{image} ({versions})"


def base_image() -> str:
    """Tag of the base image for the pinned CLI versions; built when missing."""
    versions = SETTINGS["cli_versions"]
    digest = hashlib.sha256(((HERE / "base.Dockerfile").read_text() + json.dumps(versions, sort_keys=True))
                            .encode()).hexdigest()[:12]
    tag = f"eval-agent-instructions-base:{digest}"
    if subprocess.run(["docker", "image", "inspect", tag], capture_output=True).returncode != 0:
        wait_for_docker()
        subprocess.run(["docker", "build", "-t", tag, "-f", str(HERE / "base.Dockerfile"),
                        "--build-arg", f"CLAUDE_CODE_VERSION={versions['claude-code']}",
                        "--build-arg", f"CODEX_VERSION={versions['codex']}",
                        "--build-arg", f"OPENCLAW_VERSION={versions['openclaw']}", str(HERE)], check=True)
    return tag


def wait_for_docker(timeout_sec: int = 300) -> None:
    """Harbor gives up when `docker info` takes over 10 s, which Docker Desktop does under load."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            if subprocess.run(["docker", "info"], capture_output=True, timeout=10).returncode == 0:
                return
        except subprocess.TimeoutExpired:
            pass
        time.sleep(5)
    raise SystemExit("Docker is not responding")


def openclaw_model_config(config: dict) -> str:
    """OpenClaw config overlay with an explicit entry for the configured model.

    An explicit entry replaces the catalog's, so it restates reasoning support;
    without it OpenClaw rejects --thinking. Harbor adds the provider's base URL
    and key from <PROVIDER>_BASE_URL and <PROVIDER>_API_KEY.

    For OpenRouter it also limits the upstream providers to the configured ones, tried in order, and
    declares the one supported effort so OpenClaw sends it as `reasoning.effort`
    verbatim. Without that, the levels stop at high plus OpenClaw's own `ultra`
    (sent as max), there is no xhigh, and some models get medium sent as low.
    """
    provider, model_id = config["model"].split("/", 1)
    # OpenClaw's default output cap of 8192 tokens can go entirely to reasoning, ending the turn with nothing done.
    entry = {"id": model_id, "name": model_id, "reasoning": True, "contextWindow": config["context_window"],
             "maxTokens": config.get("max_tokens", 64000)}
    if provider == "openrouter":
        effort = config["effort"]
        entry["compat"] = {"supportsReasoningEffort": True, "supportedReasoningEfforts": [effort]} if effort else \
            {"supportsReasoningEffort": False}
        if config.get("openrouter_providers"):
            entry["params"] = {"provider": {"order": config["openrouter_providers"], "allow_fallbacks": False}}
        native = {"models": [entry]}
    else:
        native = {"api": "anthropic-messages", "models": [entry]}
    overlay = {"models": {"providers": {provider: native}}}
    if not config.get("builtin_skills"):
        # An empty allowlist means every bundled skill, so name one that does not exist.
        # The two plugin skills are not bundled and need their own switch.
        overlay["skills"] = {"allowBundled": ["none"],
                             "entries": {name: {"enabled": False} for name in ("browser-automation", "canvas")}}
    # The harness's own settings, such as the raised cap on injected AGENTS.md, share no top-level key with the overlay.
    return json.dumps(config.get("native_config", {}) | overlay)


def agent_args(config: dict, system_prompt: str | None = None) -> list[str]:
    """Arguments that decide how the agent runs, as opposed to where results go.

    `system_prompt` is appended to Claude Code's system prompt, or becomes Codex's
    developer instructions; OpenClaw has no such setting.
    """
    harness = config["harness"]
    if harness == API:
        args = [API, config["model"], f"effort={config.get('effort')}",
                f"provider={','.join(config.get('openrouter_providers') or ['None'])}"]
        return args + [f"max_tokens={config['max_tokens']}"] if "max_tokens" in config else args
    args = ["-a", HARBOR_AGENT[harness], "-m", config["model"],
            "--ak", f"version={SETTINGS['cli_versions'][harness]}",
            # The OpenClaw adapter reads its config from a bind-mounted /logs/agent.
            "--ek", "auto_mounting=true"]
    if config.get("effort"):
        args += ["--ak", f"reasoning_effort={config['effort']}"]
    if harness == "openclaw":
        if system_prompt is not None:
            raise SystemExit("OpenClaw has no system prompt setting; evaluate the text as an AGENTS.md instead")
        setup = ["--ak", f"workspace_setup={config['workspace_setup']}"] if config.get("workspace_setup") else []
        return args + ["--ak", f"openclaw_config={openclaw_model_config(config)}"] + setup
    native = {} if config.get("builtin_skills") else dict(BLOCK_BUILTIN_SKILLS[harness])
    # Codex otherwise streams over a websocket and sends requests the proxy rejects mid-run
    # (`response.interrupt`), failing the session; Harbor fills the provider's base_url.
    native |= config.get("native_config", {})
    if harness == "claude-code" and not config.get("builtin_skills"):
        args += ["--ae", "CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1"]
    if system_prompt is not None and harness == "claude-code":
        args += ["--ak", f"append_system_prompt={system_prompt}"]
    elif system_prompt is not None:
        native["developer_instructions"] = system_prompt
    if native:
        args += ["--ak", f"config={json.dumps(native)}"]
    return args


def harbor_command(config: dict, tasks_dir: Path, jobs_dir: Path, job: str, attempts: int, concurrency: int,
                   exclude: list[str] = (), include: list[str] = (), system_prompt: str | None = None,
                   environment: list[str] = ()) -> list[str]:
    cmd = ["uv", "tool", "run", "--python", "3.12", "--from", f"harbor @ {SETTINGS['harbor']}", "harbor", "run",
           "-p", str(tasks_dir), *agent_args(config, system_prompt), *environment,
           "-k", str(attempts), "-n", str(concurrency), "-o", str(jobs_dir), "--job-name", job, "-y", "-q"]
    for task in include:
        cmd += ["-i", task, "-i", f"*/{task}"]
    for task in exclude:
        cmd += ["-x", task, "-x", f"*/{task}"]
    return cmd


def job_plan(tasks_dir: Path, tasks: list[str], skip: list[str], artifact: dict) -> list[tuple[str, list[str], str | None]]:
    """(job name, tasks, system prompt) per Harbor job for one setup.

    A system prompt is an agent argument, which Harbor sets per job, so each task
    that delivers one runs as its own job; everything else shares one job.
    """
    pending = [t for t in tasks if t not in skip]
    if artifact["type"] != "prompt" or artifact["role"] != "system":
        return [("main", pending, None)] if pending else []
    plain = [t for t in pending if not (tasks_dir / t / "prompt" / "system.md").is_file()]
    plan = [("main", plain, None)] if plain else []
    return plan + [(t, [t], (tasks_dir / t / "prompt" / "system.md").read_text())
                   for t in pending if t not in plain]


def trial_dirs(job_root: Path) -> list[Path]:
    """Trial folders under a setup's jobs, one or two levels down: those whose config.json names a task."""
    found = []
    for path in sorted(job_root.glob("*/config.json")) + sorted(job_root.glob("*/*/config.json")):
        try:
            if "task" in json.loads(path.read_text()):
                found.append(path.parent)
        except json.JSONDecodeError:
            continue
    return found


def new_run_dir(results: Path, run_id: str | None) -> Path:
    """Create the run's folder; a default id that a run started in the same second already took gets a suffix."""
    base = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for n in range(1 if run_id else 100):
        run_dir = results / (base if n == 0 else f"{base}-{n}")
        try:
            run_dir.mkdir(parents=True)
            return run_dir
        except FileExistsError:
            continue
    raise SystemExit(f"{results / base} exists")


def stored_baseline(results: Path, run_id: str, config: dict, task: str, digest: str, attempts: int) -> list[Path]:
    """Up to `attempts` graded trials of the same task from earlier runs, newest first.

    A trial matches when its task directory hashes the same and it ran under the same
    configuration, Harbor version and agent arguments; the run tops up the attempts it lacks.
    """
    case, variant = task.split("--")
    metas = [(p.parent, json.loads(p.read_text())) for p in results.glob("*/run.json") if p.parent.name != run_id]
    found = []
    for prior, meta in sorted(metas, key=lambda m: m[1].get("started_at", ""), reverse=True):
        grades = prior / "grades.jsonl"
        if meta.get("harbor") != SETTINGS["harbor"] or not grades.is_file():
            continue
        task_dirs = {name: prior / meta.get("task_dirs", {}).get(name, "tasks") / task for name in meta["configs"]}
        names = {name for name, c in meta["configs"].items()
                 if c == config and meta.get("agent_args", {}).get(name) == agent_args(config)
                 and task_dirs[name].is_dir() and task_digest(task_dirs[name]) == digest}
        for line in grades.read_text().splitlines():
            row = json.loads(line)
            # A reused row points at an older run's trial, which this loop reaches on its own.
            if (row["config"] in names and (row["case"], row["variant"]) == (case, variant)
                    and row["status"] == "ok" and not row.get("reused_from")):
                found.append(prior / row.get("trial_path", f"jobs/{row['config']}/{row['trial']}"))
    return found[:attempts]


def reuse_baselines(run_dir: Path, configs: list[str], tasks: list[str], attempts: int,
                    task_dirs: dict[str, str]) -> dict:
    """Copy matching earlier trials of every task into run_dir/reused/<config>/; `task_dirs` names each
    setup's task folder in the run.

    Returns {config: {task: [source]}}.
    """
    results = run_dir.parent
    digests = {(folder, task): task_digest(run_dir / folder / task)
               for folder in set(task_dirs.values()) for task in tasks}
    reused = {}
    for name in configs:
        for task in tasks:
            digest = digests[(task_dirs[name], task)]
            trials = stored_baseline(results, run_dir.name, SETTINGS["configs"][name], task, digest, attempts)
            for trial in trials:
                shutil.copytree(trial, run_dir / "reused" / name / trial.name)
            if trials:
                reused.setdefault(name, {})[task] = [str(t.relative_to(results)) for t in trials]
    return reused


def case_dirs(suite: str, names: list[str] | None, probe: bool, trigger: bool = False,
              integration: bool = True) -> list[Path]:
    """The named cases, or all of them; the probe joins when --probe is set or named as a case.

    `trigger_only` cases test a description, so only a trigger check runs them; `integration`
    cases, the long ones kept for breadth, and `reserve` cases, whose coverage the regular set
    already has, run only when `integration` is set.
    """
    root = REPO / "evals" / suite
    found = sorted(p for p in root.iterdir() if (p / "graders.json").is_file())
    if not trigger:
        found = [p for p in found if not load_spec(p).get("trigger_only")]
    if names:
        probe = probe or PROBE_CASE in names
        names = [n for n in names if n != PROBE_CASE]
        missing = set(names) - {p.name for p in found}
        if missing:
            raise SystemExit(f"unknown cases{'' if trigger else ' outside --trigger'}: {sorted(missing)}")
        found = [p for p in found if p.name in names]
    if not integration:
        found = [p for p in found if not (load_spec(p).get("integration") or load_spec(p).get("reserve"))]
    return found + ([root / PROBE_CASE] if probe else [])


def archive_cases(suite: str, cases: list[Path], dest: Path) -> None:
    """Keep the run's own copy of each case, so regrading uses the fixtures the agents saw."""
    dest.mkdir(parents=True)
    for case in cases:
        if case.is_dir():
            shutil.copytree(case, dest / case.name, ignore=shutil.ignore_patterns("results"))
    eval_config = REPO / "evals" / suite / "eval.json"
    if eval_config.is_file():
        shutil.copy(eval_config, dest / "eval.json")


def check_credentials(configs: list[str]) -> None:
    """Stop before any paid run when a configuration's credentials are not set."""
    missing = {"ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN"} - set(os.environ)  # judges use them too
    for name in configs:
        config = SETTINGS["configs"][name]
        missing |= {v for value in config.get("env", {}).values()
                    for v in re.findall(r"\$\{(\w+)\}", value) if v not in os.environ}
        if config["model"].startswith("openrouter/") and "OPENROUTER_API_KEY" not in os.environ:
            missing.add("OPENROUTER_API_KEY")
    if missing:
        raise SystemExit(f"set these in the environment or .env first: {sorted(missing)}")


def setup_name(entry: str | dict) -> str:
    """A preset's name, or the name of a setup given as a spec, which joins the known configs."""
    if isinstance(entry, str):
        return entry
    name, config = setups.resolve(entry, SETTINGS)
    SETTINGS["configs"][name] = config
    return name


def instruction_files(artifact: dict, configs: list[str]) -> dict[str, str | None]:
    """Per setup, the workspace name an instruction-file artifact takes there; None for other artifacts."""
    if artifact["type"] != "instruction-file":
        return dict.fromkeys(configs)
    return {c: workspace_name(artifact, SETTINGS["harnesses"][SETTINGS["configs"][c]["harness"]]["instruction_file"])
            for c in configs}


def check_instruction_limit(tasks_dir: Path, file_name: str, limit: dict, config: str) -> None:
    """Stop when a task delivers `file_name` longer than the setup's harness puts in context whole.

    `limit` is the harness's `instruction_limit` in configs.json, {"chars": n} or {"bytes": n}.
    A harness cuts a longer file silently, so its agent would be graded on part of the artifact.
    """
    (unit, most), = limit.items()
    for path in sorted(tasks_dir.glob(f"*/environment/instructions/{file_name}")):
        data = path.read_bytes()
        size = len(data) if unit == "bytes" else len(data.decode())
        if size > most:
            raise SystemExit(f"{config}: task {path.parents[2].name} delivers {file_name} at {size} {unit}, over the "
                             f"{most} its harness puts in context whole; raise the harness's cap and its "
                             f"instruction_limit in configs.json, or shorten the artifact")


def instruction_templates(names: dict[str, str | None], kind: str) -> dict[str, str | None]:
    """Per setup, the harness's own starter text the instruction file goes under, or None.

    A harness that seeds its instruction file on first run, as OpenClaw seeds `AGENTS.md`,
    has that template in the without arm; the with arm gets it too, with the artifact pasted
    below, so the arms differ by the artifact alone. `names` is each setup's delivered file name.
    """
    texts = {}

    def template(config: str) -> str | None:
        harness = SETTINGS["configs"][config]["harness"]
        settings = SETTINGS["harnesses"][harness]
        if not settings.get("instruction_template") or names[config] != settings.get("instruction_file"):
            return None
        if harness not in texts:
            texts[harness] = without_frontmatter(harness_file(harness, settings["instruction_template"], kind))
        return texts[harness]
    return {c: template(c) for c in names}


def harness_file(harness: str, relative: str, kind: str) -> str:
    """A file from the pinned install of a harness's npm package, from the toolchain or the base image."""
    if kind == "docker":
        script = f'cat "$(npm root -g)/{harness}/{relative}"'
        return subprocess.run(["docker", "run", "--rm", base_image(), "sh", "-c", script],
                              capture_output=True, text=True, check=True).stdout
    toolchain = sandbox.toolchain(SETTINGS["cli_versions"])
    return next(toolchain.glob(f"nvm/versions/node/*/lib/node_modules/{harness}/{relative}")).read_text()


def task_folder(instruction_file: str | None, harness: str | None = None) -> str:
    """A setup's task folder in the run, relative to it: one per workspace name an instruction file takes,
    and one per harness whose template it goes under."""
    if instruction_file is None:
        return "tasks"
    return "tasks/" + instruction_file.replace(".", "_") + (f"-{harness}" if harness else "")


def cmd_run(args) -> None:
    load_dotenv(REPO / ".env")
    suite = load_suite(REPO, args.suite)
    artifact, full = suite["artifact"], REPO / suite["artifact"]["path"]
    if args.artifact:
        # A draft runs in the artifact's place, under its name, so every arm differs from earlier runs by its text.
        full = Path(args.artifact).resolve()
        if not (full / "SKILL.md" if artifact["type"] == "skill" else full).is_file():
            raise SystemExit(f"--artifact {args.artifact} is not a {'skill folder' if artifact['type'] == 'skill' else 'file'}")
        if args.minus:
            raise SystemExit("--minus removes a rule from the suite's own artifact; it does not take --artifact")
    wants_api = artifact["type"] == "prompt" and artifact["runner"] == API
    if args.model and args.full:
        raise SystemExit("--full runs the suite's setups; name another setup with --config or --harness and --model")
    named = list(args.config or [])
    if args.model or args.harness:
        if not (args.model and args.harness):
            raise SystemExit("a setup needs both --harness and --model")
        spec = {"harness": args.harness, "model": args.model, "provider": args.provider}
        named.append(setup_name(spec | ({"effort": args.effort} if args.effort else {})))
    # A removal test, like a full run, covers every setup the artifact must support.
    targets = {**SETTINGS["defaults"]["api" if wants_api else "harness"], **suite["setups"]}
    if args.full or (args.minus and not named):
        configs = [setup_name(s) for s in targets["full"]]
    else:
        configs = named or [setup_name(s) for s in targets["run"]]
    unknown = set(configs) - set(SETTINGS["configs"])
    if unknown:
        raise SystemExit(f"unknown configs: {sorted(unknown)}")
    try:
        budget, named = parse_concurrency(args.concurrency)
    except ValueError:
        raise SystemExit(f"--concurrency takes N or CONFIG=N, not {args.concurrency}")
    if set(named) - set(configs):
        raise SystemExit(f"--concurrency names setups this run does not use: {sorted(set(named) - set(configs))}")
    caps = {name: SETTINGS["configs"][name]["max_sessions"] for name in configs
            if "max_sessions" in SETTINGS["configs"][name]} | named
    check_credentials(configs)
    run_dir = new_run_dir(REPO / "evals" / args.suite / "results", args.run_id)
    mismatched = [c for c in configs if (SETTINGS["configs"][c]["harness"] == API) != wants_api]
    if mismatched:
        kind = "api setups" if wants_api else "harness setups"
        raise SystemExit(f"evals/{args.suite} runs on {kind}; pick others than {mismatched}")
    if artifact["type"] == "prompt" and artifact["role"] == "system" and not wants_api:
        openclaw = [c for c in configs if SETTINGS["configs"][c]["harness"] == "openclaw"]
        if openclaw:
            raise SystemExit(f"OpenClaw has no system prompt setting, so {openclaw} cannot run this suite; "
                             "evaluate the text as an AGENTS.md instead")
    variants, sources, attempts = args.variants, {}, args.attempts or 1
    # Cases named outright, or a removal test's cases, run even when marked integration.
    case_names, integration = args.case, bool(args.case) or args.all_cases or bool(args.minus)
    if args.rule:
        rules = checked_rules(suite)
        unknown_rules = sorted(set(args.rule) - set(rules))
        if unknown_rules:
            raise SystemExit(f"not rules in evals/{args.suite}/rules.json: {unknown_rules}")
        case_names = sorted({case for name in args.rule for case in rule_cases(rules, name)} | set(case_names or []))
    if args.trigger and (args.minus or artifact["type"] != "skill"):
        raise SystemExit("--trigger checks a skill's description, on its own")
    if args.trigger:
        variants = ["with"]
    if args.artifact:
        sources["with"] = full
    if args.minus:
        rules = checked_rules(suite)
        if args.minus not in rules or not rules[args.minus]["graders"]:
            raise SystemExit(f"{args.minus} is not a rule with graders in evals/{args.suite}/rules.json")
        minus = MINUS + args.minus
        variants, attempts = ["with", minus], args.attempts or 3
        case_names = case_names or rule_cases(rules, args.minus)
        sources[minus] = run_dir / "minus" / full.name
        minus_artifact(full, rules[args.minus], sources[minus])
    cases = case_dirs(args.suite, case_names, args.probe, args.trigger, integration)
    # A body run measures the text, so a skill is named rather than left to trigger.
    # An instruction file or prompt is always in context.
    pinned = artifact["type"] == "skill" and not args.trigger
    # An API run starts no sandbox, so it needs no image.
    image, environment, described = ("none", [], "none") if wants_api else task_environment(args.env)
    names = instruction_files(artifact, configs)
    templates = instruction_templates(names, args.env)
    deliveries = {c: (names[c], SETTINGS["configs"][c]["harness"] if templates[c] else None) for c in configs}
    task_dirs = {c: task_folder(*deliveries[c]) for c in configs}
    for c in {deliveries[c]: c for c in configs}.values():
        tasks = build_tasks(REPO, suite, cases, variants, image, run_dir / task_dirs[c], sources, pinned, names[c],
                            templates[c])
    for c in configs:
        limit = SETTINGS["harnesses"][SETTINGS["configs"][c]["harness"]].get("instruction_limit")
        if names[c] and limit:
            check_instruction_limit(run_dir / task_dirs[c], names[c], limit, c)
    archive_cases(args.suite, cases, run_dir / "cases")
    reused = {} if args.fresh else reuse_baselines(run_dir, configs, tasks, attempts, task_dirs)
    texts = {c: loaded_texts(artifact, full, names[c]) for c in configs}
    meta = {"suite": args.suite, "artifact": artifact, "artifact_digest": artifact_digest(full),
            "artifact_source": str(full) if args.artifact else None,
            # An instruction file or prompt is one text, delivered alike on every setup.
            "probe_text": None if artifact["type"] == "skill" else first_line(texts[configs[0]][0][1]),
            "minus": args.minus, "trigger": args.trigger,
            "preamble": USE_SKILL.format(skill=artifact["name"]) if pinned else "",
            "configs": {c: SETTINGS["configs"][c] for c in configs},
            "cases": [c.name for c in cases], "variants": variants, "attempts": attempts,
            "harbor": SETTINGS["harbor"], "cli_versions": SETTINGS["cli_versions"], "base_image": image,
            "environment": described,
            "agent_args": {c: agent_args(SETTINGS["configs"][c]) for c in configs},
            "tasks": tasks, "task_dirs": task_dirs, "reused": reused,
            "loaded_tokens": loaded_tokens(texts, {c: SETTINGS["configs"][c]["model"] for c in configs}),
            "started_at": datetime.now(timezone.utc).isoformat()}
    # Each task runs only the attempts its reused trials leave open.
    remaining = {name: {t: attempts - len(reused.get(name, {}).get(t, [])) for t in tasks} for name in configs}
    plans = {name: job_plan(run_dir / task_dirs[name], tasks, [t for t in tasks if not remaining[name][t]], artifact)
             for name in configs}
    queued = args.env == "bwrap" and not wants_api
    if queued:
        gb = {name: SESSION_GB[SETTINGS["configs"][name]["harness"]] for name in configs}
        room = free_memory_gb() - RESERVE_GB
        slots = {"all": budget or DEFAULT_SLOTS["bwrap"]} | caps
        if budget and budget * max(gb.values()) > room:
            print(f"== warning: {budget} sessions may need about {budget * max(gb.values()):.0f} GB; "
                  f"{room:.0f} GB is free beyond the {RESERVE_GB:.0f} GB kept for the host", file=sys.stderr)
        # A given number runs as given; otherwise the queue also keeps the sessions within free memory.
        room = float("inf") if budget else room
        print(f"== memory for sessions: {room:.0f} GB, per session {gb}", file=sys.stderr)
    else:
        slots = {name: caps.get(name, budget or DEFAULT_SLOTS[args.env]) for name in configs}
    meta["slots"] = slots
    print(f"== sessions at once: {slots}", file=sys.stderr)
    (run_dir / "run.json").write_text(json.dumps(meta, indent=2) + "\n")

    def harbor_env(config: dict) -> dict:
        env = dict(os.environ, PYTHONPATH=str(HERE))
        env.update({k: os.path.expandvars(v) for k, v in config.get("env", {}).items()})
        return env

    def run_setup(name: str) -> None:
        config = SETTINGS["configs"][name]
        plan = plans[name]
        if not plan:
            print(f"== {name}: every task reused", file=sys.stderr)
            return
        print(f"== {name}", file=sys.stderr)
        if config["harness"] == API:
            for n, group in by_remaining(remaining[name], [t for _, job_tasks, _ in plan for t in job_tasks]):
                run_api_job(config, run_dir / task_dirs[name], group, n, run_dir / "jobs" / name / API, slots[name])
            return
        with open(run_dir / f"harbor-{name}.log", "w") as log:
            for job, job_tasks, system_prompt in plan:
                groups = by_remaining(remaining[name], job_tasks)
                for n, group in groups:
                    if args.env == "docker":
                        wait_for_docker()
                    subprocess.run(harbor_command(config, run_dir / task_dirs[name], run_dir / "jobs" / name,
                                                  job if len(groups) == 1 else f"{job}-{n}", n, slots[name],
                                                  include=group, system_prompt=system_prompt,
                                                  environment=environment),
                                   env=harbor_env(config), stdout=log, stderr=subprocess.STDOUT, check=False)
        print(f"== {name}: done", file=sys.stderr)

    def run_session(session: tuple[str, str, int, str | None]) -> None:
        name, task, attempt, system_prompt = session
        config = SETTINGS["configs"][name]
        with open(run_dir / f"harbor-{name}.log", "a") as log:
            subprocess.run(harbor_command(config, run_dir / task_dirs[name], run_dir / "jobs" / name, f"{task}.{attempt}", 1, 1,
                                          include=[task], system_prompt=system_prompt, environment=environment),
                           env=harbor_env(config), stdout=log, stderr=subprocess.STDOUT, check=False)

    if queued:
        # Every session of every setup is its own Harbor job, drawn from one queue, longest
        # expected first: no slot idles while another setup still has work, and the slowest
        # sessions do not start last.
        sessions = [(name, task, attempt, system_prompt) for name in configs
                    for _, job_tasks, system_prompt in plans[name] for task in job_tasks
                    for attempt in range(remaining[name][task])]
        expected = {name: expected_seconds(run_dir.parent, name) for name in configs}
        sessions.sort(key=lambda s: expected[s[0]].get(s[1], expected[s[0]].get(None, 0.0)), reverse=True)
        print(f"== {len(sessions)} sessions", file=sys.stderr)
        run_queue(sessions, slots["all"], caps, run_session, gb, room)
        print("== sessions done", file=sys.stderr)
    else:
        # Under Docker setups run one at a time: concurrent Harbor jobs would race to build the same
        # task images.
        with ThreadPoolExecutor(max_workers=1 if args.env == "docker" else len(configs)) as pool:
            list(pool.map(run_setup, configs))
    grade([run_dir], args.judge or SETTINGS["judges"])
    print(report(run_dir))


def by_remaining(remaining: dict[str, int], tasks: list[str]) -> list[tuple[int, list[str]]]:
    """`tasks` grouped by the attempts each still needs, as (attempts, tasks); a Harbor job runs one count."""
    groups = defaultdict(list)
    for task in tasks:
        groups[remaining[task]].append(task)
    return sorted(groups.items())


def parse_concurrency(values: list[str]) -> tuple[int | None, dict[str, int]]:
    """(the last bare N, {CONFIG: N}) from --concurrency values."""
    named = {k: int(v) for k, v in (value.split("=", 1) for value in values if "=" in value)}
    bare = [int(value) for value in values if "=" not in value]
    return (bare[-1] if bare else None), named


# Seconds between two session starts of one setup: starting a burst at once drew rate-limit errors
# (HTTP 429) from Codex, on top of the per-setup caps.
LAUNCH_GAP_SECONDS = 1.0


def run_queue(items: list[tuple], budget: int, caps: dict[str, int], launch,
              gb: dict[str, float] | None = None, room: float = float("inf")) -> None:
    """Run `launch(item)` for every item, `budget` at once and in the given order, with at most
    `caps[setup]` of one setup's items at once, the running items' `gb` within `room` (one item
    always runs), and starts of one setup LAUNCH_GAP_SECONDS apart; an item's first field names its setup."""
    pending, running, next_start = list(items), defaultdict(int), defaultdict(float)
    gb = gb or {}
    ready = threading.Condition()

    def fits(setup: str) -> bool:
        used = sum(n * gb.get(s, 0.0) for s, n in running.items())
        return (running[setup] < caps.get(setup, budget)
                and (not any(running.values()) or used + gb.get(setup, 0.0) <= room))

    def worker() -> None:
        while True:
            with ready:
                while True:
                    item = next((i for i in pending if fits(i[0])), None)
                    if item or not pending:
                        break
                    ready.wait()
                if item is None:
                    return
                pending.remove(item)
                running[item[0]] += 1
                start = max(time.monotonic(), next_start[item[0]])
                next_start[item[0]] = start + LAUNCH_GAP_SECONDS
            try:
                time.sleep(max(0.0, start - time.monotonic()))
                launch(item)
            finally:
                with ready:
                    running[item[0]] -= 1
                    ready.notify_all()

    threads = [threading.Thread(target=worker) for _ in range(min(budget, len(items)))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def free_memory_gb() -> float:
    """Memory the host can give new processes without swapping; unbounded where Linux does not say."""
    try:
        with open("/proc/meminfo") as f:
            kib = next(int(line.split()[1]) for line in f if line.startswith("MemAvailable:"))
    except (FileNotFoundError, StopIteration):
        return float("inf")
    return kib / 1024 ** 2


def agent_seconds(result: dict) -> float | None:
    """How long the agent ran, from a Harbor trial's result.json."""
    phase = result.get("agent_execution") or {}
    if not (phase.get("started_at") and phase.get("finished_at")):
        return None
    start, end = (datetime.fromisoformat(phase[k].replace("Z", "+00:00")) for k in ("started_at", "finished_at"))
    return (end - start).total_seconds()


def expected_seconds(results: Path, config_name: str) -> dict[str | None, float]:
    """Mean agent time per task for the setup over the suite's earlier runs, from Harbor's result.json,
    with the mean over every task under None for tasks never run. Probe trials are left out: they are
    short by design."""
    seconds = defaultdict(list)
    for path in results.glob(f"*/jobs/{config_name}/*/*/result.json"):
        try:
            result = json.loads(path.read_text())
            task = Path(json.loads((path.parent / "config.json").read_text())["task"]["path"]).name
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            continue
        elapsed = agent_seconds(result)
        if not task.startswith(f"{PROBE_CASE}--") and elapsed is not None:
            seconds[task].append(elapsed)
    means = {task: sum(v) / len(v) for task, v in seconds.items()}
    every = [x for v in seconds.values() for x in v]
    return means | ({None: sum(every) / len(every)} if every else {})


def first_line(text: str) -> str:
    """The delivered text's first non-empty line without heading marks, or "": what the probe asks the agent to quote."""
    return next((line.strip().lstrip("#").strip() for line in text.splitlines() if line.strip()), "")


def probe_says_truncated(final_message: str) -> bool:
    """Whether the probe's reply answers `TRUNCATED: yes`, as PROBE_INSTRUCTION asks."""
    return bool(re.search(r"TRUNCATED:\W*yes", final_message, re.I))


def grade_trial(trial: Path, config_name: str, config: dict, artifact: dict, cases_root: Path,
                judges: list[str], specs_root: Path | None = None, probe_text: str | None = None,
                tasks_root: Path | None = None) -> dict:
    """One row per trial: its status, evidence, and grader results.

    Workspaces come from the cases under `cases_root`, plus the instruction file a
    task delivered, found in the setup's task folder `tasks_root` (default the run's
    `tasks` beside the cases); graders.json comes from `specs_root` when given,
    otherwise from the same cases.
    """
    harbor_config = json.loads((trial / "config.json").read_text())
    case, variant = Path(harbor_config["task"]["path"]).name.split("--")
    row = {"trial": trial.name, "config": config_name, "harness": config["harness"], "model": config["model"],
           "case": case, "variant": variant}
    result_path = trial / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    if not result:
        row["status"] = "incomplete"
        return row
    error = (result.get("exception_info") or {}).get("exception_type")
    # Running out of time is the agent's own outcome, graded when the snapshot exists;
    # any other exception is infrastructure and not graded.
    if error and error != "AgentTimeoutError":
        row.update(status="infra_error", error=error)
        return row
    workspace = trial / "verifier" / "workspace"
    # test.sh writes reward.json only after the whole copy succeeded.
    if not (trial / "verifier" / "reward.json").is_file() or not workspace.is_dir():
        row.update(status="missing_evidence", error=error)
        return row
    row["timed_out"] = error == "AgentTimeoutError"
    row["agent_seconds"] = agent_seconds(result)
    case_dir = cases_root / case
    spec = load_spec((specs_root or cases_root) / case)
    evidence = EXTRACTORS[config["harness"]](trial / "agent")
    # The harness ended the run itself, as when a reply hit its output cap.
    if evidence.get("terminal_error"):
        row.update(status="infra_error", error=evidence["terminal_error"])
        return row
    final_message = evidence.pop("final_message") if evidence["complete"] else None
    # The messages go to graders only, not into the saved evidence.
    messages = evidence.pop("messages")
    messages = messages if evidence["complete"] else None
    ops = evidence.pop("ops", None)
    row.update(status="ok", final_message=final_message, evidence=evidence)
    if artifact["type"] == "skill":
        skill = artifact["name"]
        loaded, foreign, listed = evidence["skills_loaded"], evidence["foreign_skills_loaded"], evidence["skills_listed"]
        row.update(skill_loaded=None if loaded is None else skill in loaded,
                   skill_loaded_expected=spec["expect_skill_loaded"][arm(variant)],
                   # A same-named skill from anywhere but the installed copy.
                   foreign_copy_loaded=None if foreign is None else skill in foreign,
                   harness_lists_skill=None if listed is None else skill in listed)
        marker = skill
    else:
        # An instruction file or prompt reaches the model without a tool call, so no transcript shows a load.
        row.update(skill_loaded=None, delivered=variant != "without")
        marker = probe_text
    if spec.get("probe"):
        row["probe_sees_artifact"] = None if final_message is None or not marker else marker in final_message
        if artifact["type"] == "instruction-file":
            row["probe_truncated"] = None if final_message is None else probe_says_truncated(final_message)
    run = {"final_message": final_message, "messages": messages, "writes": evidence["writes"],
           "skills_loaded": evidence["skills_loaded"], "ops": ops}
    delivered = (tasks_root or cases_root.parent / "tasks") / f"{case}--{variant}" / "environment" / "instructions"
    with temporary_initial_workspace(case_dir) as initial:
        if delivered.is_dir():
            shutil.copytree(delivered, initial, dirs_exist_ok=True)
        row["graders"] = run_graders(spec["graders"], arm(variant), workspace, initial, config["harness"], run,
                                     judges)
    return row


def grade(run_dirs: list[Path], judges: list[str], graders_from_repo: bool = False) -> None:
    """Grade every trial of each run from its archived cases; optionally with the repo's current graders.json.

    The runs share one batch of judge calls, so outputs graded against the same criterion go to the judge
    together, and each run records the token usage of the calls it shared in `judge-usage.json`.
    """
    load_dotenv(REPO / ".env")
    if len({run_dir.resolve().parent for run_dir in run_dirs}) > 1:
        raise SystemExit("grade runs of one suite together; these runs sit in different results folders")
    rows = {run_dir: grade_rows(run_dir, judges, graders_from_repo) for run_dir in run_dirs}
    # Judge calls batch across every setup in the runs; verdicts are shared across the suite's runs.
    usage = judge_pending([row for run in rows.values() for row in run], judges,
                          run_dirs[0].parent / "judge-cache.jsonl")
    for run_dir, run in rows.items():
        (run_dir / "grades.jsonl").write_text("".join(json.dumps(row) + "\n" for row in run))
        (run_dir / "judge-usage.json").write_text(json.dumps(
            {"graded_with": sorted(r.name for r in run_dirs), "calls": usage}, indent=1) + "\n")
        (run_dir / "report.md").write_text(report(run_dir))


def grade_rows(run_dir: Path, judges: list[str], graders_from_repo: bool) -> list[dict]:
    """One row per trial of the run, and per attempt it never produced, with `llm` grades left pending."""
    meta = json.loads((run_dir / "run.json").read_text())
    cases_root = run_dir / "cases"
    suite = meta.get("suite") or meta["skill"]
    artifact = meta.get("artifact") or {"type": "skill", "name": meta["skill"]}
    specs_root = REPO / "evals" / suite if graders_from_repo else None
    rows = []
    for config_name, config in meta["configs"].items():
        sources = {Path(src).name: src for srcs in meta.get("reused", {}).get(config_name, {}).values()
                   for src in srcs}
        trials = trial_dirs(run_dir / "jobs" / config_name) + trial_dirs(run_dir / "reused" / config_name)
        graded = []
        for trial in trials:
            graded.append(grade_trial(trial, config_name, config, artifact, cases_root, judges, specs_root,
                                      meta.get("probe_text"),
                                      run_dir / meta.get("task_dirs", {}).get(config_name, "tasks")))
            graded[-1]["trial_path"] = trial.relative_to(run_dir).as_posix()
            if trial.relative_to(run_dir).parts[0] == "reused":
                graded[-1]["reused_from"] = sources.get(trial.name)
        rows += graded + missing_trials(meta, config_name, config, graded)
    return rows


def missing_trials(meta: dict, config_name: str, config: dict, graded: list[dict]) -> list[dict]:
    """A row for each expected attempt Harbor never produced, so an absent arm still shows."""
    seen = defaultdict(int)
    for row in graded:
        seen[(row["case"], row["variant"])] += 1
    rows = []
    for task in meta["tasks"]:
        case, variant = task.split("--")
        rows += [{"config": config_name, "harness": config["harness"], "model": config["model"],
                  "case": case, "variant": variant, "status": "missing"}] * (meta["attempts"] - seen[(case, variant)])
    return rows


def report(run_dir: Path) -> str:
    """Pass counts per case, configuration and variant; infra errors and undecided grades apart; the
    work each run took; the tokens of each text the with arm loads; and for a trigger check, how often
    each kind of case loaded the skill."""
    rows = [json.loads(line) for line in (run_dir / "grades.jsonl").read_text().splitlines()]
    cells = defaultdict(list)
    arms = defaultdict(list)  # (config, variant) -> ok rows
    for row in rows:
        cells[(row["case"], row["config"], row["variant"])].append(row)
    lines = [f"# {run_dir.name}", ""]
    disagreements, collisions = [], []
    verdicts, cached = 0, 0
    cost, cost_known = defaultdict(float), defaultdict(bool)
    for (case, config, variant), trials in sorted(cells.items()):
        ok = [t for t in trials if t["status"] == "ok"]
        errors = [t.get("error") or t["status"] for t in trials if t["status"] != "ok"]
        timed_out = sum(1 for t in ok if t.get("timed_out"))
        reused = sum(1 for t in ok if t.get("reused_from"))
        loaded = sum(1 for t in ok if t["skill_loaded"])
        unknown = sum(1 for t in ok if t["skill_loaded"] is None and "delivered" not in t)
        grader_counts = defaultdict(lambda: [0, 0, 0])
        arms[(config, variant)] += ok
        for t in ok:
            # A reused trial's cost was paid by the run it came from.
            if t["evidence"].get("cost_usd") is not None and not t.get("reused_from"):
                cost[config] += t["evidence"]["cost_usd"]
                cost_known[config] = True
            if t.get("foreign_copy_loaded"):
                collisions.append(f"{case} / {config} / {variant}: loaded a same-named skill that is not the copy under test")
            if variant == "without" and t.get("harness_lists_skill"):
                collisions.append(f"{case} / {config} / without: the harness lists a skill with this name")
            for name, g in t["graders"].items():
                grader_counts[name][0 if g["pass"] else (2 if g["pass"] is None else 1)] += 1
                by_judge = {m: v["pass"] for m, v in g.get("judges", {}).items()}
                if len(set(by_judge.values())) > 1:
                    disagreements.append(f"{case} / {config} / {variant} / {name}: {by_judge}")
                verdicts += len(by_judge)
                cached += sum(1 for v in g.get("judges", {}).values() if v.get("cached"))
        grades = ", ".join(f"{n} {p}/{p + f}" + (f" ({u} undecided)" if u else "")
                           for n, (p, f, u) in grader_counts.items())
        probe = ""
        if ok and "probe_sees_artifact" in ok[0]:
            probe = f" | visible {sum(1 for t in ok if t['probe_sees_artifact'])}/{len(ok)}"
        if ok and "probe_truncated" in ok[0]:
            probe += f" | truncated {sum(1 for t in ok if t['probe_truncated'])}/{len(ok)}"
        if ok and "delivered" in ok[0]:
            load = " | artifact " + ("delivered" if ok[0]["delivered"] else "absent")
        else:
            expected = ok[0]["skill_loaded_expected"] if ok else None
            load = (f" | skill loaded {loaded}/{len(ok)} (expected {expected})"
                    + (f", {unknown} unknown" if unknown else ""))
        lines.append(f"- {case} | {config} | {variant}: {len(ok)} ok"
                     + (f" ({reused} reused)" if reused else "")
                     + (f" ({timed_out} timed out)" if timed_out else "")
                     + (f", {len(errors)} not graded {errors}" if errors else "")
                     + load + probe
                     + (f" | {describe_work(work(ok))}" if work(ok) else "")
                     + f" | {grades}")
    totals = graders_passed(rows)
    if totals:
        lines += ["", "Graders passed in every attempt, per setup and arm; a grader counts once however many "
                  "attempts ran:"] + totals
    if any(work(ok) for ok in arms.values()):
        lines += ["", "Median work per run: agent time, tool calls, and input (cached or not) and output tokens "
                      "summed over the run's model calls:"]
        for config in sorted({c for c, _ in arms}):
            medians = {v: work(ok) for (c, v), ok in arms.items() if c == config and work(ok)}
            with_, without = medians.get("with", {}), medians.get("without", {})
            change = ", ".join(f"{label} {with_[key] / without[key] - 1:+.0%}"
                               for key, label in (("input", "input"), ("seconds", "time"))
                               if with_.get(key) and without.get(key))
            lines.append(f"- {config}: " + "; ".join(f"{v} {describe_work(m)}" for v, m in sorted(medians.items()))
                         + (f" ({change} with the artifact)" if change else ""))
    retried = [f"{t['case']} / {t['config']} / {t['variant']}: {t['evidence']['retries']} retries"
               for ok in arms.values() for t in ok if t["evidence"].get("retries") and not t.get("reused_from")]
    if retried:
        lines += ["", "Runs whose harness retried failed model calls; their time includes the provider's delay:"]
        lines += [f"- {r}" for r in retried]
    meta_path = run_dir / "run.json"
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    if meta.get("loaded_tokens"):
        lines += ["", "Tokens of each text the with arm loads:", "", "| load path | setup | tokens | method |",
                  "| --- | --- | --- | --- |"]
        lines += [f"| {e['path']} | {config} | {'not counted' if e['tokens'] is None else e['tokens']} | "
                  f"{e.get('method') or e.get('not_counted')} |"
                  for config, entries in sorted(meta["loaded_tokens"].items()) for e in entries]
    if meta.get("trigger"):
        lines += ["", "Triggering, runs that loaded the skill:"] + trigger_counts(rows)
    lines += ["", "Cost reported by the harness (USD):"]
    lines += [f"- {config}: " + (f"{cost[config]:.4f}" if cost_known[config] else "not reported")
              for config in sorted({k[1] for k in cells})]
    if cached:
        lines += ["", f"Judge verdicts reused from earlier grading of the same output: {cached} of {verdicts}."]
    usage_path = run_dir / "judge-usage.json"
    if usage_path.is_file():
        lines += judge_usage(json.loads(usage_path.read_text()), run_dir.name)
    if collisions:
        lines += ["", "Same-named skill collisions:"] + [f"- {c}" for c in sorted(set(collisions))]
    if disagreements:
        lines += ["", "Judge disagreements:"] + [f"- {d}" for d in disagreements]
    return "\n".join(lines) + "\n"


def graders_passed(rows: list[dict]) -> list[str]:
    """Per setup and arm, the case graders that passed in every attempt, out of those decided at least once."""
    results = defaultdict(list)  # (config, variant, case, grader) -> decided passes
    for row in rows:
        if row["status"] != "ok" or row["case"] == PROBE_CASE:
            continue
        for name, g in row["graders"].items():
            if g["pass"] is not None:
                results[(row["config"], row["variant"], row["case"], name)].append(g["pass"])
    cells = defaultdict(lambda: [0, 0])
    for (config, variant, _, _), passes in results.items():
        cells[(config, variant)][0] += all(passes)
        cells[(config, variant)][1] += 1
    return [f"- {config} | {variant}: {p}/{n}" for (config, variant), (p, n) in sorted(cells.items())]


def judge_usage(usage: dict, run: str) -> list[str]:
    """Report lines for the judge calls of the grading that last wrote this run, per judge."""
    shared = [r for r in usage["graded_with"] if r != run]
    totals = defaultdict(lambda: [0, 0, 0, 0])  # judge -> [calls, outputs, input, output]
    for call in usage["calls"]:
        t = totals[call["judge"]]
        t[0] += 1
        t[1] += call["outputs"]
        t[2] += call.get("input_tokens", 0)
        t[3] += call.get("output_tokens", 0)
    lines = ["", "Judge calls in the last grading" + (f", shared with {', '.join(shared)}" if shared else "") + ":"]
    lines += [f"- {judge}: {calls} calls, {outputs} outputs, in {inp / 1000:.1f}k out {out / 1000:.1f}k tokens"
              for judge, (calls, outputs, inp, out) in sorted(totals.items())] or ["- none: every verdict was reused"]
    return lines


def trigger_counts(rows: list[dict]) -> list[str]:
    """Per setup, loads among should-trigger cases and among near-misses; transcripts that do not say are left out."""
    counts = defaultdict(lambda: [0, 0])  # (config, expected) -> [loaded, known]
    for row in rows:
        if row["status"] == "ok" and row.get("skill_loaded") is not None:
            cell = counts[(row["config"], row["skill_loaded_expected"])]
            cell[0] += row["skill_loaded"]
            cell[1] += 1
    return [f"- {config}: should-trigger {counts[(config, True)][0]}/{counts[(config, True)][1]}, "
            f"near-miss {counts[(config, False)][0]}/{counts[(config, False)][1]}"
            for config in sorted({c for c, _ in counts})]


def checked_rules(suite: dict) -> dict:
    """The suite's rule map, stopping on any rule whose text or graders do not resolve."""
    artifact = suite["artifact"]
    rules = load_rules(REPO / "evals" / suite["name"])
    problems = check_rules(rules, artifact_root(REPO, artifact), REPO / "evals" / suite["name"])
    if artifact["type"] == "instruction-file":
        problems += [f"{name}: file must be {Path(artifact['path']).name}" for name, rule in rules.items()
                     if rule["file"] != Path(artifact["path"]).name]
    if problems:
        raise SystemExit("rules.json problems:\n" + "\n".join(f"- {p}" for p in problems))
    return rules


def setup_label(name: str, meta: dict) -> str:
    """A setup's name, marked with its config's digest when the run used an earlier config under that name,
    so runs of a changed setup are never pooled with its current runs."""
    recorded, current = meta.get("configs", {}).get(name), SETTINGS["configs"].get(name)
    if recorded is None or current is None or recorded == current:
        return name
    return f"{name}{EARLIER}{hashlib.sha256(json.dumps(recorded, sort_keys=True).encode()).hexdigest()[:6]})"


def cmd_rules(args) -> None:
    """Per-rule pass counts from every graded run of the artifact's current text."""
    suite = load_suite(REPO, args.suite)
    rules = checked_rules(suite)
    current = artifact_digest(REPO / suite["artifact"]["path"])
    runs = []
    for meta_path in sorted((REPO / "evals" / args.suite / "results").glob("*/run.json")):
        meta, grades = json.loads(meta_path.read_text()), meta_path.parent / "grades.jsonl"
        digest = meta.get("artifact_digest") or meta.get("skill_digest")
        # A probe-only run checks delivery, not the text's effect.
        probe_only = set(meta.get("cases") or [None]) <= {PROBE_CASE}
        if grades.is_file() and not probe_only and (args.all_versions or digest == current):
            rows = [json.loads(line) for line in grades.read_text().splitlines()]
            runs.append((meta, [row | {"config": setup_label(row["config"], meta)} for row in rows]))
    untestable = sum(1 for r in rules.values() if r.get("untestable"))
    untested = sum(1 for r in rules.values() if not r["graders"]) - untestable
    print(f"{len(rules)} rules, {untested} without graders, {untestable} untestable from outputs; {len(runs)} runs of "
          + ("any artifact text" if args.all_versions else "the current artifact text") + ".\n")
    if not args.min_set:
        print(tabulate(rules, runs, guard_refs(REPO / "evals" / args.suite)))
        return
    suite_dir = REPO / "evals" / args.suite
    # Reserve cases stay candidates, so a later map or run can bring one back.
    acceptance = {p.name: acceptance_graders(suite_dir, p.name) for p in case_dirs(args.suite, None, False)
                  if not load_spec(p).get("integration")}
    targets = {**SETTINGS["defaults"]["harness"], **suite["setups"]}
    chosen = min_set(rules, runs, acceptance, {setup_name(s) for s in targets["full"]}, args.gaps,
                     guard_refs(suite_dir)["without"])
    print(f"Regular set: {len(chosen['kept'])} of {len(acceptance)} cases cover every mapped rule they test" + (" and every gap on the --full setups" if args.gaps else "") + ".\n")
    for case in chosen["kept"]:
        own = sorted({u[1] if u[0] in ("rule", "effect") else f"gap {u[2]}" for u in chosen["units"][case]
                     if all(u not in chosen["units"][c] for c in chosen["kept"] if c != case)})
        print(f"- {case} ({chosen['cost'][case] / 1000:.0f}k tokens): only it covers {', '.join(own)}")
    print(f"\nMark `reserve`: {', '.join(chosen['dropped']) or 'none'}")
    if chosen["rules_outside"]:
        print(f"\nRules tested only outside the regular set: {', '.join(chosen['rules_outside'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("suite", help="folder name under evals/")
    chosen = run.add_mutually_exclusive_group()
    chosen.add_argument("--config", action="append",
                        help="a preset from configs.json; default the suite's `run` setups in eval.json, else "
                             f"{SETTINGS['defaults']['harness']['run']}, or {SETTINGS['defaults']['api']['run']} "
                             "for an api prompt; with --minus, the --full setups")
    chosen.add_argument("--full", action="store_true",
                        help="run the suite's `full` setups in eval.json, else "
                             f"{SETTINGS['defaults']['harness']['full']}, or {SETTINGS['defaults']['api']['full']} "
                             "for an api prompt")
    run.add_argument("--harness", choices=sorted(SETTINGS["harnesses"]),
                     help="with --model, one more setup beside any --config ones")
    run.add_argument("--model", help="a model named in configs.json, or a full id such as openrouter/vendor/model")
    run.add_argument("--effort", help="reasoning effort, or `default` to send none; default high")
    run.add_argument("--provider", help="OpenRouter provider to try first, or a comma-separated order; "
                                        "default the model's preferred providers")
    run.add_argument("--case", action="append", help="case folder name; default every case not marked integration or reserve")
    run.add_argument("--rule", action="append",
                     help="a rule from rules.json: run the cases whose graders test it (an edit round's cases)")
    run.add_argument("--all-cases", action="store_true",
                     help="also run the cases marked integration or reserve, as an acceptance run does")
    run.add_argument("--variants", type=lambda s: s.split(","), default=["with", "without"])
    run.add_argument("--attempts", type=int, help="runs per task; default 1, or 3 with --minus")
    run.add_argument("--concurrency", action="append", default=[], metavar="[CONFIG=]N",
                     help="N: sessions at once across all setups, longest expected first "
                          f"(default: up to {DEFAULT_SLOTS['bwrap']} under bwrap, as many as free memory holds; "
                          f"under Docker, per setup, {DEFAULT_SLOTS['docker']}); CONFIG=N caps one setup, over its harness's "
                          "max_sessions in configs.json. "
                          "A given number runs as given, with a warning when it will not fit in memory")
    run.add_argument("--env", choices=["bwrap", "docker"], default=DEFAULT_ENV,
                     help=f"where sessions run; default {DEFAULT_ENV}")
    run.add_argument("--probe", action="store_true",
                     help="add a case asking the agent to list its skills or quote its instruction file")
    run.add_argument("--judge", action="append")
    run.add_argument("--run-id")
    run.add_argument("--fresh", action="store_true",
                     help="rerun every task instead of reusing matching earlier trials")
    run.add_argument("--trigger", action="store_true",
                     help="check the skill's description: the with arm only, left to trigger, on every case "
                          "including trigger_only ones")
    run.add_argument("--artifact", metavar="PATH",
                     help="run this draft in place of the suite's artifact, under its name; compare its with arm "
                          "against the artifact's runs with `compare`")
    run.add_argument("--minus", metavar="RULE",
                     help="compare the full artifact with a copy lacking this rule from rules.json, on the rule's cases")
    regrade = sub.add_parser("grade")
    regrade.add_argument("run_dirs", nargs="+", type=Path, metavar="run_dir",
                         help="one or more runs of the suite, graded with shared judge calls")
    regrade.add_argument("--judge", action="append")
    regrade.add_argument("--graders-from-repo", action="store_true",
                         help="grade with the repo's current graders.json instead of the run's copy")
    show = sub.add_parser("report")
    show.add_argument("run_dir", type=Path)
    versus = sub.add_parser("compare", help="compare a candidate's with-arm runs against a baseline's")
    versus.add_argument("--baseline", action="append", type=Path, required=True, metavar="RUN_DIR")
    versus.add_argument("--candidate", action="append", type=Path, required=True, metavar="RUN_DIR")
    versus.add_argument("--pairwise", metavar="JUDGE",
                        help="also judge whole outputs pairwise, blinded, with this judge model")
    versus.add_argument("--case", action="append", help="compare only this case; default every case")
    table = sub.add_parser("rules")
    table.add_argument("suite", help="folder name under evals/")
    table.add_argument("--all-versions", action="store_true", help="include runs of earlier artifact text")
    table.add_argument("--min-set", action="store_true",
                       help="list the cheapest regular cases that keep every mapped rule covered")
    table.add_argument("--gaps", action="store_true",
                       help="with --min-set, also keep every case the current text fails in most runs")
    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "rules":
        cmd_rules(args)
    elif args.command == "grade":
        grade(args.run_dirs, args.judge or SETTINGS["judges"], args.graders_from_repo)
        for run_dir in args.run_dirs:
            print(report(run_dir))
    elif args.command == "compare":
        load_dotenv(REPO / ".env")
        meta = json.loads((args.candidate[0] / "run.json").read_text())
        text = compare(args.baseline, args.candidate, REPO / "evals" / meta["suite"], args.pairwise, args.case)
        (args.candidate[0] / "compare.md").write_text(text)
        print(text)
    else:
        print(report(args.run_dir))


if __name__ == "__main__":
    main()
