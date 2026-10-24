"""Grader types, run on the host against a trial's saved workspace and final message.

Grader specs come from a case's graders.json. Each returns {"pass": bool | None,
"detail": str}; None means the grader could not decide, such as a failed or
malformed judge reply or a transcript that ended early, and is reported apart
from a failure. `run` is the trial's evidence: its final message and the files
it wrote, each None when the transcript is incomplete.
"""
import contextlib
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

# Files a harness writes into the workspace on its own. They are ignored unless the
# initial workspace already had them; `.git` is ignored everywhere, since commits are
# not file content.
HARNESS_FILES = {
    "openclaw": {"AGENTS.md", "BOOTSTRAP.md", "IDENTITY.md", "SOUL.md", "USER.md", "TOOLS.md",
                 "HEARTBEAT.md", "MEMORY.md", ".openclaw"},
}

# The agent's working directory inside the task container.
WORKSPACE = "/app"

_REGEX_FLAGS = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}


def initial_workspace(case_dir: Path, dest: Path) -> Path:
    """Recreate the workspace the agent started from, the way the task image builds it."""
    dest.mkdir(parents=True, exist_ok=True)
    if (case_dir / "scaffold.sh").is_file():
        subprocess.run(["bash", str((case_dir / "scaffold.sh").resolve())], cwd=dest, check=True,
                       capture_output=True)
    elif (case_dir / "fixture").is_dir():
        shutil.copytree(case_dir / "fixture", dest, dirs_exist_ok=True)
    return dest


def _file_hashes(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts}


_UNDECIDED_NO_TRANSCRIPT = {"pass": None, "detail": "transcript incomplete"}


def _file_text(workspace: Path, rel: str) -> str | None:
    path = workspace / rel
    return path.read_text(errors="replace") if path.is_file() else None


def regex(spec, workspace, initial, harness, run, judges):
    if spec.get("path"):
        text = _file_text(workspace, spec["path"])
        if text is None:
            return {"pass": False, "detail": f"{spec['path']} missing"}
    elif run["final_message"] is None:
        return _UNDECIDED_NO_TRANSCRIPT
    else:
        text = run["final_message"]
    flags = 0
    for f in spec.get("flags", ""):
        flags |= _REGEX_FLAGS[f]
    found = re.search(spec["pattern"], text, flags) is not None
    wanted = spec.get("match", "contains") == "contains"
    return {"pass": found == wanted, "detail": "" if found == wanted else f"pattern {'not ' if wanted else ''}found"}


def file_exists(spec, workspace, initial, harness, run, judges):
    exists = (workspace / spec["path"]).exists()
    return {"pass": exists == spec.get("exists", True), "detail": ""}


def unchanged_except(spec, workspace, initial, harness, run, judges):
    before, after = _file_hashes(initial), _file_hashes(workspace)
    allowed = set(spec.get("allow", []))
    ignored = HARNESS_FILES.get(harness, set())
    changed = sorted(p for p in before if p not in allowed and after.get(p) != before[p])
    added = sorted(p for p in after if p not in before and p not in allowed
                   and p.split("/", 1)[0] not in ignored)
    ok = not changed and not added
    return {"pass": ok, "detail": "" if ok else f"changed {changed} added {added}"}


def no_writes(spec, workspace, initial, harness, run, judges):
    """The transcript shows no writes through file-editing tools, even ones later undone.

    Shell commands that write files are not recognized here; unchanged_except catches
    those that persist to the end state, so read-only cases use both.
    """
    if run["writes"] is None:
        return _UNDECIDED_NO_TRANSCRIPT
    # Only workspace files count, and not the side files the harness keeps there.
    ignored = HARNESS_FILES.get(harness, set())
    paths = [w if w.startswith("/") else f"{WORKSPACE}/{w}" for w in run["writes"]]
    writes = [w for w in paths if w.startswith(WORKSPACE + "/")
              and w[len(WORKSPACE) + 1:].split("/", 1)[0] not in ignored]
    return {"pass": not writes, "detail": f"wrote {writes}" if writes else ""}


def llm(spec, workspace, initial, harness, run, judges):
    """Hold the output for a batched judge call; `judge_pending` fills in the verdict."""
    if spec.get("path"):
        original = _file_text(initial, spec["path"]) or "(absent)"
        subject = _file_text(workspace, spec["path"]) or "(file missing)"
        label = spec["path"]
        if spec.get("with_final_message"):
            if run["final_message"] is None:
                return _UNDECIDED_NO_TRANSCRIPT
            subject += f"\n>>>\n\nThe agent's final message:\n<<<\n{run['final_message']}"
    elif run["final_message"] is None:
        return _UNDECIDED_NO_TRANSCRIPT
    else:
        original, subject, label = "(not applicable)", run["final_message"], "final message"
    return {"pass": None, "detail": "not judged",
            "pending": {"criteria": spec["criteria"], "original": original, "subject": subject, "label": label}}


def json_output(spec, workspace, initial, harness, run, judges):
    """The file at `path`, or the final message, parses as JSON whole and holds every `required` top-level key."""
    text = _file_text(workspace, spec["path"]) if spec.get("path") else run["final_message"]
    if text is None:
        return {"pass": None if not spec.get("path") else False, "detail": "no text to parse"}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return {"pass": False, "detail": f"not JSON: {exc}"}
    missing = [k for k in spec.get("required", []) if not isinstance(value, dict) or k not in value]
    return {"pass": not missing, "detail": f"missing {missing}" if missing else ""}


GRADERS = {"regex": regex, "file_exists": file_exists, "unchanged_except": unchanged_except,
           "no_writes": no_writes, "llm": llm, "json": json_output}


def run_graders(specs: list[dict], variant: str, workspace: Path, initial: Path, harness: str,
                run: dict, judges: list[str]) -> dict:
    """Run every grader that applies to the variant; a spec's "variants" limits where it applies."""
    return {s["name"]: GRADERS[s["type"]](s, workspace, initial, harness, run, judges)
            for s in specs if variant in s.get("variants", (variant,))}


def judge_pending(rows: list[dict], judges: list[str]) -> None:
    """Judge every pending `llm` grade in `rows`, in place.

    Outputs that share a criterion and original go to each judge in one call, shuffled
    and unlabelled so the judge cannot tell which arm or setup produced them. A group
    over BATCH_CHARS splits across calls.
    """
    groups = defaultdict(list)
    for row in rows:
        for result in row.get("graders", {}).values():
            if "pending" in result:
                p = result["pending"]
                groups[(p["criteria"], p["original"], p["label"])].append(result)
    for (criteria, original, label), results in groups.items():
        random.shuffle(results)
        for batch in _batches(results):
            subjects = [r.pop("pending")["subject"] for r in batch]
            verdicts = {m: judge(m, criteria, original, subjects, label) for m in judges}
            for i, result in enumerate(batch):
                per_judge = {m: v[i] for m, v in verdicts.items()}
                primary = per_judge[judges[0]]
                result.update({"pass": primary["pass"], "detail": primary["reason"], "judges": per_judge})


# Characters of agent output per judge call; a larger group splits.
BATCH_CHARS = 120_000


def _batches(results: list[dict]) -> list[list[dict]]:
    batches, size = [[]], 0
    for result in results:
        n = len(result["pending"]["subject"])
        if batches[-1] and size + n > BATCH_CHARS:
            batches.append([])
            size = 0
        batches[-1].append(result)
        size += n
    return batches


def judge(model: str, criteria: str, original: str, subjects: list[str], label: str) -> list[dict]:
    """Ask one judge model through the proxy at $ANTHROPIC_BASE_URL whether each of `subjects` meets `criteria`."""
    outputs = "\n\n".join(f"Output {i}, the agent's resulting {label}:\n<<<\n{s}\n>>>"
                           for i, s in enumerate(subjects, 1))
    prompt = (
        f"You grade {len(subjects)} outputs of AI agents against one criterion. Each output comes from a separate, "
        "independent run on the same task; judge each on its own, never by comparison with the others. Reply with "
        'JSON only, one object per output: [{"id": 1, "pass": true|false, "reason": "<one sentence>"}, ...].\n\n'
        f"Criterion:\n{criteria}\n\nOriginal {label}:\n<<<\n{original}\n>>>\n\n{outputs}"
    )
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
    if model.startswith("gpt-"):
        url = f"{base}/v1/responses"
        body = {"model": model, "input": prompt, "reasoning": {"effort": "high"}}
    else:
        url = f"{base}/v1/messages"
        body = {"model": model, "max_tokens": 32000, "output_config": {"effort": "high"},
                "messages": [{"role": "user", "content": prompt}]}
    try:
        data = _post(url, body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [{"pass": None, "reason": f"judge call failed: {exc}", "model": model}] * len(subjects)
    if model.startswith("gpt-"):
        text = "".join(c.get("text", "") for o in data.get("output", []) if o.get("type") == "message"
                       for c in o.get("content", []))
    else:
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
    return [v | {"model": data.get("model")} for v in parse_verdicts(text, len(subjects))]


def parse_verdicts(text: str, count: int) -> list[dict]:
    """One verdict per output; a verdict needs a JSON boolean "pass", and anything else is undecided, never a pass or fail."""
    match = re.search(r"\[.*\]", text, re.S)
    try:
        reply = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        reply = None
    by_id = {v.get("id"): v for v in reply if isinstance(v, dict)} if isinstance(reply, list) else {}
    verdicts = []
    for i in range(1, count + 1):
        v = by_id.get(i)
        if not isinstance(v, dict) or not isinstance(v.get("pass"), bool):
            verdicts.append({"pass": None, "reason": f"malformed or missing verdict for output {i}: {text[:200]}"})
        else:
            verdicts.append({"pass": v["pass"], "reason": str(v.get("reason", ""))})
    return verdicts


def _post(url: str, body: dict, attempts: int = 2) -> dict:
    """POST to the proxy, retrying once on throttling or a server error."""
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}",
        "content-type": "application/json", "anthropic-version": "2023-06-01"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt + 1 == attempts:
                raise
            time.sleep(10)
    return {}


@contextlib.contextmanager
def temporary_initial_workspace(case_dir: Path):
    """Yield a temporary copy of the workspace the case starts from."""
    with tempfile.TemporaryDirectory() as tmp:
        yield initial_workspace(case_dir, Path(tmp) / "app")
