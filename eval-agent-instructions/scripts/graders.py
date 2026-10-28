"""Grader types, run on the host against a trial's saved workspace and final message.

Grader specs come from a case's graders.json. Each returns {"pass": bool | None,
"detail": str}; None means the grader could not decide, such as a failed or
malformed judge reply or a transcript that ended early, and is reported apart
from a failure. `run` is the trial's evidence: its final message, every assistant
message in order, and the files it wrote, each None when the transcript is incomplete.
"""
import contextlib
import fnmatch
import hashlib
import json
import os
import random
import re
import shlex
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
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
            return {"pass": bool(spec.get("optional")), "detail": f"{spec['path']} missing"}
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
    # An entry may be a glob, such as `.agents/skills/*`, for files whose names the agent picks.
    allowed = lambda path: any(fnmatch.fnmatchcase(path, pattern) for pattern in spec.get("allow", []))
    ignored = HARNESS_FILES.get(harness, set())
    changed = sorted(p for p in before if not allowed(p) and after.get(p) != before[p])
    added = sorted(p for p in after if p not in before and not allowed(p)
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


def skills_loaded(spec, workspace, initial, harness, run, judges):
    """The transcript shows every skill in `skills` loaded from the installed copies."""
    if run.get("skills_loaded") is None:
        return _UNDECIDED_NO_TRANSCRIPT
    missing = [s for s in spec["skills"] if s not in run["skills_loaded"]]
    return {"pass": not missing, "detail": f"not loaded {missing}" if missing else ""}


def read(spec, workspace, initial, harness, run, judges):
    """A file read or shell command delivered text containing `marker`, such as a file's first line.

    Matching delivered content rather than paths counts wildcard and relative reads,
    and not a listing, a failed read, or a command that only names the file.
    """
    if run.get("ops") is None:
        return _UNDECIDED_NO_TRANSCRIPT
    found = any(spec["marker"] in op["output"] for op in run["ops"]
                if op["kind"] in ("read", "exec") and (op["ok"] or op["kind"] == "exec"))
    wanted = spec.get("match", "contains") == "contains"
    return {"pass": found == wanted, "detail": "" if found == wanted else f"marker {'not ' if wanted else ''}delivered"}


# Commands that only read or print text: a pattern found in their arguments was searched for or
# quoted, not run.
_TEXT_COMMANDS = {"rg", "grep", "egrep", "fgrep", "cat", "head", "tail", "less", "sed", "awk", "echo", "printf",
                  "find", "ls", "wc", "diff", "git grep", "git log", "git show", "git diff"}
_SHELLS = {"sh", "bash", "zsh"}
# Words before the command a part runs: wrappers, and shell keywords that open or close a block.
_PREFIXES = {"sudo", "env", "exec", "time", "do", "done", "then", "else", "fi", "if", "while", "until", "!", "{", "}"}
_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.S)


def invocations(command: str) -> list[str]:
    """The commands a shell line runs, one per pipeline or list element, without heredoc bodies (text
    written to a file) or commands that only read or print text. A command a harness wraps in a shell,
    as Codex runs `/usr/bin/zsh -lc "<command>"`, counts as the command it wraps."""
    try:
        words = shlex.split(command)
    except ValueError:
        words = []
    if len(words) == 3 and Path(words[0]).name in _SHELLS and words[1] in ("-c", "-lc"):
        return invocations(words[2])
    found = []
    for line in _HEREDOC.sub("", command).splitlines():
        try:
            tokens = list(shlex.shlex(line, posix=True, punctuation_chars=True))
        except ValueError:
            tokens = line.split()
        part = []
        for token in tokens + [";"]:
            if token not in (";", "&&", "||", "|", "&", "(", ")"):
                part.append(token)
                continue
            while part and (re.fullmatch(r"\w+=.*", part[0]) or part[0] in _PREFIXES):
                part = part[1:]
            # A `for x in a b` header lists words; it runs nothing.
            if part and part[0] in ("for", "select", "case"):
                part = []
            if part and part[0] not in _TEXT_COMMANDS and " ".join(part[:2]) not in _TEXT_COMMANDS:
                found.append(" ".join(part))
            part = []
    return found


def ran(spec, workspace, initial, harness, run, judges):
    """A shell command matching `pattern` ran and succeeded; with `not_contains`, none was even tried,
    since a command that failed only because its tool is missing still shows the attempt. Text the
    agent searched for, printed or wrote through a heredoc does not count as running it."""
    if run.get("ops") is None:
        return _UNDECIDED_NO_TRANSCRIPT
    wanted = spec.get("match", "contains") == "contains"
    found = any(re.search(spec["pattern"], part) for op in run["ops"]
                if op["kind"] == "exec" and (op["ok"] or not wanted) for part in invocations(op["path"]))
    return {"pass": found == wanted, "detail": "" if found == wanted else f"command {'not ' if wanted else ''}run"}


def _glob_files(root: Path, pattern: str):
    """Files matching `pattern`; a matched folder, as `dir/**` yields, stands for every file under it."""
    for match in root.glob(pattern):
        if ".git" in match.relative_to(root).parts:
            continue
        if match.is_file():
            yield match
        elif match.is_dir():
            yield from (f for f in match.rglob("*") if f.is_file() and ".git" not in f.relative_to(root).parts)


def _agent_text(spec, run) -> tuple[str | None, str]:
    """(text, what it is) the judge sees of the agent's messages: with `all_messages` every assistant message of
    the run in order, else the final message; the text is None when the transcript is incomplete."""
    if not spec.get("all_messages"):
        return run["final_message"], "final message"
    texts = run.get("messages")
    joined = None if texts is None else "\n\n".join(f"[message {i}]\n{t}" for i, t in enumerate(texts, 1))
    return joined, "messages, in order"


def llm(spec, workspace, initial, harness, run, judges):
    """Hold the output for a batched judge call; `judge_pending` fills in the verdict."""
    message, kind = _agent_text(spec, run)
    if spec.get("paths"):
        # Several files go to the judge as one document, each under its own header.
        # A glob such as `skill/**/*.md` stands for every matching file in either workspace.
        names = sorted({str(f.relative_to(root)) for pattern in spec["paths"] for root in (initial, workspace)
                        for f in _glob_files(root, pattern)} if any("*" in p for p in spec["paths"]) else [])
        names = names + [p for p in spec["paths"] if "*" not in p and p not in names]

        def joined(root, missing):
            texts = {p: _file_text(root, p) for p in names}
            return "\n\n".join(f"=== {p}\n{missing if t is None else t}" for p, t in texts.items())
        original, subject = joined(initial, "(absent)"), joined(workspace, "(file missing)")
        label = "files " + ", ".join(names)
    elif spec.get("path"):
        original, subject = _file_text(initial, spec["path"]), _file_text(workspace, spec["path"])
        original = "(absent)" if original is None else original
        subject = "(file missing)" if subject is None else subject
        label = spec["path"]
    if spec.get("path") or spec.get("paths"):
        if spec.get("with_final_message") or spec.get("all_messages"):
            if message is None:
                return _UNDECIDED_NO_TRANSCRIPT
            subject += f"\n>>>\n\nThe agent's {kind}:\n<<<\n{message}"
    elif message is None:
        return _UNDECIDED_NO_TRANSCRIPT
    else:
        # The label differs between the two kinds, so a cached verdict on one never stands for the other.
        original, subject, label = "(not applicable)", message, kind
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
           "no_writes": no_writes, "skills_loaded": skills_loaded, "read": read, "ran": ran, "llm": llm, "json": json_output}


# Fields each grader type cannot run without.
REQUIRED = {"regex": ("pattern",), "file_exists": ("path",), "unchanged_except": (), "no_writes": (),
            "skills_loaded": ("skills",), "read": ("marker",), "ran": ("pattern",), "llm": ("criteria",), "json": ()}


def spec_problems(specs: list[dict]) -> list[str]:
    """Grader specs that would fail or mislead at grading time; empty when all are sound."""
    problems = []
    for s in specs:
        kind = s.get("type")
        if kind not in GRADERS:
            problems.append(f"{s.get('name')}: unknown type {kind}")
            continue
        problems += [f"{s['name']}: {kind} needs {f}" for f in REQUIRED[kind] if f not in s]
        if "path" in s and "paths" in s:
            problems.append(f"{s['name']}: give path or paths, not both")
    return problems


def run_graders(specs: list[dict], variant: str, workspace: Path, initial: Path, harness: str,
                run: dict, judges: list[str]) -> dict:
    """Run every grader that applies to the variant; a spec's "variants" limits where it applies."""
    return {s["name"]: GRADERS[s["type"]](s, workspace, initial, harness, run, judges)
            for s in specs if variant in s.get("variants", (variant,))}


# Judge calls in flight at once; throttled calls retry with backoff.
JUDGE_WORKERS = 12


def judge_pending(rows: list[dict], judges: list[str], cache_path: Path | None = None) -> list[dict]:
    """Judge every pending `llm` grade in `rows`, in place; return one usage record per judge call.

    Outputs that share a criterion and original go to each judge in one call, shuffled
    and unlabelled so the judge cannot tell which arm or setup produced them. A group
    over BATCH_CHARS splits across calls, and calls run JUDGE_WORKERS at a time.

    A decided verdict is saved in `cache_path`; an output that already has one from the
    same judge, prompt, criterion and original keeps it, marked "cached", instead of
    being judged again.
    """
    cache = _load_cache(cache_path)
    groups = defaultdict(list)
    for row in rows:
        for result in row.get("graders", {}).values():
            if "pending" in result:
                p = result["pending"]
                groups[(p["criteria"], p["original"], p["label"])].append(result)
    verdicts, calls = defaultdict(dict), []
    for (criteria, original, label), results in groups.items():
        random.shuffle(results)
        for model in judges:
            todo = []
            for result in results:
                saved = cache.get(_cache_key(model, criteria, original, label, result["pending"]["subject"]))
                if saved:
                    verdicts[id(result)][model] = saved | {"cached": True}
                else:
                    todo.append(result)
            calls += [(model, criteria, original, label, batch) for batch in _batches(todo) if batch]

    def call(c):
        model, criteria, original, label, batch = c
        return judge(model, criteria, original, [r["pending"]["subject"] for r in batch], label)

    new, usage = [], []
    with ThreadPoolExecutor(JUDGE_WORKERS) as pool:
        for (model, criteria, original, label, batch), (replies, used) in zip(calls, pool.map(call, calls)):
            usage.append({"judge": model, "outputs": len(batch)} | used)
            for result, verdict in zip(batch, replies):
                verdicts[id(result)][model] = verdict
                if verdict["pass"] is not None:
                    key = _cache_key(model, criteria, original, label, result["pending"]["subject"])
                    new.append({"key": key, "verdict": verdict})
    for results in groups.values():
        for result in results:
            result.pop("pending")
            per_judge = verdicts[id(result)]
            primary = per_judge[judges[0]]
            result.update({"pass": primary["pass"], "detail": primary["reason"], "judges": per_judge})
    if cache_path and new:
        with open(cache_path, "a") as f:
            f.writelines(json.dumps(entry) + "\n" for entry in new)
    return usage


def _load_cache(path: Path | None) -> dict[str, dict]:
    if not path or not path.is_file():
        return {}
    cache = {}
    for line in path.read_text().splitlines():
        # An interrupted append leaves a partial last line; its verdict is judged again.
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        cache[entry["key"]] = entry["verdict"]
    return cache


def _cache_key(model: str, criteria: str, original: str, label: str, subject: str) -> str:
    """Everything a verdict depends on: the request settings, the prompt, and what it grades."""
    parts = [JUDGE_PROMPT, JUDGE_EFFORT, JUDGE_MAX_TOKENS, model, criteria, original, label, subject]
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()


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


JUDGE_PROMPT = (
    "You grade {count} outputs of AI agents against one criterion. Each output comes from a separate, "
    "independent run on the same task; judge each on its own, never by comparison with the others. Judge the "
    "end result and its meaning, not its wording: any phrasing with the same effect passes unless the criterion "
    "requires exact text. Reply with "
    'JSON only, one object per output: [{{"id": 1, "pass": true|false, "reason": "<one sentence>"}}, ...].\n\n'
    "Criterion:\n{criteria}\n\nOriginal {label}:\n<<<\n{original}\n>>>\n\n{outputs}"
)
JUDGE_EFFORT = "high"
JUDGE_MAX_TOKENS = 32000


def judge(model: str, criteria: str, original: str, subjects: list[str], label: str) -> tuple[list[dict], dict]:
    """Ask one judge model through the proxy at $ANTHROPIC_BASE_URL whether each of `subjects` meets `criteria`;
    return the verdicts and the call's token usage."""
    outputs = "\n\n".join(f"Output {i}, the agent's resulting {label}:\n<<<\n{s}\n>>>"
                           for i, s in enumerate(subjects, 1))
    prompt = JUDGE_PROMPT.format(count=len(subjects), criteria=criteria, label=label, original=original,
                                 outputs=outputs)
    try:
        text, served, used = complete(model, prompt)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [{"pass": None, "reason": f"judge call failed: {exc}", "model": model}] * len(subjects), {}
    return [v | {"model": served} for v in parse_verdicts(text, len(subjects))], used


def complete(model: str, prompt: str) -> tuple[str, str | None, dict]:
    """(reply text, model that answered, input and output tokens) for one judge prompt through the proxy at
    $ANTHROPIC_BASE_URL."""
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
    if model.startswith("gpt-"):
        url = f"{base}/v1/responses"
        body = {"model": model, "input": prompt, "reasoning": {"effort": JUDGE_EFFORT}}
    else:
        url = f"{base}/v1/messages"
        body = {"model": model, "max_tokens": JUDGE_MAX_TOKENS, "output_config": {"effort": JUDGE_EFFORT},
                "messages": [{"role": "user", "content": prompt}]}
    data = _post(url, body)
    if model.startswith("gpt-"):
        text = "".join(c.get("text", "") for o in data.get("output", []) if o.get("type") == "message"
                       for c in o.get("content", []))
    else:
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
    reported = data.get("usage") or {}
    # Anthropic counts cached input apart from input_tokens; the Responses API includes it.
    used = {"input_tokens": sum(reported.get(k) or 0 for k in
                                ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
            "output_tokens": reported.get("output_tokens") or 0} if reported else {}
    return text, data.get("model"), used


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


def _post(url: str, body: dict, attempts: int = 4) -> dict:
    """POST to the proxy, retrying throttling and server errors after 10, 20 and 40 s."""
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
            time.sleep(10 * 2 ** attempt)
    return {}


@contextlib.contextmanager
def temporary_initial_workspace(case_dir: Path):
    """Yield a temporary copy of the workspace the case starts from."""
    with tempfile.TemporaryDirectory() as tmp:
        yield initial_workspace(case_dir, Path(tmp) / "app")
