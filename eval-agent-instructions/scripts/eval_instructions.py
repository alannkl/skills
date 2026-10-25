#!/usr/bin/env python3
"""Evaluate agent instructions with and without them across agent harnesses and models, through Harbor.

Run from the root of the repository that holds the artifact and its `evals/<suite>/`.

  eval_instructions.py run <suite> [--config NAME... | --full] [--harness H --model M [--effort E] [--provider P]]
                           [--case NAME]... [--attempts N] [--probe] [--fresh-baseline]
                           [--env bwrap|docker] [--concurrency N] [--concurrency CONFIG=N]...
  eval_instructions.py run <suite> --minus RULE [--config NAME]... [--harness H --model M ...]
  eval_instructions.py grade <run-dir> [--judge MODEL]...
  eval_instructions.py report <run-dir>
  eval_instructions.py rules <suite> [--all-versions]

`run` builds one Harbor task per case and variant, runs each configuration as a
Harbor job, then grades and reports. The arms not under test (without the
artifact; with it, for --minus) reuse earlier graded trials when their task
directory, configuration, Harbor version and agent arguments all match. Results
go to evals/<suite>/results/<run-id>/. Grading reads only saved artifacts and
the run's own copy of its cases, so `grade` reruns with other judges, or with
the repo's current graders through --graders-from-repo, without rerunning any agent.

`--minus RULE` runs the full artifact against a copy lacking that rule's text
from evals/<suite>/rules.json, three times each by default, on the cases whose
graders test the rule and on the --full setups unless --config names others; for a skill, both arms are told to use it. `rules` checks
the map and tabulates each rule's grader results over every run of the current
artifact text.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path.cwd()
sys.path.insert(0, str(HERE))

from evidence import EXTRACTORS  # noqa: E402
from graders import judge_pending, run_graders, temporary_initial_workspace  # noqa: E402
from rules import MINUS, arm, artifact_digest, check_rules, load_rules, minus_artifact, rule_cases, tabulate  # noqa: E402
from tasks import PROBE_CASE, artifact_root, build_tasks, load_spec, load_suite, task_digest  # noqa: E402
from api_runner import run_api_job  # noqa: E402
import sandbox  # noqa: E402
import setups  # noqa: E402

SETTINGS = json.loads((HERE / "configs.json").read_text())
SETTINGS["configs"] = setups.catalog(SETTINGS)
# bubblewrap sandboxes start faster and cost less memory than containers; Docker covers hosts without it.
DEFAULT_ENV = "bwrap" if sys.platform == "linux" and shutil.which("bwrap") else "docker"
# Sessions at once across all setups: at most 16 under bwrap, fewer when the host's memory cannot hold
# them; Docker setups run one at a time, each container capped at 2 GB.
DEFAULT_SLOTS = {"bwrap": 16, "docker": 6}
# Memory a session holds midway through a run, in GB. OpenClaw's Node heap grows over a session, from
# about 0.3 GB to 1-1.9 GB; Claude Code and Codex sessions stayed near 0.3 GB.
SESSION_GB = {"openclaw": 1.0, "claude-code": 0.5, "codex": 0.5, "api": 0.0}
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
# Names the installed copy by path: a harness may ship a built-in skill with the same name.
USE_SKILL = "Use the skill at /skills/{skill}/SKILL.md for this task.\n\n"
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
    return json.dumps(overlay)


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
        return args + ["--ak", f"openclaw_config={openclaw_model_config(config)}"]
    native = {} if config.get("builtin_skills") else dict(BLOCK_BUILTIN_SKILLS[harness])
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


def stored_baseline(results: Path, run_id: str, config: dict, task: str, digest: str, attempts: int) -> list[Path]:
    """Graded trials of the same task from earlier runs, newest first, when at least `attempts` exist.

    A trial matches when its task directory hashes the same and it ran under the same
    configuration, Harbor version and agent arguments; with fewer matches the task runs fresh.
    """
    case, variant = task.split("--")
    metas = [(p.parent, json.loads(p.read_text())) for p in results.glob("*/run.json") if p.parent.name != run_id]
    found = []
    for prior, meta in sorted(metas, key=lambda m: m[1].get("started_at", ""), reverse=True):
        task_dir, grades = prior / "tasks" / task, prior / "grades.jsonl"
        if (meta.get("harbor") != SETTINGS["harbor"] or not task_dir.is_dir() or not grades.is_file()
                or task_digest(task_dir) != digest):
            continue
        names = {name for name, c in meta["configs"].items()
                 if c == config and meta.get("agent_args", {}).get(name) == agent_args(config)}
        for line in grades.read_text().splitlines():
            row = json.loads(line)
            # A reused row points at an older run's trial, which this loop reaches on its own.
            if (row["config"] in names and (row["case"], row["variant"]) == (case, variant)
                    and row["status"] == "ok" and not row.get("reused_from")):
                found.append(prior / row.get("trial_path", f"jobs/{row['config']}/{row['trial']}"))
    return found[:attempts] if len(found) >= attempts else []


def reuse_baselines(run_dir: Path, configs: list[str], tasks: list[str], attempts: int, under_test: str) -> dict:
    """Copy matching earlier trials of every arm but the one under test into run_dir/reused/<config>/.

    Returns {config: {task: [source]}}.
    """
    results = run_dir.parent
    digests = {task: task_digest(run_dir / "tasks" / task) for task in tasks
               if not task.endswith(f"--{under_test}")}
    reused = {}
    for name in configs:
        for task, digest in digests.items():
            trials = stored_baseline(results, run_dir.name, SETTINGS["configs"][name], task, digest, attempts)
            for trial in trials:
                shutil.copytree(trial, run_dir / "reused" / name / trial.name)
            if trials:
                reused.setdefault(name, {})[task] = [str(t.relative_to(results)) for t in trials]
    return reused


def case_dirs(suite: str, names: list[str] | None, probe: bool) -> list[Path]:
    """The named cases, or all of them; the probe joins when --probe is set or named as a case."""
    root = REPO / "evals" / suite
    found = sorted(p for p in root.iterdir() if (p / "graders.json").is_file())
    if names:
        probe = probe or PROBE_CASE in names
        names = [n for n in names if n != PROBE_CASE]
        missing = set(names) - {p.name for p in found}
        if missing:
            raise SystemExit(f"unknown cases: {sorted(missing)}")
        found = [p for p in found if p.name in names]
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


def cmd_run(args) -> None:
    load_dotenv(REPO / ".env")
    suite = load_suite(REPO, args.suite)
    artifact, full = suite["artifact"], REPO / suite["artifact"]["path"]
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
    check_credentials(configs)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = REPO / "evals" / args.suite / "results" / run_id
    if run_dir.exists():
        raise SystemExit(f"{run_dir} exists")
    mismatched = [c for c in configs if (SETTINGS["configs"][c]["harness"] == API) != wants_api]
    if mismatched:
        kind = "api setups" if wants_api else "harness setups"
        raise SystemExit(f"evals/{args.suite} runs on {kind}; pick others than {mismatched}")
    if artifact["type"] == "prompt" and artifact["role"] == "system" and not wants_api:
        openclaw = [c for c in configs if SETTINGS["configs"][c]["harness"] == "openclaw"]
        if openclaw:
            raise SystemExit(f"OpenClaw has no system prompt setting, so {openclaw} cannot run this suite; "
                             "evaluate the text as an AGENTS.md instead")
    variants, under_test, sources, attempts, preamble = args.variants, "with", {}, args.attempts or 1, ""
    case_names = args.case
    if args.minus:
        rules = checked_rules(suite)
        if args.minus not in rules or not rules[args.minus]["graders"]:
            raise SystemExit(f"{args.minus} is not a rule with graders in evals/{args.suite}/rules.json")
        under_test = MINUS + args.minus
        variants, attempts = ["with", under_test], args.attempts or 3
        case_names = case_names or rule_cases(rules, args.minus)
        sources[under_test] = run_dir / "minus" / full.name
        minus_artifact(full, rules[args.minus], sources[under_test])
        # A removal test measures the text, so a skill is named rather than left to trigger.
        # An instruction file is always in context.
        if artifact["type"] == "skill":
            preamble = USE_SKILL.format(skill=artifact["name"])
    cases = case_dirs(args.suite, case_names, args.probe)
    # An API run starts no sandbox, so it needs no image.
    image, environment, described = ("none", [], "none") if wants_api else task_environment(args.env)
    tasks = build_tasks(REPO, suite, cases, variants, image, run_dir / "tasks", sources, preamble)
    archive_cases(args.suite, cases, run_dir / "cases")
    reused = {} if args.fresh_baseline else reuse_baselines(run_dir, configs, tasks, attempts, under_test)
    meta = {"suite": args.suite, "artifact": artifact, "artifact_digest": artifact_digest(full),
            "probe_text": None if artifact["type"] == "skill" else first_line(full),
            "minus": args.minus, "preamble": preamble,
            "configs": {c: SETTINGS["configs"][c] for c in configs},
            "cases": [c.name for c in cases], "variants": variants, "attempts": attempts,
            "harbor": SETTINGS["harbor"], "cli_versions": SETTINGS["cli_versions"], "base_image": image,
            "environment": described,
            "agent_args": {c: agent_args(SETTINGS["configs"][c]) for c in configs},
            "tasks": tasks, "reused": reused, "started_at": datetime.now(timezone.utc).isoformat()}
    plans = {name: job_plan(run_dir / "tasks", tasks, sorted(reused.get(name, {})), artifact) for name in configs}
    if args.env == "docker" and not wants_api:
        slots = {name: named.get(name, budget or DEFAULT_SLOTS["docker"]) for name in configs}
    else:
        trials = {name: attempts * sum(len(job_tasks) for _, job_tasks, _ in plans[name]) for name in configs}
        seconds = {name: mean_agent_seconds(run_dir.parent, name) for name in configs}
        gb = {name: SESSION_GB[SETTINGS["configs"][name]["harness"]] for name in configs}
        room = free_memory_gb() - RESERVE_GB
        slots = choose_slots(budget, trials, seconds, named, gb, room)
        need = sum(slots[name] * gb[name] for name in configs)
        if need > room:
            print(f"== warning: {sum(slots.values())} sessions need about {need:.0f} GB; "
                  f"{room:.0f} GB is free beyond the {RESERVE_GB:.0f} GB kept for the host", file=sys.stderr)
    meta["slots"] = slots
    print(f"== sessions at once: {slots}", file=sys.stderr)
    (run_dir / "run.json").write_text(json.dumps(meta, indent=2) + "\n")

    def run_setup(name: str) -> None:
        config = SETTINGS["configs"][name]
        plan = plans[name]
        if not plan:
            print(f"== {name}: every task reused", file=sys.stderr)
            return
        print(f"== {name}", file=sys.stderr)
        if config["harness"] == API:
            run_api_job(config, run_dir / "tasks", [t for _, job_tasks, _ in plan for t in job_tasks], attempts,
                        run_dir / "jobs" / name / API, slots[name])
            return
        env = dict(os.environ, PYTHONPATH=str(HERE))
        env.update({k: os.path.expandvars(v) for k, v in config.get("env", {}).items()})
        with open(run_dir / f"harbor-{name}.log", "w") as log:
            for job, job_tasks, system_prompt in plan:
                if args.env == "docker":
                    wait_for_docker()
                subprocess.run(harbor_command(config, run_dir / "tasks", run_dir / "jobs" / name, job, attempts,
                                              slots[name], include=job_tasks,
                                              system_prompt=system_prompt,
                                              environment=environment),
                               env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
        print(f"== {name}: done", file=sys.stderr)

    # Setups run side by side, sharing the slots. Under Docker they run one at a time:
    # concurrent Harbor jobs would race to build the same task images.
    with ThreadPoolExecutor(max_workers=1 if args.env == "docker" else len(configs)) as pool:
        list(pool.map(run_setup, configs))
    grade(run_dir, args.judge or SETTINGS["judges"])
    print(report(run_dir))


def parse_concurrency(values: list[str]) -> tuple[int | None, dict[str, int]]:
    """(the last bare N, {CONFIG: N}) from --concurrency values."""
    named = {k: int(v) for k, v in (value.split("=", 1) for value in values if "=" in value)}
    bare = [int(value) for value in values if "=" not in value]
    return (bare[-1] if bare else None), named


def choose_slots(budget: int | None, trials: dict[str, int], seconds: dict[str, float | None],
                 named: dict[str, int], gb: dict[str, float], room: float) -> dict[str, int]:
    """Sessions at once per setup: an explicit budget as given, otherwise the largest default-or-smaller
    budget whose sessions fit in `room` GB, by each setup's `gb` per session."""
    if budget is None:
        budget = DEFAULT_SLOTS["bwrap"]
        while budget > len(trials) and sum(n * gb[name] for name, n in
                                           split_slots(budget, trials, seconds, named).items()) > room:
            budget -= 1
    return split_slots(budget, trials, seconds, named)


def free_memory_gb() -> float:
    """Memory the host can give new processes without swapping; unbounded where Linux does not say."""
    try:
        with open("/proc/meminfo") as f:
            kib = next(int(line.split()[1]) for line in f if line.startswith("MemAvailable:"))
    except (FileNotFoundError, StopIteration):
        return float("inf")
    return kib / 1024 ** 2


def split_slots(budget: int, trials: dict[str, int], seconds: dict[str, float | None],
                named: dict[str, int]) -> dict[str, int]:
    """Sessions at once per setup. A named setup gets its own number; the rest share what is left of
    the budget in proportion to their expected agent time: trials times mean seconds per trial, or the
    other setups' mean for a setup with no history. Each setup gets at least one.

    Each setup is its own Harbor job, so a setup that finishes early leaves its slots idle; splitting
    by expected time makes the setups finish together.
    """
    rest = [name for name in trials if name not in named]
    known = [seconds[name] for name in rest if seconds.get(name)]
    fallback = sum(known) / len(known) if known else 1.0
    work = {name: trials[name] * (seconds.get(name) or fallback) for name in rest}
    total = sum(work.values()) or 1.0
    left = max(budget - sum(named.values()), len(rest))
    shares = {name: left * work[name] / total for name in rest}
    slots = {name: max(1, int(share)) for name, share in shares.items()}
    # Hand out what rounding down left over, largest remainder first.
    for name in sorted(rest, key=lambda n: shares[n] - int(shares[n]), reverse=True):
        if sum(slots.values()) >= left:
            break
        slots[name] += 1
    return {name: named[name] for name in trials if name in named} | slots


def mean_agent_seconds(results: Path, config_name: str, sample: int = 20) -> float | None:
    """Mean agent time per trial for the setup, from Harbor's result.json in the suite's newest runs
    until `sample` trials are counted: speeds change with the sandbox, harness and provider.

    Probe trials are left out: they are short by design and would understate a real case.
    """
    seconds = []
    for jobs in sorted(results.glob(f"*/jobs/{config_name}"), key=lambda p: p.stat().st_mtime, reverse=True):
        for path in jobs.glob("*/*/result.json"):
            if path.parent.name.startswith(f"{PROBE_CASE}--"):
                continue
            phase = json.loads(path.read_text()).get("agent_execution") or {}
            if phase.get("started_at") and phase.get("finished_at"):
                start, end = (datetime.fromisoformat(phase[k].replace("Z", "+00:00"))
                              for k in ("started_at", "finished_at"))
                seconds.append((end - start).total_seconds())
        if len(seconds) >= sample:
            break
    return sum(seconds) / len(seconds) if seconds else None


def first_line(path: Path) -> str:
    """The file's first non-empty line without heading marks: what the probe asks the agent to quote."""
    return next(line.strip().lstrip("#").strip() for line in path.read_text().splitlines() if line.strip())


def grade_trial(trial: Path, config_name: str, config: dict, artifact: dict, cases_root: Path,
                judges: list[str], specs_root: Path | None = None, probe_text: str | None = None) -> dict:
    """One row per trial: its status, evidence, and grader results.

    Workspaces come from the cases under `cases_root`, plus the instruction file a
    task delivered, found beside them in the run's tasks; graders.json comes from
    `specs_root` when given, otherwise from the same cases.
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
    case_dir = cases_root / case
    spec = load_spec((specs_root or cases_root) / case)
    evidence = EXTRACTORS[config["harness"]](trial / "agent")
    # The harness ended the run itself, as when a reply hit its output cap.
    if evidence.get("terminal_error"):
        row.update(status="infra_error", error=evidence["terminal_error"])
        return row
    final_message = evidence.pop("final_message") if evidence["complete"] else None
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
    run = {"final_message": final_message, "writes": evidence["writes"],
           "skills_loaded": evidence["skills_loaded"], "ops": ops}
    delivered = cases_root.parent / "tasks" / f"{case}--{variant}" / "environment" / "instructions"
    with temporary_initial_workspace(case_dir) as initial:
        if delivered.is_dir():
            shutil.copytree(delivered, initial, dirs_exist_ok=True)
        row["graders"] = run_graders(spec["graders"], arm(variant), workspace, initial, config["harness"], run,
                                     judges)
    return row


def grade(run_dir: Path, judges: list[str], graders_from_repo: bool = False) -> None:
    """Grade every trial from the run's archived cases; optionally with the repo's current graders.json."""
    load_dotenv(REPO / ".env")
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
                                      meta.get("probe_text")))
            graded[-1]["trial_path"] = trial.relative_to(run_dir).as_posix()
            if trial.relative_to(run_dir).parts[0] == "reused":
                graded[-1]["reused_from"] = sources.get(trial.name)
        rows += graded + missing_trials(meta, config_name, config, graded)
    # Judge calls batch across every setup in the run; verdicts are shared across the suite's runs.
    judge_pending(rows, judges, run_dir.parent / "judge-cache.jsonl")
    (run_dir / "grades.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    (run_dir / "report.md").write_text(report(run_dir))


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
    """Pass counts per case, configuration and variant; infra errors and undecided grades apart."""
    rows = [json.loads(line) for line in (run_dir / "grades.jsonl").read_text().splitlines()]
    cells = defaultdict(list)
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
                     + load + probe + f" | {grades}")
    lines += ["", "Cost reported by the harness (USD):"]
    lines += [f"- {config}: " + (f"{cost[config]:.4f}" if cost_known[config] else "not reported")
              for config in sorted({k[1] for k in cells})]
    if cached:
        lines += ["", f"Judge verdicts reused from earlier grading of the same output: {cached} of {verdicts}."]
    if collisions:
        lines += ["", "Same-named skill collisions:"] + [f"- {c}" for c in sorted(set(collisions))]
    if disagreements:
        lines += ["", "Judge disagreements:"] + [f"- {d}" for d in disagreements]
    return "\n".join(lines) + "\n"


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


def cmd_rules(args) -> None:
    """Per-rule pass counts from every graded run of the artifact's current text."""
    suite = load_suite(REPO, args.suite)
    rules = checked_rules(suite)
    current = artifact_digest(REPO / suite["artifact"]["path"])
    runs = []
    for meta_path in sorted((REPO / "evals" / args.suite / "results").glob("*/run.json")):
        meta, grades = json.loads(meta_path.read_text()), meta_path.parent / "grades.jsonl"
        digest = meta.get("artifact_digest") or meta.get("skill_digest")
        if grades.is_file() and (args.all_versions or digest == current):
            runs.append((meta, [json.loads(line) for line in grades.read_text().splitlines()]))
    untestable = sum(1 for r in rules.values() if r.get("untestable"))
    untested = sum(1 for r in rules.values() if not r["graders"]) - untestable
    print(f"{len(rules)} rules, {untested} without graders, {untestable} untestable from outputs; {len(runs)} runs of "
          + ("any artifact text" if args.all_versions else "the current artifact text") + ".\n")
    print(tabulate(rules, runs))


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
    run.add_argument("--case", action="append", help="case folder name; default all")
    run.add_argument("--variants", type=lambda s: s.split(","), default=["with", "without"])
    run.add_argument("--attempts", type=int, help="runs per task; default 1, or 3 with --minus")
    run.add_argument("--concurrency", action="append", default=[], metavar="[CONFIG=]N",
                     help="N: sessions at once across all setups, split by each setup's agent time in recent "
                          f"runs (default: up to {DEFAULT_SLOTS['bwrap']} under bwrap, as many as free memory holds; "
                          f"under Docker, per setup, {DEFAULT_SLOTS['docker']}); CONFIG=N fixes one setup's number. "
                          "A given number runs as given, with a warning when it will not fit in memory")
    run.add_argument("--env", choices=["bwrap", "docker"], default=DEFAULT_ENV,
                     help=f"where sessions run; default {DEFAULT_ENV}")
    run.add_argument("--probe", action="store_true",
                     help="add a case asking the agent to list its skills or quote its instruction file")
    run.add_argument("--judge", action="append")
    run.add_argument("--run-id")
    run.add_argument("--fresh-baseline", action="store_true",
                     help="rerun the arms not under test instead of reusing matching earlier trials")
    run.add_argument("--minus", metavar="RULE",
                     help="compare the full artifact with a copy lacking this rule from rules.json, on the rule's cases")
    regrade = sub.add_parser("grade")
    regrade.add_argument("run_dir", type=Path)
    regrade.add_argument("--judge", action="append")
    regrade.add_argument("--graders-from-repo", action="store_true",
                         help="grade with the repo's current graders.json instead of the run's copy")
    show = sub.add_parser("report")
    show.add_argument("run_dir", type=Path)
    table = sub.add_parser("rules")
    table.add_argument("suite", help="folder name under evals/")
    table.add_argument("--all-versions", action="store_true", help="include runs of earlier artifact text")
    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "rules":
        cmd_rules(args)
    elif args.command == "grade":
        grade(args.run_dir, args.judge or SETTINGS["judges"], args.graders_from_repo)
        print(report(args.run_dir))
    else:
        print(report(args.run_dir))


if __name__ == "__main__":
    main()
