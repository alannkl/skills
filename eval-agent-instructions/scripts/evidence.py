"""Extract normalized evidence from one Harbor trial's agent logs, per harness.

Each harness's log is reduced to operations: file reads, file writes, shell
commands with their output, and (Claude Code only) skill injections. From those,
every extractor reports the same record: whether the transcript is complete,
the models that answered, the final message, the skills the agent loaded from
the installed copies, any same-named skills it loaded from elsewhere, the files
it wrote, the skills the harness listed (None when it does not say), usage and cost.

A skill counts as loaded only when its instructions reached the agent: a read or
command on a `<name>/SKILL.md` path whose output carries the `name:` frontmatter,
the closing `---`, and the start of the body, or Claude Code's Skill tool injecting
it. Reading only the frontmatter is discovery, not loading. The copy counts as the
one under test only when its path starts with the harness's install root; a
same-named copy anywhere else is foreign. When the transcript is missing or ends
early, loaded skills and writes are None (unknown).
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Where each harness's Harbor adapter installs the skills from the task's skills_dir,
# with the agent running as root, plus skills_dir itself, which a --minus prompt names.
# OpenClaw's export redacts its state directory.
INSTALLED_ROOTS = {
    "claude-code": ("/logs/agent/sessions/skills/", "/skills/"),
    "codex": ("/root/.agents/skills/", "/skills/"),
    "openclaw": ("$OPENCLAW_STATE_DIR/skills/", "/root/.openclaw/skills/", "/skills/"),
    "api": (),
}
_SKILL_FILE = re.compile(r"[^\s'\"`]*/([A-Za-z0-9._-]+)/SKILL\.md")


def _absolute(path: str) -> str:
    for home in ("~/", "$HOME/", "${HOME}/"):
        if path.startswith(home):
            return "/root/" + path[len(home):]
    return path


def _delivers_body(output: str, name: str) -> bool:
    """The output holds the frontmatter naming the skill, its closing `---`, and body text after it.

    Lines may carry a line-number prefix, as Claude Code's Read output does.
    """
    pattern = rf"(?:^|\s)name:\s*{re.escape(name)}\s*$[\s\S]*?^[\s\d]*---\s*$\s*\d*\s*\S"
    return re.search(pattern, output, re.M) is not None


def _json_lines(path: Path):
    if not path.is_file():
        return
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                yield json.loads(line, strict=False)
            except json.JSONDecodeError:
                continue


def _text(content) -> str:
    """Flatten a tool result's content (a string or a list of text blocks) to text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def _op(kind: str, ok: bool, path: str = "", output: str = "") -> dict:
    return {"kind": kind, "ok": ok, "path": path, "output": output}


def summarize(harness: str, ops: list[dict], complete: bool, **fields) -> dict:
    """The common record, derived from a harness's operations."""
    loaded, foreign = set(), set()
    for op in ops:
        # A command's output is what the agent saw, even when a later step in it failed.
        if not op["ok"] and op["kind"] != "exec":
            continue
        if op["kind"] == "skill":
            hits = [(op["path"].rstrip("/").rsplit("/", 1)[-1], op["path"].rstrip("/") + "/SKILL.md")]
        elif op["kind"] in ("read", "exec"):
            hits = [(m.group(1), _absolute(m.group(0))) for m in _SKILL_FILE.finditer(op["path"])
                    if _delivers_body(op["output"], m.group(1))]
        else:
            continue
        for name, origin in hits:
            installed = any(origin.startswith(root) for root in INSTALLED_ROOTS[harness])
            (loaded if installed else foreign).add(name)
    record = {"complete": complete, "models": [], "final_message": "", "skills_listed": None,
              "usage": None, "cost_usd": None, "cost_basis": None,
              "skills_loaded": sorted(loaded) if complete else None,
              "foreign_skills_loaded": sorted(foreign) if complete else None,
              "writes": sorted({op["path"] for op in ops if op["kind"] == "write" and op["ok"]}) if complete else None}
    record.update(fields)
    return record


def claude_code(agent_dir: Path) -> dict:
    events = list(_json_lines(agent_dir / "claude-code.txt"))
    ops, models, texts, listed, calls = [], set(), [], None, {}
    usage = cost = None
    complete = False
    for e in events:
        kind = e.get("type")
        if kind == "system" and e.get("subtype") == "init":
            listed = e.get("skills")
        elif kind == "assistant":
            message = e.get("message", {})
            models.add(message.get("model"))
            for block in message.get("content", []):
                if block.get("type") == "text":
                    texts.append(block["text"])
                elif block.get("type") == "tool_use":
                    calls[block["id"]] = (block["name"], block.get("input", {}))
        elif kind == "user":
            content = e.get("message", {}).get("content", [])
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_result" and block.get("tool_use_id") in calls:
                    name, args = calls.pop(block["tool_use_id"])
                    ok, output = not block.get("is_error"), _text(block.get("content"))
                    if name == "Read":
                        ops.append(_op("read", ok, args.get("file_path", ""), output))
                    elif name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                        ops.append(_op("write", ok, args.get("file_path") or args.get("notebook_path", "")))
                    elif name == "Bash":
                        ops.append(_op("exec", ok, args.get("command", ""), output))
                # The Skill tool injects the skill body headed by its base directory.
                if block.get("type") == "text":
                    for m in re.finditer(r"Base directory for this skill: (\S+)", block.get("text", "")):
                        ops.append(_op("skill", True, m.group(1)))
        elif kind == "result":
            usage, cost, complete = e.get("usage"), e.get("total_cost_usd"), True
    return summarize("claude-code", ops, complete, models=sorted(m for m in models if m),
                     final_message=texts[-1] if texts else "", skills_listed=listed, usage=usage,
                     cost_usd=cost, cost_basis="Claude Code estimate from model name")


def codex(agent_dir: Path) -> dict:
    ops, texts, usage, complete = [], [], None, False
    for e in _json_lines(agent_dir / "codex.txt"):
        item = e.get("item") or {}
        if e.get("type") == "item.completed":
            if item.get("type") == "agent_message":
                texts.append(item.get("text", ""))
            elif item.get("type") == "command_execution":
                ops.append(_op("exec", item.get("exit_code") == 0, item.get("command", ""),
                               item.get("aggregated_output", "")))
            elif item.get("type") == "file_change":
                ok = item.get("status", "completed") == "completed"
                ops += [_op("write", ok, change.get("path", "")) for change in item.get("changes", [])]
        elif e.get("type") == "turn.completed":
            usage, complete = e.get("usage"), True
    models = set()
    for session in (agent_dir / "sessions").rglob("*.jsonl"):
        for e in _json_lines(session):
            if e.get("type") == "turn_context":
                models.add(e.get("payload", {}).get("model"))
    return summarize("codex", ops, complete, models=sorted(m for m in models if m),
                     model_basis="requested; Codex logs no response model",
                     final_message=texts[-1] if texts else "", usage=usage, cost_basis="tokens only")


# Harbor captures OpenClaw's stderr into the same file, so a log line such as
# "[agents/agent-command] run ... ended" can land inside the JSON envelope, on a
# line of its own or mid-line at a pipe-buffer boundary. JSON strings cannot span
# lines, so a whole line of this shape is never envelope text; the mid-line form
# is tried last, and only a parse that yields the envelope is accepted.
_OPENCLAW_LOG_LINE = re.compile(r"^\s*\[[A-Za-z][\w/.:-]*\] .*\n", re.M)
_OPENCLAW_LOG_SPLICE = re.compile(r"\[[a-z][\w/.:-]*\] \[[\w-]+\] [^\n]*\n")


def _openclaw_envelope(agent_dir: Path) -> dict | None:
    path = agent_dir / "openclaw.txt"
    if not path.is_file():
        return None
    text = path.read_text(errors="replace")
    unlined = _OPENCLAW_LOG_LINE.sub("", text)
    for candidate in (text, unlined, _OPENCLAW_LOG_SPLICE.sub("", unlined)):
        decoder = json.JSONDecoder(strict=False)
        start = candidate.find("\n{")
        while start != -1:
            try:
                obj, _ = decoder.raw_decode(candidate[start + 1:])
                if isinstance(obj, dict) and "meta" in obj:
                    return obj
            except json.JSONDecodeError:
                pass
            start = candidate.find("\n{", start + 1)
    return None


def _openclaw_export_complete(events_path: Path) -> bool:
    """An export is whole only when it reaches the session's end event."""
    return any(e.get("type") == "session.ended" for e in _json_lines(events_path))


def _openclaw_ops(events_path: Path) -> list[dict]:
    """Operations from the exported trajectory's runtime events, which the transcript events duplicate."""
    calls, results = {}, {}
    for e in _json_lines(events_path):
        if e.get("source") != "runtime":
            continue
        data = e.get("data", {})
        if e.get("type") == "tool.call":
            calls[data.get("toolCallId")] = (data.get("name"), data.get("args") or {})
        elif e.get("type") == "tool.result":
            results[data.get("toolCallId")] = (bool(data.get("success")),
                                               _text((data.get("result") or {}).get("content")))
    ops = []
    for call_id, (name, args) in calls.items():
        ok, output = results.get(call_id, (False, ""))
        if name == "read":
            ops.append(_op("read", ok, args.get("path", ""), output))
        elif name in ("write", "edit", "apply_patch"):
            ops.append(_op("write", ok, args.get("path", "")))
        elif name == "exec":
            ops.append(_op("exec", ok, args.get("command", ""), output))
    return ops


# OpenRouter lookups in flight at once for one trial.
LOOKUP_WORKERS = 8


def openrouter_generations(agent_dir: Path) -> list[dict] | None:
    """Each OpenRouter generation the run made, with its upstream provider. Needs OPENROUTER_API_KEY
    for any generation not yet looked up.

    Lookups are saved beside the transcript, so a regrade repeats only the ones that failed.
    """
    events_path = agent_dir / "openclaw-trajectory" / "events.jsonl"
    if not events_path.is_file():
        return None
    ids = sorted(set(re.findall(r'"responseId":"(gen-[^"]+)"', events_path.read_text(errors="replace"))))
    saved_path = agent_dir / "openrouter-generations.json"
    try:
        saved = {g["id"]: g for g in json.loads(saved_path.read_text())}
    except (FileNotFoundError, json.JSONDecodeError):
        saved = {}
    todo = [i for i in ids if i not in saved or "lookup_error" in saved[i]]
    key = os.environ.get("OPENROUTER_API_KEY")
    if todo and not key:
        return None
    if todo:
        with ThreadPoolExecutor(LOOKUP_WORKERS) as pool:
            saved.update(zip(todo, pool.map(lambda gen_id: _generation(gen_id, key), todo)))
        # Replace, never truncate: an interrupted write must not lose the lookups already saved.
        partial = saved_path.with_suffix(".partial")
        partial.write_text(json.dumps([saved[i] for i in ids]))
        partial.replace(saved_path)
    return [saved[i] for i in ids]


def _generation(gen_id: str, key: str, attempts: int = 3) -> dict:
    """One generation's record; a lookup that keeps failing yields an unknown provider, not a crash."""
    error = None
    for attempt in range(attempts):
        request = urllib.request.Request(f"https://openrouter.ai/api/v1/generation?id={gen_id}",
                                         headers={"Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode(), strict=False).get("data", {})
            return {"id": gen_id, "provider": data.get("provider_name"), "model": data.get("model"),
                    "reasoning_tokens": data.get("native_tokens_reasoning"), "cost": data.get("total_cost")}
        except (urllib.error.URLError, TimeoutError) as exc:
            error = str(exc)
            time.sleep(2 * (attempt + 1))
    return {"id": gen_id, "provider": None, "lookup_error": error}


def openclaw(agent_dir: Path) -> dict:
    envelope = _openclaw_envelope(agent_dir)
    events_path = agent_dir / "openclaw-trajectory" / "events.jsonl"
    if envelope is None:
        return summarize("openclaw", [], False)
    meta = envelope["meta"]
    agent_meta = meta.get("agentMeta", {})
    receipt = agent_meta.get("terminalReceipt", {})
    effective = receipt.get("effective", {})
    # Only OpenRouter has a generation endpoint naming the upstream provider.
    generations = openrouter_generations(agent_dir) if effective.get("provider") == "openrouter" else None
    payloads = envelope.get("payloads") or []
    return summarize(
        "openclaw", _openclaw_ops(events_path), _openclaw_export_complete(events_path),
        models=sorted({m for m in (effective.get("responseModel"), effective.get("model")) if m}),
        final_message=payloads[-1].get("text", "") if payloads else "",
        skills_listed=[s.get("name") for s in meta.get("systemPromptReport", {}).get("skills", {}).get("entries", [])],
        usage=agent_meta.get("usage"),
        cost_usd=agent_meta.get("costUsd"),
        cost_basis=agent_meta.get("usage", {}).get("cost", {}).get("totalOrigin"),
        rerouted=receipt.get("rerouted"),
        fallback_used=meta.get("executionTrace", {}).get("fallbackUsed"),
        thinking=meta.get("requestShaping", {}).get("thinking"),
        upstream_providers=None if generations is None else sorted({str(g["provider"]) for g in generations}),
        generations=generations,
        terminal_error=_openclaw_terminal_error(events_path),
    )


def _openclaw_terminal_error(events_path: Path) -> str | None:
    """The error that ended the run without a deliverable turn, such as output hitting the token cap."""
    for event in _json_lines(events_path):
        if event.get("type") == "model.completed" and (event.get("data") or {}).get("terminalError"):
            return event["data"]["terminalError"]
    return None


def api(agent_dir: Path) -> dict:
    """A direct API call has no tools, so its record is the reply alone."""
    path = agent_dir / "api.json"
    if not path.is_file():
        return summarize("api", [], False)
    reply = json.loads(path.read_text())
    return summarize("api", [], True, models=[reply["model"]] if reply.get("model") else [],
                     final_message=reply.get("text", ""), usage=reply.get("usage"), cost_usd=reply.get("cost_usd"),
                     cost_basis="reported by the API" if reply.get("cost_usd") is not None else None,
                     upstream_providers=[reply["provider"]] if reply.get("provider") else None)


EXTRACTORS = {"claude-code": claude_code, "codex": codex, "openclaw": openclaw, "api": api}
