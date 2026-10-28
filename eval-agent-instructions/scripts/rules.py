"""Map an artifact's rules to the graders that test them, build minus-one-rule copies, and tabulate results.

`evals/<suite>/rules.json`:

    {"rules": {"<rule>": {"file": "SKILL.md", "text": "<exact text>" | ["<text>", ...],
                          "graders": ["<case>/<grader>", ...]}}}

`file` is relative to the skill folder, or is the instruction file's own name.
Each text must occur exactly once in its file; deleting every text of a rule
gives that rule's minus variant. A rule with no graders is listed as untested.
"""
import hashlib
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from statistics import median

from evidence import input_tokens

MINUS = "minus-"
RULE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def arm(variant: str) -> str:
    """The arm a variant stands for in expectations and grader filters: a minus variant is a with run."""
    return "with" if variant.startswith(MINUS) else variant


def load_rules(suite_dir: Path) -> dict:
    path = suite_dir / "rules.json"
    if not path.is_file():
        raise SystemExit(f"{path} does not exist")
    rules = json.loads(path.read_text())["rules"]
    for rule in rules.values():
        if isinstance(rule["text"], str):
            rule["text"] = [rule["text"]]
    return rules


def check_rules(rules: dict, root: Path, cases_root: Path) -> list[str]:
    """Problems that would make a minus variant or a grader reference wrong; empty when the map is sound."""
    problems = []
    for name, rule in rules.items():
        if not RULE_NAME.match(name):
            problems.append(f"{name}: rule names are lowercase kebab-case")
        source = root / rule["file"]
        content = source.read_text() if source.is_file() else None
        if content is None:
            problems.append(f"{name}: {rule['file']} does not exist")
        for text in rule["text"] if content is not None else []:
            count = content.count(text)
            if count != 1:
                problems.append(f"{name}: text occurs {count} times in {rule['file']}: {text[:60]!r}")
            elif not _whole_sentences(content, text):
                problems.append(f"{name}: text is not whole sentences, so removing it leaves a fragment: {text[:60]!r}")
        spans = sorted((content.find(text), content.find(text) + len(text)) for text in rule["text"]) if content else []
        if any(a_end > b_start for (_, a_end), (b_start, _) in zip(spans, spans[1:])):
            problems.append(f"{name}: two of its passages overlap, so one cannot be removed after the other")
        elif content and all(content.count(text) == 1 for text in rule["text"]):
            removed, expected = content, content
            for text in rule["text"]:
                removed, expected = remove_text(removed, text), expected.replace(text, " ", 1)
            if _words(removed) != _words(expected):
                problems.append(f"{name}: removing its text changes more than its words")
        for ref in rule["graders"]:
            case, _, grader = ref.partition("/")
            spec = cases_root / case / "graders.json"
            names = {g["name"] for g in json.loads(spec.read_text())["graders"]} if spec.is_file() else set()
            if grader not in names:
                problems.append(f"{name}: no grader {ref}")
    # Cumulative removal deletes one rule's text after another's, so no text may contain another rule's.
    texts = [(name, rule["file"], text) for name, rule in rules.items() for text in rule["text"]]
    for name, file, text in texts:
        for other, other_file, other_text in texts:
            if other != name and file == other_file and other_text in text:
                problems.append(f"{name}: its text contains {other}'s text, so the two cannot both be removed")
    for name, rule in rules.items():
        if rule.get("untestable") and rule["graders"]:
            problems.append(f"{name}: marked untestable but has graders")
    return problems


def _whole_sentences(content: str, text: str) -> bool:
    """Text starts where a line, list item or sentence starts, and ends a sentence or line."""
    start = content.index(text)
    before, after = content[:start], content[start + len(text):]
    starts = before == "" or re.search(r"(\n|^)\s*([-*]|\d+\.)?\s*$|[.!?:] $", before) is not None
    ends = text.rstrip()[-1:] in (".", "!", "?", ":") or after[:1] in ("", "\n")
    return starts and ends


def remove_text(content: str, text: str) -> str:
    """Delete one occurrence of text, then the space or list item it leaves empty."""
    start = content.index(text)
    before, after = content[:start], content[start + len(text):]
    if before.endswith(" ") and after[:1] in (" ", "\n", ""):
        before = before[:-1]
    elif after.startswith(" ") and (before == "" or before.endswith("\n") or before.endswith("- ")):
        after = after[1:]
    line_start = before.rfind("\n") + 1
    line_end = after.find("\n")
    line = before[line_start:] + after[:line_end if line_end != -1 else len(after)]
    if line.strip() in ("", "-", "*") or re.fullmatch(r"\s*\d+\.\s*", line):
        before = before[:line_start]
        after = after[line_end + 1:] if line_end != -1 else ""
    return before + after


def minus_artifact(source: Path, rule: dict, dest: Path) -> None:
    """Copy a skill folder or instruction file with only this rule's text removed; nothing else differs."""
    if source.is_dir():
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns("evals"))
        target = dest / rule["file"]
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, dest)
        target = dest
    content = target.read_text()
    expected = content
    for text in rule["text"]:
        content = remove_text(content, text)
        expected = expected.replace(text, " ", 1)
    if _words(content) != _words(expected):
        raise SystemExit(f"removing {rule['text']!r} changed more than its words")
    target.write_text(content)


def _words(text: str) -> list[str]:
    """Words other than list markers, which removing a whole item also drops."""
    return [w for w in text.split() if w not in ("-", "*") and not re.fullmatch(r"\d+\.", w)]


def artifact_digest(source: Path) -> str:
    """Hash of a skill folder's files, or of an instruction file."""
    if source.is_file():
        return hashlib.sha256(source.read_bytes()).hexdigest()
    h = hashlib.sha256()
    for path in sorted(p for p in source.rglob("*") if p.is_file() and "evals" not in p.parts):
        h.update(path.relative_to(source).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def rule_cases(rules: dict, rule: str) -> list[str]:
    return sorted({ref.split("/", 1)[0] for ref in rules[rule]["graders"]})


# Marks a setup label whose runs used an earlier config under the setup's name.
EARLIER = " (earlier config "


def tabulate(rules: dict, runs: list[tuple[dict, list[dict]]]) -> str:
    """Per rule and configuration, pass counts of the rule's graders in each arm, with a status.

    `runs` holds (run.json, grade rows) for runs of the current artifact text only.
    Configurations are never pooled. A reused row repeats its original and is
    skipped; a with or minus run that never loaded a skill artifact tests
    triggering, not the text, so it is counted apart; undecided grades are left out.
    A --minus run's full-artifact arm goes in its own `full` column, since those runs
    may be told to use the skill and the plain with runs are not.
    """
    columns = ("with", "without", "full", "minus")
    counts = defaultdict(lambda: [0, 0])  # (rule, config, column) -> [passed, graded]
    trials = defaultdict(set)  # (rule, config, column, case) -> trials that contributed
    unloaded = defaultdict(set)  # (rule, config) -> with or minus trials that never loaded a skill artifact
    configs = set()
    for meta, rows in runs:
        for row in rows:
            if row.get("status") != "ok" or row.get("reused_from"):
                continue
            column = "minus" if row["variant"].startswith(MINUS) else row["variant"]
            if column == "with" and meta.get("minus"):
                column = "full"
            for name, rule in rules.items():
                if column == "minus" and row["variant"] != MINUS + name:
                    continue
                refs = [ref.partition("/")[2] for ref in rule["graders"] if ref.partition("/")[0] == row["case"]]
                if not refs:
                    continue
                configs.add(row["config"])
                if column != "without" and not (row.get("skill_loaded") or row.get("delivered")):
                    unloaded[(name, row["config"])].add(row["trial"])
                    continue
                for grader in refs:
                    result = row["graders"].get(grader)
                    if result is None or result.get("pass") is None:
                        continue
                    counts[(name, row["config"], column)][0] += bool(result["pass"])
                    counts[(name, row["config"], column)][1] += 1
                    trials[(name, row["config"], column, row["case"])].add(row["trial"])
    lines = ["| rule | config | with | without | full | minus | not loaded | status |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    weakest = []
    for name, rule in rules.items():
        if not rule["graders"]:
            lines.append(f"| {name} | | | | | | | "
                         f"{'untestable from outputs: ' + rule['untestable'] if rule.get('untestable') else 'untested: no grader'} |")
            continue
        tested = [c for c in sorted(configs)
                  if any(counts[(name, c, col)][1] for col in columns) or unloaded[(name, c)]]
        if not tested:
            lines.append(f"| {name} | | | | | | | no runs yet |")
        cases = sorted({ref.split("/", 1)[0] for ref in rule["graders"]})
        statuses = {}
        for config in tested:
            cells = {col: counts[(name, config, col)] for col in columns}
            fewest = {col: min(len(trials[(name, config, col, case)]) for case in cases) for col in columns}
            shown = {col: f"{p}/{t}" if t else "" for col, (p, t) in cells.items()}
            statuses[config] = status(cells, fewest)
            lines.append(f"| {name} | {config} | {shown['with']} | {shown['without']} | {shown['full']} | "
                         f"{shown['minus']} | "
                         f"{len(unloaded[(name, config)]) or ''} | {statuses[config]} |")
        # A run under an earlier config of a setup shows in the table but no longer speaks for the setup.
        current = {c: v for c, v in statuses.items() if EARLIER not in c}
        if current:
            weakest.append(f"| {name} | {across_setups(current)} |")
    lines += ["", "Each rule by its weakest setup: a candidate only when every setup run is one.", "",
              "| rule | across setups |", "| --- | --- |"] + weakest
    return "\n".join(lines) + "\n"


def across_setups(statuses: dict[str, str]) -> str:
    """One rule's verdict from its per-setup statuses: the setup that needs it, or that shows a problem, decides."""
    def where(test):
        return ", ".join(sorted(c for c, s in statuses.items() if test(s)))
    if worse := where(lambda s: "did worse" in s or s.startswith("removal did worse")):
        return f"check: the artifact did worse on {worse}"
    if needed := where(lambda s: "helps" in s):
        short = any("fewer than 3" in s for s in statuses.values() if "helps" in s)
        return f"keep: helps on {needed}" + (", in fewer than 3 runs per arm" if short else "")
    if failing := where(lambda s: s.startswith("graders fail")):
        return f"check the wording or grader: graders fail in both arms on {failing}"
    if all(s.startswith("candidate") or s == "removal matched the full artifact" for s in statuses.values()):
        return f"candidate on every setup run ({len(statuses)}): no case shows its effect"
    return "undecided: " + "; ".join(f"{c}: {s}" for c, s in sorted(statuses.items()))


def min_set(rules: dict, runs: list[tuple[dict, list[dict]]], acceptance: dict[str, set[str]],
            setups: set[str] | None = None, gaps: bool = False) -> dict:
    """The cheapest cases in `acceptance` (case -> its acceptance graders) that still cover every mapped
    rule a case there tests, and with `gaps` every gap: an acceptance grader the current text fails in most
    with runs on some setup in `setups` (default every setup), which only its own case can show. Cost is a case's median input tokens per with run, summed
    over setups. Greedy cover by units per token, then any case whose units others cover is dropped,
    costliest first. `runs` holds runs of the current text, as `tabulate` takes them.
    """
    units = {case: {("rule", name) for name, rule in rules.items()
                    for ref in rule["graders"] if ref.partition("/")[0] == case} for case in acceptance}
    passes = defaultdict(lambda: [0, 0])  # (case, grader, config) -> [passed, graded]
    tokens = defaultdict(list)  # (case, config) -> input tokens per with run
    for meta, rows in runs:
        for row in rows:
            if (row.get("status") != "ok" or row.get("reused_from") or row["variant"] != "with"
                    or row["case"] not in acceptance or not (row.get("skill_loaded") or row.get("delivered"))
                    or (setups is not None and row["config"] not in setups)):
                continue
            if (used := input_tokens(row["evidence"].get("usage"))) is not None:
                tokens[(row["case"], row["config"])].append(used)
            for grader, result in row["graders"].items():
                if grader in acceptance[row["case"]] and result.get("pass") is not None:
                    passes[(row["case"], grader, row["config"])][0] += bool(result["pass"])
                    passes[(row["case"], grader, row["config"])][1] += 1
    for (case, grader, _), (passed, graded) in passes.items():
        if gaps and passed < graded / 2:
            units[case].add(("gap", case, grader))
    cost = defaultdict(float)
    for (case, _), used in tokens.items():
        cost[case] += median(used)
    known = [c for c in cost.values() if c]
    default = median(known) if known else 1.0
    cost = {case: cost.get(case) or default for case in acceptance}
    wanted, kept = set().union(*units.values()) if units else set(), []
    while wanted:
        best = max((c for c in acceptance if c not in kept), key=lambda c: (len(units[c] & wanted) / cost[c], -cost[c]))
        kept.append(best)
        wanted -= units[best]
    for case in sorted(kept, key=lambda c: -cost[c]):
        others = set().union(*(units[c] for c in kept if c != case))
        if units[case] <= others:
            kept.remove(case)
    mapped = {name for name, rule in rules.items() if rule["graders"]}
    covered = {u[1] for c in acceptance for u in units[c] if u[0] == "rule"}
    return {"kept": sorted(kept), "dropped": sorted(set(acceptance) - set(kept)), "cost": cost,
            "units": units, "rules_outside": sorted(mapped - covered)}


def status(cells: dict, fewest: dict) -> str:
    """`cells` holds [passed, graded] per column; `fewest` the fewest runs any of the rule's cases has per column."""
    rate = {col: p / t if t else None for col, (p, t) in cells.items()}
    if rate["minus"] is not None and rate["full"] is not None:
        if fewest["minus"] < 3 or fewest["full"] < 3:
            return "removal: fewer than 3 runs per arm on some case"
        return "removal matched the full artifact" if rate["minus"] >= rate["full"] else "removal did worse"
    if rate["with"] is None or rate["without"] is None:
        return "needs with and without runs"
    if rate["with"] == rate["without"]:
        # Failing in both arms says the text is not followed or the grader is wrong, not that the rule is a no-op.
        return "candidate: no difference" if rate["with"] == 1 else "graders fail in both arms: check the wording or grader"
    verdict = "keep: the artifact helps" if rate["with"] > rate["without"] else "the artifact did worse"
    if min(fewest["with"], fewest["without"]) < 3:
        return verdict.removeprefix("keep: ") + ", in fewer than 3 runs per arm"
    return verdict
