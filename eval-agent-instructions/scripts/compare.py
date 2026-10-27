"""Compare a candidate version of the instructions with a baseline, from the with arms of graded runs.

Per setup it reports, on the cases both versions ran: each acceptance grader's pass
count in both, every case whose total dropped, the work each run took, and, when asked,
a blinded pairwise judgment of whole outputs. Acceptance graders are those the case's
current graders.json does not mark `diagnostic`, excluding process checks (`read`,
`skills_loaded`), which show how the agent worked rather than what it delivered.
Regrade both sides with --graders-from-repo first, so they are judged by the same graders.
"""
import difflib
import json
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import median

from evidence import input_tokens, output_tokens
from graders import HARNESS_FILES, JUDGE_WORKERS, _file_hashes, complete, temporary_initial_workspace

PROCESS_GRADERS = {"read", "skills_loaded"}
# Characters of changed files shown to the pairwise judge per output.
DIFF_CHARS = 40_000
PAIRWISE_PROMPT = (
    "Two AI agents each got the same request in the same workspace. Compare what each delivered: its changes "
    "to the files and its final message. Decide which better serves the user who sent the request: correct, "
    "complete, within the scope asked, no needless work, faithful to the files. Length is not a merit. If "
    "neither is clearly better, say tie.\n\nRequest:\n<<<\n{request}\n>>>\n\nOutput A:\n<<<\n{a}\n>>>\n\n"
    'Output B:\n<<<\n{b}\n>>>\n\nReply with JSON only: {{"better": "A" | "B" | "tie", "reason": "<one or two sentences>"}}'
)


def work(rows: list[dict]) -> dict[str, float]:
    """Median agent seconds, tool calls, and input and output tokens over the rows that report each."""
    values = {"seconds": [r.get("agent_seconds") for r in rows],
              "calls": [r["evidence"].get("tool_calls") for r in rows],
              "input": [input_tokens(r["evidence"].get("usage")) for r in rows],
              "output": [output_tokens(r["evidence"].get("usage")) for r in rows]}
    return {key: median(known) for key, v in values.items() if (known := [x for x in v if x is not None])}


def describe_work(m: dict[str, float]) -> str:
    parts = [f"{m['seconds']:.0f}s" if "seconds" in m else "", f"{m['calls']:.0f} calls" if "calls" in m else "",
             f"in {m['input'] / 1000:.0f}k" if "input" in m else "", f"out {m['output'] / 1000:.1f}k" if "output" in m else ""]
    return " ".join(p for p in parts if p)


def with_rows(run_dirs: list[Path]) -> list[dict]:
    """Graded with-arm rows of the runs, each trial once even when a later run reused it; each row
    remembers its run folder."""
    rows, seen = [], set()
    for run_dir in run_dirs:
        for line in (run_dir / "grades.jsonl").read_text().splitlines():
            row = json.loads(line)
            if row["status"] != "ok" or row["variant"] != "with":
                continue
            key = row.get("reused_from") or f"{run_dir.name}/{row.get('trial_path')}"
            if key not in seen:
                seen.add(key)
                rows.append(row | {"run_dir": str(run_dir)})
    return rows


def acceptance_graders(suite_dir: Path, case: str) -> set[str]:
    path = suite_dir / case / "graders.json"
    if not path.is_file():
        return set()
    return {g["name"] for g in json.loads(path.read_text())["graders"]
            if not g.get("diagnostic") and g["type"] not in PROCESS_GRADERS}


def compare_graders(base: list[dict], cand: list[dict], suite_dir: Path) -> dict:
    """Per setup: pass counts per (case, acceptance grader) on both sides, over cases both sides ran."""
    counts = defaultdict(lambda: [0, 0, 0, 0])  # (config, case, grader) -> base passed, graded, cand passed, graded
    cases = {side: defaultdict(set) for side in ("base", "cand")}
    for side, rows in (("base", base), ("cand", cand)):
        offset = 0 if side == "base" else 2
        for row in rows:
            cases[side][row["config"]].add(row["case"])
            keep = acceptance_graders(suite_dir, row["case"])
            for name, g in (row.get("graders") or {}).items():
                if name in keep and g["pass"] is not None:
                    cell = counts[(row["config"], row["case"], name)]
                    cell[offset] += g["pass"]
                    cell[offset + 1] += 1
    result = {}
    for config in sorted(set(cases["base"]) | set(cases["cand"])):
        shared = cases["base"][config] & cases["cand"][config]
        cells = {(case, name): c for (cfg, case, name), c in counts.items()
                 if cfg == config and case in shared and c[1] and c[3]}
        result[config] = {"shared": sorted(shared),
                          "only_base": sorted(cases["base"][config] - shared),
                          "only_cand": sorted(cases["cand"][config] - shared),
                          "cells": cells}
    return result


def output_text(row: dict) -> str:
    """What a run delivered: a diff of every file it changed, then its final message."""
    run_dir = Path(row["run_dir"])
    workspace = run_dir / row["trial_path"] / "verifier" / "workspace"
    ignored = HARNESS_FILES.get(row["harness"], set())
    parts = []
    with temporary_initial_workspace(run_dir / "cases" / row["case"]) as initial:
        before, after = _file_hashes(initial), _file_hashes(workspace)
        for name in sorted(set(before) | set(after)):
            if before.get(name) == after.get(name) or name.split("/", 1)[0] in ignored:
                continue
            old = (initial / name).read_text(errors="replace").splitlines() if name in before else []
            new = (workspace / name).read_text(errors="replace").splitlines() if name in after else []
            parts.append("\n".join(difflib.unified_diff(old, new, f"a/{name}", f"b/{name}", lineterm="")))
    diff = "\n".join(parts) or "(no files changed)"
    if len(diff) > DIFF_CHARS:
        diff = diff[:DIFF_CHARS] + "\n(diff truncated)"
    return f"{diff}\n\nFinal message:\n{row.get('final_message') or '(none)'}"


def pairwise(base: list[dict], cand: list[dict], judge: str, seed: int = 0) -> list[dict]:
    """One blinded judgment per pair of runs on the same case and setup; A and B are assigned at random."""
    rng = random.Random(seed)
    groups = defaultdict(lambda: ([], []))
    for side, rows in ((0, base), (1, cand)):
        for row in rows:
            groups[(row["config"], row["case"])][side].append(row)
    pairs = []
    for (config, case), (b, c) in sorted(groups.items()):
        rng.shuffle(b)
        rng.shuffle(c)
        for base_row, cand_row in zip(b, c):
            pairs.append({"config": config, "case": case, "base": base_row, "cand": cand_row,
                          "cand_is_a": rng.random() < 0.5})

    def decide(pair: dict) -> dict:
        request = (Path(pair["cand"]["run_dir"]) / "cases" / pair["case"] / "instruction.md").read_text()
        a, b = (pair["cand"], pair["base"]) if pair["cand_is_a"] else (pair["base"], pair["cand"])
        try:
            text, _ = complete(judge, PAIRWISE_PROMPT.format(request=request, a=output_text(a), b=output_text(b)))
            reply = json.loads(text[text.index("{"):text.rindex("}") + 1])
            better = {"A": "cand" if pair["cand_is_a"] else "base", "B": "base" if pair["cand_is_a"] else "cand",
                      "tie": "tie"}.get(reply.get("better"))
            reason = str(reply.get("reason", ""))
        except (OSError, ValueError) as exc:
            better, reason = None, f"judge call failed: {exc}"
        return {"config": pair["config"], "case": pair["case"], "better": better, "reason": reason}

    with ThreadPoolExecutor(JUDGE_WORKERS) as pool:
        return list(pool.map(decide, pairs))


def compare(base_runs: list[Path], cand_runs: list[Path], suite_dir: Path, judge: str | None = None,
            cases: list[str] | None = None) -> str:
    """The comparison as Markdown, over `cases` or every case; `judge` adds the blinded pairwise judgment."""
    base, cand = with_rows(base_runs), with_rows(cand_runs)
    if cases:
        base, cand = [r for r in base if r["case"] in cases], [r for r in cand if r["case"] in cases]
    graded = compare_graders(base, cand, suite_dir)
    lines = [f"# Candidate {', '.join(r.name for r in cand_runs)} against baseline {', '.join(r.name for r in base_runs)}",
             "", "With arms only; acceptance graders only (diagnostics and process checks left out)."]
    judged = pairwise(base, cand, judge) if judge else []
    for config, g in graded.items():
        cells = g["cells"]
        totals = [sum(c[i] for c in cells.values()) for i in range(4)]
        lines += ["", f"## {config}", "",
                  f"- Cases both ran: {len(g['shared'])}"
                  + (f"; baseline only: {', '.join(g['only_base'])}" if g["only_base"] else "")
                  + (f"; candidate only: {', '.join(g['only_cand'])}" if g["only_cand"] else ""),
                  f"- Acceptance grades passed: baseline {totals[0]}/{totals[1]}, candidate {totals[2]}/{totals[3]}"]
        # Each case counts once, so a case run more often on one side does not shift that side's median.
        per_side = [{case: work([r for r in rows if r["config"] == config and r["case"] == case])
                     for case in g["shared"]} for rows in (base, cand)]
        for side, by_case in zip(("baseline", "candidate"), per_side):
            lines.append(f"- Median work over cases, {side}: " + describe_work(
                {k: median(v) for k in ("seconds", "calls", "input", "output")
                 if (v := [m[k] for m in by_case.values() if k in m])}))
        changes = [per_side[1][c]["input"] - per_side[0][c]["input"] for c in g["shared"]
                   if "input" in per_side[0][c] and "input" in per_side[1][c]]
        if changes:
            lines.append(f"- Median change in input per case: {median(changes) / 1000:+.0f}k "
                         f"({sum(x < 0 for x in changes)} of {len(changes)} cases lower)")
        per_case = defaultdict(lambda: [0, 0, 0, 0])
        for (case, _), c in cells.items():
            per_case[case] = [x + y for x, y in zip(per_case[case], c)]
        dropped = sorted((c[2] / c[3] - c[0] / c[1], case, c) for case, c in per_case.items() if c[2] / c[3] < c[0] / c[1])
        if dropped:
            lines += ["", "Cases whose pass rate dropped:"]
            lines += [f"- {case}: {c[0]}/{c[1]} -> {c[2]}/{c[3]}" for _, case, c in dropped]
        drops = sorted((c[2] / c[3] - c[0] / c[1], case, name, c) for (case, name), c in cells.items()
                       if c[2] / c[3] < c[0] / c[1])
        gains = [k for k, c in cells.items() if c[2] / c[3] > c[0] / c[1]]
        if drops:
            lines += ["", f"Graders that dropped ({len(drops)}; {len(gains)} rose):"]
            lines += [f"- {case}/{name}: {c[0]}/{c[1]} -> {c[2]}/{c[3]}" for _, case, name, c in drops]
        verdicts = [v for v in judged if v["config"] == config]
        if verdicts:
            tally = {k: sum(1 for v in verdicts if v["better"] == k) for k in ("cand", "base", "tie", None)}
            lines += ["", f"Blinded pairwise judgment by {judge}: candidate better {tally['cand']}, baseline better "
                          f"{tally['base']}, tie {tally['tie']}" + (f", undecided {tally[None]}" if tally[None] else "")]
            lines += [f"- {v['case']}: baseline better: {v['reason']}" for v in verdicts if v["better"] == "base"]
    return "\n".join(lines) + "\n"
