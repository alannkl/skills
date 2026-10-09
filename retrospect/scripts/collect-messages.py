#!/usr/bin/env python3
"""Indexes the messages the user typed in recent agent sessions, across harnesses.

Reads Claude Code, Codex, Cursor CLI and Antigravity CLI logs under $HOME
read-only and keeps only messages a person typed: no injected context, tool
results, subagent or headless prompts. Splits them into time slices for
collectors and lists every session active in each slice. Message text goes to
files only; stdout carries counts and paths. Files that lack a format's markers
are counted as unrecognized, never guessed.
"""
import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

DEFAULT_DAYS = 14
INVOCATION = re.compile(r"^\s*(?:<command-message>retrospect</command-message>|\[?[/$]retrospect\b)")
LIMITS = {
    "cursor": "headless runs (agent -p) are indistinguishable from typed sessions; tool results are not logged",
    "antigravity": "tool-call and subagent steps are unverified",
}


def main():
    args = parse_args()
    home = Path.home()
    until = dt.datetime.now(dt.timezone.utc)
    try:
        window = resolve_window(args.since, home / ".agents" / "retrospect-last-run", until)
    except ValueError as error:
        print(json.dumps({"error": str(error)}))
        return 2
    project = str(Path(args.project).expanduser().resolve()) if args.project else None
    since = window["since"]

    readers = {"claude-code": read_claude, "codex": read_codex, "cursor": read_cursor, "antigravity": read_antigravity}
    harnesses, messages, sessions = {}, [], []
    for name, reader in readers.items():
        harvest = reader(home, since)
        harnesses[name] = harvest.report(LIMITS.get(name))
        messages += harvest.messages
        sessions += harvest.sessions

    in_scope = lambda item: item["time" if "time" in item else "last"] >= since and matches_project(item["project"], project)
    messages = [m for m in messages if in_scope(m)]
    sessions = [s for s in sessions if in_scope(s)]
    excluded = sorted({(m["harness"], m["session"]) for m in messages if INVOCATION.match(m["text"])})
    messages = sorted((m for m in messages if (m["harness"], m["session"]) not in excluded), key=lambda m: m["time"])
    sessions = [s for s in sessions if (s["harness"], s["session"]) not in excluded]
    for name in harnesses:
        harnesses[name]["messages"] = sum(m["harness"] == name for m in messages)

    out = Path(args.out).expanduser() if args.out else home / ".tmp" / "retrospect" / until.strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    summary = {
        "window": {**window, "since": iso(since), "until": iso(until)},
        "project": project,
        "harnesses": harnesses,
        "excluded_sessions": [{"harness": h, "session": s} for h, s in excluded],
        "projects": count_projects(messages),
        "slices": write_slices(out, messages, sessions, args.slices, since, until),
        "out": str(out),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description="Index user-typed messages from recent agent sessions into time slices.",
        epilog="Exits 0 with a JSON summary on stdout (window, per-harness status and counts, excluded sessions, "
               "message counts per project, slice files); 2 for an unusable --since. The window starts at the later "
               f"of {DEFAULT_DAYS} days ago and the time in ~/.agents/retrospect-last-run unless --since is given. "
               "Sessions that invoke retrospect are excluded. Each slice-<n>.json holds its messages and the sessions "
               "active in its time range; message text never reaches stdout.",
    )
    parser.add_argument("--since", help="Window start, ISO 8601 date or time; naive values are local time")
    parser.add_argument("--project", help="Keep only sessions in this directory or below it")
    parser.add_argument("--slices", type=int, default=3, help="Number of time slices (default 3)")
    parser.add_argument("--out", help="Output directory; default ~/.tmp/retrospect/<UTC time>/")
    return parser.parse_args()


def resolve_window(since_arg, stamp_path, until):
    if since_arg:
        try:
            return {"since": parse_time(since_arg), "source": "argument"}
        except ValueError:
            raise ValueError(f"--since is not an ISO 8601 date or time: {since_arg!r}")
    window = {"since": until - dt.timedelta(days=DEFAULT_DAYS), "source": f"default {DEFAULT_DAYS} days"}
    if stamp_path.exists():
        try:
            stamp = parse_time(stamp_path.read_text().strip())
        except ValueError:
            window["note"] = f"{stamp_path} is not an ISO 8601 time; ignored"
            return window
        if stamp > window["since"]:
            window = {"since": stamp, "source": f"last run stamp {stamp_path}"}
    return window


class Harvest:
    """What one harness reader found: typed messages, sessions and file counts."""

    def __init__(self, root):
        self.root = root
        self.messages, self.sessions = [], []
        self.files = self.unrecognized = self.headless = self.subagent = 0

    def add_session(self, harness, session, project, transcript, role, times):
        if not times:
            return
        self.files += 1
        self.headless += role == "headless"
        self.subagent += role == "subagent"
        self.sessions.append({"harness": harness, "session": session, "project": project, "transcript": str(transcript),
                              "role": role, "first": min(times), "last": max(times)})

    def add_message(self, harness, session, project, transcript, time, text):
        text = text.strip()
        if text:
            self.messages.append({"harness": harness, "session": session, "project": project,
                                  "transcript": str(transcript), "time": time, "text": text})

    def report(self, limits):
        if not self.root.is_dir():
            return {"status": "absent", "root": str(self.root)}
        status = "unrecognized" if self.unrecognized and not self.files else "read"
        report = {"status": status, "root": str(self.root), "sessions": self.files, "headless": self.headless,
                  "subagent": self.subagent, "unrecognized_files": self.unrecognized}
        if limits:
            report["limits"] = limits
        return report


# Claude Code: ~/.claude/projects/<slug>/<session>.jsonl, subagents in <session>/subagents/.
IDE_BLOCK = re.compile(r"<ide_[a-z_]+>.*?</ide_[a-z_]+>\s*", re.S)


def read_claude(home, since):
    harvest = Harvest(home / ".claude" / "projects")
    for path in recent(harvest.root.glob("*/*/subagents/*.jsonl"), since):
        records = list(jsonl(path))
        harvest.add_session("claude-code", path.stem, first_value(records, "cwd"), path, "subagent", claude_times(records))
    for path in recent(harvest.root.glob("*/*.jsonl"), since):
        records = list(jsonl(path))
        users = [r for r in records if r.get("type") == "user"]
        has_origin = any("origin" in r for r in users)
        if any(r.get("entrypoint") == "sdk-cli" for r in records) or (
                not has_origin and any(r.get("promptSource") == "sdk" for r in users)):
            role = "headless"
        elif users and not has_origin:
            harvest.unrecognized += 1
            continue
        else:
            role = "interactive"
        session = first_value(records, "sessionId") or path.stem
        harvest.add_session("claude-code", session, first_value(records, "cwd"), path, role, claude_times(records))
        if role != "interactive":
            continue
        for record in records:
            text = claude_typed_text(record)
            if text is not None:
                harvest.add_message("claude-code", session, record.get("cwd"), path, parse_time(record["timestamp"]),
                                    IDE_BLOCK.sub("", text))
    return harvest


def claude_typed_text(record):
    if record.get("type") == "user":
        content = (record.get("message") or {}).get("content")
        if ((record.get("origin") or {}).get("kind") != "human" or record.get("isSidechain") or record.get("isMeta")
                or record.get("toolUseResult") is not None
                or isinstance(content, list) and content and content[0].get("type") == "tool_result"):
            return None
        return block_text(content)
    attachment = record.get("attachment") or {}
    if (record.get("type") == "attachment" and attachment.get("type") == "queued_command"
            and (attachment.get("origin") or {}).get("kind") == "human"):
        return block_text(attachment.get("prompt"))
    return None


def claude_times(records):
    return [parse_time(r["timestamp"]) for r in records if r.get("timestamp")]


# Codex: ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl, one session_meta per file.
def read_codex(home, since):
    harvest = Harvest(home / ".codex" / "sessions")
    for path in recent(harvest.root.glob("*/*/*/*.jsonl"), since):
        records = list(jsonl(path))
        meta = next((r.get("payload") or {} for r in records if r.get("type") == "session_meta"), None)
        if meta is None:
            harvest.unrecognized += 1
            continue
        source = meta.get("source")
        role = ("subagent" if isinstance(source, dict)
                else "headless" if meta.get("originator") == "codex_exec" or source == "exec" else "interactive")
        times = [parse_time(r["timestamp"]) for r in records if r.get("timestamp")]
        harvest.add_session("codex", meta.get("id", path.stem), meta.get("cwd"), path, role, times)
        if role != "interactive":
            continue
        for record in records:
            payload = record.get("payload") or {}
            item = payload.get("item") or {}
            if record.get("type") != "event_msg" or payload.get("type") != "item_completed" or item.get("type") != "UserMessage":
                continue
            text = block_text(item.get("content"))
            if text.startswith("# Context from my IDE"):
                text = text.partition("## My request:\n")[2]
            if not text.startswith("<send_user_message_question_reply>"):
                harvest.add_message("codex", meta.get("id", path.stem), meta.get("cwd"), path,
                                    parse_time(record["timestamp"]), text)
    return harvest


# Cursor CLI: ~/.cursor/projects/<slug>/agent-transcripts/<chat>/<chat>.jsonl; no per-record time or cwd.
USER_QUERY = re.compile(r"<user_query>(.*?)</user_query>", re.S)
CURSOR_TIME = re.compile(r"<timestamp>\w+, (\w+ \d+, \d+, \d+:\d+ [AP]M) \(UTC([+-])(\d+)(?::(\d+))?\)</timestamp>")


def read_cursor(home, since):
    harvest = Harvest(home / ".cursor" / "projects")
    resolved = {}
    for path in recent(harvest.root.glob("*/agent-transcripts/*/**/*.jsonl"), since):
        slug = path.relative_to(harvest.root).parts[0]
        if slug not in resolved:
            resolved[slug] = resolve_cursor_slug(slug)
        project, modified = resolved[slug], file_time(path)
        if "subagents" in path.parts:
            harvest.add_session("cursor", path.stem, project, path, "subagent", [modified])
            continue
        typed = []
        for record in jsonl(path):
            if record.get("role") != "user":
                continue
            text = block_text((record.get("message") or {}).get("content"))
            query = USER_QUERY.search(text)
            if query:
                typed.append((cursor_time(text) or modified, query.group(1)))
        if not typed:
            harvest.unrecognized += 1
            continue
        harvest.add_session("cursor", path.stem, project, path, "interactive", [modified, *(t for t, _ in typed)])
        for time, text in typed:
            harvest.add_message("cursor", path.stem, project, path, time, text)
    return harvest


def cursor_time(text):
    match = CURSOR_TIME.search(text)
    if not match:
        return None
    for month in ("%b", "%B"):
        try:
            local = dt.datetime.strptime(match.group(1), f"{month} %d, %Y, %I:%M %p")
            break
        except ValueError:
            continue
    else:
        return None
    sign = 1 if match.group(2) == "+" else -1
    offset = dt.timedelta(hours=int(match.group(3)), minutes=int(match.group(4) or 0)) * sign
    return local.replace(tzinfo=dt.timezone(offset)).astimezone(dt.timezone.utc)


def resolve_cursor_slug(slug):
    """Finds the existing directory whose path Cursor turned into slug ('/' became '-', '.' dropped)."""
    def walk(base, rest):
        if not rest:
            return str(base)
        try:
            entries = sorted((e for e in os.scandir(base) if e.is_dir()), key=lambda e: -len(e.name))
        except OSError:
            return None
        for entry in entries:
            key = entry.name.replace(".", "")
            if key and (rest == key or rest.startswith(key + "-")):
                found = walk(Path(entry.path), rest[len(key) + 1:])
                if found:
                    return found
        return None

    return walk(Path("/"), slug) or f"cursor-slug:{slug}"


# Antigravity CLI: ~/.gemini/antigravity-cli/brain/<id>/.system_generated/logs/transcript_full.jsonl,
# workspace in conversations/<id>.db.
USER_REQUEST = re.compile(r"<USER_REQUEST>(.*?)</USER_REQUEST>", re.S)


def read_antigravity(home, since):
    harvest = Harvest(home / ".gemini" / "antigravity-cli")
    transcripts = harvest.root.glob("brain/*/.system_generated/logs/transcript_full.jsonl")
    for path in recent(transcripts, since):
        conversation = path.parents[2].name
        records = list(jsonl(path))
        try:
            workspace = antigravity_workspace(harvest.root / "conversations" / f"{conversation}.db")
        except (sqlite3.Error, ValueError, IndexError, UnicodeDecodeError):
            harvest.unrecognized += 1
            continue
        if not any("type" in r and "source" in r for r in records):
            harvest.unrecognized += 1
            continue
        role = "interactive" if workspace else "headless"
        times = [parse_time(r["created_at"]) for r in records if r.get("created_at")]
        harvest.add_session("antigravity", conversation, workspace, path, role, times)
        if role != "interactive":
            continue
        for record in records:
            if record.get("type") == "USER_INPUT" and record.get("source") == "USER_EXPLICIT":
                content = record.get("content") or ""
                request = USER_REQUEST.search(content)
                harvest.add_message("antigravity", conversation, workspace, path, parse_time(record["created_at"]),
                                    request.group(1) if request else content)
    return harvest


def antigravity_workspace(db_path):
    """Workspace path from trajectory_metadata_blob field 1.1; None for headless runs, which carry none."""
    if not db_path.exists():
        raise ValueError(f"missing {db_path}")
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as db:
        row = db.execute("select data from trajectory_metadata_blob").fetchone()
    outer = proto_field(row[0], 1) if row else None
    uri = proto_field(outer, 1) if outer else None
    return uri.decode().removeprefix("file://") if uri else None


def proto_field(data, number):
    """First length-delimited value of a top-level protobuf field."""
    i = 0
    while i < len(data):
        key, i = varint(data, i)
        field, wire = key >> 3, key & 7
        if wire == 0:
            value, i = varint(data, i)
        elif wire == 2:
            length, i = varint(data, i)
            value, i = data[i:i + length], i + length
        elif wire in (1, 5):
            i += 8 if wire == 1 else 4
            continue
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        if field == number and wire == 2:
            return value
    return None


def varint(data, i):
    result = shift = 0
    while True:
        byte = data[i]
        i += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return result, i


def write_slices(out, messages, sessions, count, since, until):
    """Splits messages into contiguous time slices of near-equal size covering the whole window."""
    count = max(1, min(count, len(messages)))
    size, extra = divmod(len(messages), count)
    groups, start = [], 0
    for index in range(count):
        end = start + size + (index < extra)
        groups.append(messages[start:end])
        start = end
    slices = []
    for index, group in enumerate(groups):
        begin = since if index == 0 else group[0]["time"]
        end = until if index == count - 1 else groups[index + 1][0]["time"]
        active = [s for s in sessions if s["first"] <= end and s["last"] >= begin]
        path = out / f"slice-{index + 1}.json"
        path.write_text(json.dumps({"from": iso(begin), "to": iso(end), "messages": group, "sessions": active},
                                   indent=1, default=iso))
        slices.append({"file": str(path), "from": iso(begin), "to": iso(end), "messages": len(group),
                       "sessions": len(active)})
    return slices


def matches_project(value, project):
    if project is None:
        return True
    if value and value.startswith("cursor-slug:"):
        slug = project.strip("/").replace("/", "-").replace(".", "")
        value = value.removeprefix("cursor-slug:")
        return value == slug or value.startswith(slug + "-")
    return bool(value) and (value == project or value.startswith(project.rstrip("/") + "/"))


def count_projects(messages):
    counts = {}
    for message in messages:
        counts[message["project"]] = counts.get(message["project"], 0) + 1
    return dict(sorted(counts.items(), key=lambda item: -item[1]))


def recent(paths, since):
    return sorted(p for p in paths if file_time(p) >= since)


def jsonl(path):
    with open(path, encoding="utf-8", errors="replace") as lines:
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def block_text(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def first_value(records, key):
    return next((r[key] for r in records if r.get(key)), None)


def file_time(path):
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)


def parse_time(value):
    return aware(dt.datetime.fromisoformat(value.replace("Z", "+00:00")))


def aware(value):
    return value if value.tzinfo else value.astimezone()


def iso(value):
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    sys.exit(main())
