"""collect-messages.py indexes only user-typed messages from every harness log in the window."""
import datetime as dt
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "retrospect" / "scripts" / "collect-messages.py"
NOW = dt.datetime.now(dt.timezone.utc)


def ago(days):
    return (NOW - dt.timedelta(days=days)).isoformat().replace("+00:00", "Z")


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records))


def claude_typed(text, cwd="/work/app", session="s1", days=1):
    return {"type": "user", "origin": {"kind": "human"}, "message": {"content": text}, "cwd": cwd,
            "sessionId": session, "timestamp": ago(days)}


class CollectMessages(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)

    def run_script(self, *args):
        completed = subprocess.run([sys.executable, str(SCRIPT), "--out", str(self.home / "out"), *args],
                                   capture_output=True, text=True, env={**os.environ, "HOME": str(self.home)})
        summary = json.loads(completed.stdout)
        slices = [json.loads(Path(s["file"]).read_text()) for s in summary.get("slices", [])]
        return completed, summary, slices

    def messages(self, *args):
        _, summary, slices = self.run_script(*args)
        return summary, [m for s in slices for m in s["messages"]]

    def claude_session(self, records, slug="-work-app", session="s1"):
        write_jsonl(self.home / ".claude" / "projects" / slug / f"{session}.jsonl", records)

    def test_claude_code_keeps_typed_and_queued_messages_only(self):
        """Given a Claude Code session with a typed prompt wrapped in IDE blocks, a mid-turn queued message, a tool result, a skill body, a task notification and a subagent file, when collected, then only the two typed texts are indexed, IDE blocks stripped, with the record cwd as project."""
        base = {"cwd": "/work/app", "sessionId": "s1", "timestamp": ago(1)}
        self.claude_session([
            {**claude_typed(None), "message": {"content": [
                {"type": "text", "text": "<ide_opened_file>The user opened a.py</ide_opened_file>"},
                {"type": "text", "text": "stop adding comments"}]}},
            {**base, "type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}},
            {**base, "type": "user", "message": {"content": [{"type": "tool_result", "content": "tool output"}]}},
            {**base, "type": "user", "isMeta": True, "message": {"content": "Base directory for this skill"}},
            {**base, "type": "user", "origin": {"kind": "task-notification"}, "message": {"content": "agent done"}},
            {**base, "type": "attachment", "attachment": {"type": "queued_command", "origin": {"kind": "human"},
                                                          "prompt": [{"type": "text", "text": "use pnpm not npm"}]}},
        ])
        write_jsonl(self.home / ".claude" / "projects" / "-work-app" / "s1" / "subagents" / "agent-a.jsonl",
                    [{**base, "type": "user", "isSidechain": True, "message": {"content": "subagent prompt"}}])

        summary, messages = self.messages()

        self.assertEqual(sorted(m["text"] for m in messages), ["stop adding comments", "use pnpm not npm"])
        self.assertEqual({m["project"] for m in messages}, {"/work/app"})
        self.assertEqual(summary["harnesses"]["claude-code"]["subagent"], 1)

    def test_codex_skips_injected_headless_and_subagent_input(self):
        """Given an interactive Codex session with injected AGENTS.md and an IDE-wrapped request, plus an exec session and a subagent session, when collected, then only the request text after '## My request:' is indexed and the exec and subagent sessions are counted as excluded."""
        day = self.home / ".codex" / "sessions" / "2026" / "10" / "09"

        def session(name, meta, text):
            write_jsonl(day / f"rollout-{name}.jsonl", [
                {"timestamp": ago(1), "type": "session_meta", "payload": {"id": name, "cwd": "/work/app", **meta}},
                {"timestamp": ago(1), "type": "response_item", "payload": {
                    "type": "message", "role": "user",
                    "content": [{"type": "input_text", "text": "# AGENTS.md instructions for /work/app"}]}},
                {"timestamp": ago(1), "type": "event_msg", "payload": {
                    "type": "item_completed", "item": {"type": "UserMessage", "content": [{"type": "text", "text": text}]}}},
            ])

        session("c1", {"originator": "codex_vscode", "source": "vscode"},
                "# Context from my IDE setup:\n\n## Active file: a.py\n\n## My request:\nrun the tests first")
        session("c2", {"originator": "codex_exec", "source": "exec"}, "You are a managed task participant.")
        session("c3", {"originator": "codex_vscode", "source": {"subagent": {"thread_spawn": {"parent_thread_id": "c1"}}}},
                "copied parent message")

        summary, messages = self.messages()

        self.assertEqual([m["text"] for m in messages], ["run the tests first"])
        codex = summary["harnesses"]["codex"]
        self.assertEqual((codex["headless"], codex["subagent"]), (1, 1))

    def test_cursor_extracts_user_query_with_local_timestamp(self):
        """Given a Cursor transcript whose first user record is injected context and whose second holds a <user_query> with a UTC+8 <timestamp>, plus a subagent transcript, when collected, then one message is indexed with its UTC time and the slug resolved to the existing project directory."""
        project = self.home / "work" / "my.app"
        project.mkdir(parents=True)
        slug = str(project).strip("/").replace("/", "-").replace(".", "")
        sent = (NOW - dt.timedelta(days=1)).replace(second=0, microsecond=0)
        local = sent.astimezone(dt.timezone(dt.timedelta(hours=8)))
        stamp = f"{local:%A}, {local:%b} {local.day}, {local.year}, {local.hour % 12 or 12}:{local:%M %p} (UTC+8)"
        chat = self.home / ".cursor" / "projects" / slug / "agent-transcripts" / "chat1"
        write_jsonl(chat / "chat1.jsonl", [
            {"role": "user", "message": {"content": [{"type": "text", "text": "<user_info>OS linux</user_info><rules>r</rules>"}]}},
            {"role": "user", "message": {"content": [{"type": "text", "text":
                f"<timestamp>{stamp}</timestamp>\n<user_query>\nkeep answers short\n</user_query>"}]}},
            {"role": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}},
            {"type": "turn_ended", "status": "success"},
        ])
        write_jsonl(chat / "subagents" / "sub1.jsonl",
                    [{"role": "user", "message": {"content": [{"type": "text", "text": "<user_query>subagent work</user_query>"}]}}])

        _, messages = self.messages()

        self.assertEqual([(m["text"], m["project"]) for m in messages], [("keep answers short", str(project))])
        self.assertEqual(messages[0]["time"], sent.isoformat().replace("+00:00", "Z"))

    def test_antigravity_keeps_interactive_and_excludes_headless(self):
        """Given one Antigravity conversation with a workspace and one without, when collected, then the first's <USER_REQUEST> text is indexed under its workspace path and the second is counted as headless."""
        root = self.home / ".gemini" / "antigravity-cli"
        (root / "conversations").mkdir(parents=True)

        def conversation(name, blob, request):
            with sqlite3.connect(root / "conversations" / f"{name}.db") as db:
                db.execute("create table trajectory_metadata_blob (id text, data blob)")
                db.execute("insert into trajectory_metadata_blob values ('main', ?)", (blob,))
            write_jsonl(root / "brain" / name / ".system_generated" / "logs" / "transcript_full.jsonl", [
                {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "created_at": ago(1),
                 "content": f"<USER_REQUEST>\n{request}\n</USER_REQUEST><ADDITIONAL_METADATA>m</ADDITIONAL_METADATA>"},
                {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "created_at": ago(1), "content": "sure"},
            ])

        uri = b"file:///work/ag"
        inner = b"\x0a" + bytes([len(uri)]) + uri
        conversation("g1", b"\x0a" + bytes([len(inner)]) + inner, "explain the diff")
        conversation("g2", b"\x12\x00", "Reply with exactly the word OK")

        summary, messages = self.messages()

        self.assertEqual([(m["text"], m["project"]) for m in messages], [("explain the diff", "/work/ag")])
        self.assertEqual(summary["harnesses"]["antigravity"]["headless"], 1)

    def test_window_starts_at_later_of_stamp_and_fourteen_days(self):
        """Given a stamp three days old, when collected, then the window starts at the stamp and older messages are left out; given no stamp, it starts fourteen days ago; given --since, that time wins."""
        self.claude_session([claude_typed("fifteen days", days=15), claude_typed("five days", days=5),
                             claude_typed("one day", days=1)])

        _, messages = self.messages()
        self.assertEqual([m["text"] for m in messages], ["five days", "one day"])

        _, messages = self.messages("--since", ago(20))
        self.assertEqual([m["text"] for m in messages], ["fifteen days", "five days", "one day"])

        (self.home / ".agents").mkdir()
        (self.home / ".agents" / "retrospect-last-run").write_text(ago(3) + "\n")
        summary, messages = self.messages()
        self.assertEqual([m["text"] for m in messages], ["one day"])
        self.assertEqual(summary["window"]["since"], ago(3))

    def test_sessions_invoking_retrospect_are_excluded(self):
        """Given a session whose typed message invokes /retrospect, when collected, then none of its messages are indexed and its id is listed as excluded."""
        self.claude_session([claude_typed("keep this")])
        self.claude_session([claude_typed("<command-message>retrospect</command-message>\n<command-name>/retrospect</command-name>",
                                          session="s2"),
                             claude_typed("only the last week", session="s2")], session="s2")

        summary, messages = self.messages()

        self.assertEqual([m["text"] for m in messages], ["keep this"])
        self.assertEqual(summary["excluded_sessions"], [{"harness": "claude-code", "session": "s2"}])

    def test_project_filter_keeps_project_and_subdirectories(self):
        """Given messages from /p, /p/sub and /q, when collected with --project /p, then only the /p and /p/sub messages are indexed."""
        for cwd in ["/p", "/p/sub", "/q", "/pq"]:
            session = cwd.strip("/").replace("/", "-")
            self.claude_session([claude_typed(f"from {cwd}", cwd=cwd, session=session)], session=session)

        _, messages = self.messages("--project", "/p")

        self.assertEqual(sorted(m["text"] for m in messages), ["from /p", "from /p/sub"])

    def test_missing_and_unrecognized_logs_are_reported(self):
        """Given no Codex directory and a Claude Code session whose user records lack origin, when collected, then Codex is reported absent and Claude Code reports the file as unrecognized instead of a silent zero."""
        record = claude_typed("old format")
        del record["origin"]
        self.claude_session([record])

        summary, messages = self.messages()

        self.assertEqual(messages, [])
        self.assertEqual(summary["harnesses"]["codex"]["status"], "absent")
        claude = summary["harnesses"]["claude-code"]
        self.assertEqual((claude["status"], claude["unrecognized_files"]), ("unrecognized", 1))

    def test_slices_partition_messages_in_time_order(self):
        """Given six messages and --slices 3, when collected, then three slice files hold two messages each, in time order, with every message in exactly one slice."""
        self.claude_session([claude_typed(f"m{day}", days=day) for day in [6, 2, 5, 1, 4, 3]])

        _, _, slices = self.run_script("--slices", "3")

        self.assertEqual([[m["text"] for m in s["messages"]] for s in slices], [["m6", "m5"], ["m4", "m3"], ["m2", "m1"]])

    def test_stdout_carries_no_message_text(self):
        """Given typed messages, when collected, then stdout holds the summary without any message text."""
        self.claude_session([claude_typed("a private remark about the deploy")])

        completed, summary, slices = self.run_script()

        self.assertEqual(slices[0]["messages"][0]["text"], "a private remark about the deploy")
        self.assertNotIn("private remark", completed.stdout)


if __name__ == "__main__":
    unittest.main()
