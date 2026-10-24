#!/usr/bin/env python3
"""Evaluate agent instructions with and without them across agent harnesses and models, through Harbor.

Run from the root of the repository that holds the artifact and its `evals/<suite>/`.

  eval_instructions.py run <suite> [--config NAME]... [--case NAME]... [--attempts N] [--probe] [--fresh-baseline]
  eval_instructions.py run <suite> --minus RULE [--config NAME]...
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
graders test the rule; for a skill, both arms are told to use it. `rules` checks
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
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path.cwd()
sys.path.insert(0, str(HERE))

from evidence import EXTRACTORS  # noqa: E402
from graders import run_graders, temporary_initial_workspace  # noqa: E402
from rules import MINUS, arm, artifact_digest, check_rules, load_rules, minus_artifact, rule_cases, tabulate  # noqa: E402
from tasks import PROBE_CASE, artifact_root, build_tasks, load_spec, load_suite, task_digest  # noqa: E402

SETTINGS = json.loads((HERE / "configs.json").read_text())
DEFAULT_CONFIGS = ["openclaw-deepseek-high"]
# Each harness ships skills of its own, such as Claude Code's code-review and the
# skill-creator in Codex and OpenClaw. They compete with the skill under test and
# can share its name, so they are off unless a configuration sets builtin_skills;
# OpenClaw's switch lives in openclaw_model_config.
BLOCK_BUILTIN_SKILLS = {
    # doctor and plugin-authoring survive the bundled switch, so they are turned off by name.
    "claude-code": ["--ae", "CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1",
                    "--ak", 'config={"skillOverrides": {"doctor": "off", "plugin-authoring": "off"}}'],
    "codex": ["--ak", 'config={"skills": {"bundled": {"enabled": false}}}'],
}
# Names the installed copy by path: a harness may ship a built-in skill with the same name.
USE_SKILL = "Use the skill at /skills/{skill}/SKILL.md for this task.\n\n"
HARBOR_AGENT = {"claude-code": "claude-code", "codex": "codex", "openclaw": "harbor_agents:PreinstalledOpenClaw"}


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines into the environment without overriding variables already set."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value.strip().strip('"').strip("'"))


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

    For OpenRouter it also pins the upstream provider with no fallbacks, and
    declares the one supported effort so OpenClaw sends it as `reasoning.effort`
    verbatim. Without that, the levels stop at high plus OpenClaw's own `ultra`
    (sent as max), there is no xhigh, and some models get medium sent as low.
    """
    provider, model_id = config["model"].split("/", 1)
    entry = {"id": model_id, "name": model_id, "reasoning": True, "contextWindow": config["context_window"]}
    if provider == "openrouter":
        effort = config["effort"]
        entry["compat"] = {"supportsReasoningEffort": True, "supportedReasoningEfforts": [effort]} if effort else \
            {"supportsReasoningEffort": False}
        entry["params"] = {"provider": {"order": [config["openrouter_provider"]], "allow_fallbacks": False}}
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


def agent_args(config: dict) -> list[str]:
    """Harbor arguments that decide how the agent runs, as opposed to where results go."""
    harness = config["harness"]
    args = ["-a", HARBOR_AGENT[harness], "-m", config["model"],
            "--ak", f"version={SETTINGS['cli_versions'][harness]}",
            # The OpenClaw adapter reads its config from a bind-mounted /logs/agent.
            "--ek", "auto_mounting=true"]
    if config.get("effort"):
        args += ["--ak", f"reasoning_effort={config['effort']}"]
    if harness == "openclaw":
        args += ["--ak", f"openclaw_config={openclaw_model_config(config)}"]
    elif not config.get("builtin_skills"):
        args += BLOCK_BUILTIN_SKILLS[harness]
    return args


def harbor_command(config: dict, tasks_dir: Path, jobs_dir: Path, job: str, attempts: int, concurrency: int,
                   exclude: list[str] = ()) -> list[str]:
    cmd = ["uv", "tool", "run", "--python", "3.12", "--from", f"harbor @ {SETTINGS['harbor']}", "harbor", "run",
           "-p", str(tasks_dir), *agent_args(config),
           "-k", str(attempts), "-n", str(concurrency), "-o", str(jobs_dir), "--job-name", job, "-y", "-q"]
    for task in exclude:
        cmd += ["-x", task, "-x", f"*/{task}"]
    return cmd


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
                found.append(prior / "jobs" / row["config"] / row["trial"])
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


def cmd_run(args) -> None:
    load_dotenv(REPO / ".env")
    configs = args.config or DEFAULT_CONFIGS
    unknown = set(configs) - set(SETTINGS["configs"])
    if unknown:
        raise SystemExit(f"unknown configs: {sorted(unknown)}")
    check_credentials(configs)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = REPO / "evals" / args.suite / "results" / run_id
    if run_dir.exists():
        raise SystemExit(f"{run_dir} exists")
    suite = load_suite(REPO, args.suite)
    artifact, full = suite["artifact"], REPO / suite["artifact"]["path"]
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
    image = base_image()
    tasks = build_tasks(REPO, suite, cases, variants, image, run_dir / "tasks", sources, preamble)
    archive_cases(args.suite, cases, run_dir / "cases")
    reused = {} if args.fresh_baseline else reuse_baselines(run_dir, configs, tasks, attempts, under_test)
    meta = {"suite": args.suite, "artifact": artifact, "artifact_digest": artifact_digest(full),
            "probe_text": first_line(full) if artifact["type"] == "instruction-file" else None,
            "minus": args.minus, "preamble": preamble,
            "configs": {c: SETTINGS["configs"][c] for c in configs},
            "cases": [c.name for c in cases], "variants": variants, "attempts": attempts,
            "harbor": SETTINGS["harbor"], "cli_versions": SETTINGS["cli_versions"], "base_image": image,
            "agent_args": {c: agent_args(SETTINGS["configs"][c]) for c in configs},
            "tasks": tasks, "reused": reused, "started_at": datetime.now(timezone.utc).isoformat()}
    (run_dir / "run.json").write_text(json.dumps(meta, indent=2) + "\n")
    for name in configs:
        config = SETTINGS["configs"][name]
        skip = sorted(reused.get(name, {}))
        if len(skip) == len(tasks):
            print(f"== {name}: every task reused", file=sys.stderr)
            continue
        env = dict(os.environ, PYTHONPATH=str(HERE))
        env.update({k: os.path.expandvars(v) for k, v in config.get("env", {}).items()})
        wait_for_docker()
        print(f"== {name}", file=sys.stderr)
        with open(run_dir / f"harbor-{name}.log", "w") as log:
            subprocess.run(harbor_command(config, run_dir / "tasks", run_dir / "jobs", name,
                                          attempts, args.concurrency, skip),
                           env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
    grade(run_dir, args.judge or SETTINGS["judges"])
    print(report(run_dir))


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
    final_message = evidence.pop("final_message") if evidence["complete"] else None
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
        # The harness puts an instruction file in context itself, so no transcript shows a load.
        row.update(skill_loaded=None, delivered=variant != "without")
        marker = probe_text
    if spec.get("probe"):
        row["probe_sees_artifact"] = None if final_message is None or not marker else marker in final_message
    run = {"final_message": final_message, "writes": evidence["writes"]}
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
    # Each row is written as soon as it is graded, so an interrupted grading keeps finished judge calls.
    with open(run_dir / "grades.jsonl", "w") as out:
        for config_name, config in meta["configs"].items():
            sources = {Path(src).name: src for srcs in meta.get("reused", {}).get(config_name, {}).values()
                       for src in srcs}
            trials = [t for job in (run_dir / "jobs" / config_name, run_dir / "reused" / config_name)
                      if job.is_dir() for t in sorted(job.iterdir()) if (t / "config.json").is_file()]
            graded = []
            for trial in trials:
                graded.append(grade_trial(trial, config_name, config, artifact, cases_root, judges, specs_root,
                                          meta.get("probe_text")))
                if trial.parent.parent.name == "reused":
                    graded[-1]["reused_from"] = sources.get(trial.name)
                out.write(json.dumps(graded[-1]) + "\n")
                out.flush()
            for row in missing_trials(meta, config_name, config, graded):
                out.write(json.dumps(row) + "\n")
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
                verdicts = {m: v["pass"] for m, v in g.get("judges", {}).items()}
                if len(set(verdicts.values())) > 1:
                    disagreements.append(f"{case} / {config} / {variant} / {name}: {verdicts}")
        grades = ", ".join(f"{n} {p}/{p + f}" + (f" ({u} undecided)" if u else "")
                           for n, (p, f, u) in grader_counts.items())
        probe = ""
        if ok and "probe_sees_artifact" in ok[0]:
            probe = f" | visible {sum(1 for t in ok if t['probe_sees_artifact'])}/{len(ok)}"
        if ok and "delivered" in ok[0]:
            load = " | instruction file " + ("delivered" if ok[0]["delivered"] else "absent")
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
    untested = sum(1 for r in rules.values() if not r["graders"])
    print(f"{len(rules)} rules, {untested} without graders; {len(runs)} runs of "
          + ("any artifact text" if args.all_versions else "the current artifact text") + ".\n")
    print(tabulate(rules, runs))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("suite", help="folder name under evals/")
    run.add_argument("--config", action="append", help=f"from configs.json; default {DEFAULT_CONFIGS}")
    run.add_argument("--case", action="append", help="case folder name; default all")
    run.add_argument("--variants", type=lambda s: s.split(","), default=["with", "without"])
    run.add_argument("--attempts", type=int, help="runs per task; default 1, or 3 with --minus")
    run.add_argument("--concurrency", type=int, default=2)
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
