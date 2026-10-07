"""verify-run.py accepts a headless run only when its output protocol completed."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "spawn-agent" / "scripts" / "verify-run.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class VerifyRun(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def verify(self, harness, stdout, *flags, stderr=None):
        out = self.tmp / "run.out"
        out.write_text(stdout)
        if "--exit-code" not in flags:
            flags = (*flags, "--exit-code", "0")
        args = [sys.executable, str(SCRIPT), "--harness", harness, "--stdout", str(out), *flags]
        if stderr is not None:
            err = self.tmp / "run.err"
            err.write_text(stderr)
            args += ["--stderr", str(err)]
        completed = subprocess.run(args, capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def fixture(self, name):
        return (FIXTURES / f"{name}.out").read_text()

    def test_accepts_every_captured_success(self):
        """Given each harness's real success output in json and stream form, when verified, then it completes with a session id and the response text."""
        for name in ["claude-json", "claude-stream", "codex-stream", "antigravity-json", "antigravity-stream", "cursor-json", "cursor-stream"]:
            with self.subTest(name=name):
                code, report = self.verify(name.split("-")[0], self.fixture(name), "--exit-code", "0")
                self.assertEqual(code, 0, report)
                self.assertEqual(report["status"], "completed")
                self.assertTrue(report["session_id"])
                self.assertEqual(Path(report["result_file"]).read_text().strip(), "OK")

    def test_nonzero_exit_fails_before_parsing(self):
        """Given a success stream but exit code 124 from the host timeout, when verified, then it fails naming the timeout."""
        code, report = self.verify("claude", self.fixture("claude-json"), "--exit-code", "124")
        self.assertEqual(code, 1)
        self.assertIn("timeout", report["reason"])

    def test_claude_error_result_fails(self):
        """Given a Claude result with is_error true, when verified, then it fails and reports the subtype."""
        result = json.loads(self.fixture("claude-json"))
        result.update(subtype="error_during_execution", is_error=True)
        code, report = self.verify("claude", json.dumps(result))
        self.assertEqual(code, 1)
        self.assertIn("error_during_execution", report["reason"])

    def test_claude_permission_denial_fails_with_notice(self):
        """Given a Claude success result that recorded a denied tool call, when verified, then it fails and lists the denial."""
        result = json.loads(self.fixture("claude-json"))
        result["permission_denials"] = [{"tool_name": "Bash", "tool_input": {"command": "npm test"}}]
        code, report = self.verify("claude", json.dumps(result))
        self.assertEqual(code, 1)
        self.assertIn("denied", report["reason"])
        self.assertIn("Bash", report["permission_notices"][0])

    def test_codex_stream_without_terminal_event_fails(self):
        """Given a Codex stream that ends before turn.completed, when verified, then it fails naming the missing event."""
        lines = self.fixture("codex-stream").splitlines()[:-1]
        code, report = self.verify("codex", "\n".join(lines) + "\n")
        self.assertEqual(code, 1)
        self.assertIn("turn.completed", report["reason"])

    def test_codex_turn_failed_fails(self):
        """Given a Codex stream with a turn.failed event, when verified, then it fails with the event's error."""
        lines = self.fixture("codex-stream").splitlines()[:-1]
        lines.append(json.dumps({"type": "turn.failed", "error": {"message": "context window exceeded"}}))
        code, report = self.verify("codex", "\n".join(lines) + "\n")
        self.assertEqual(code, 1)
        self.assertIn("context window exceeded", report["reason"])

    def test_antigravity_non_success_status_fails(self):
        """Given an Antigravity result whose status is WAITING, when verified, then it fails naming the status."""
        result = json.loads(self.fixture("antigravity-json"))
        result["status"] = "WAITING"
        code, report = self.verify("antigravity", json.dumps(result))
        self.assertEqual(code, 1)
        self.assertIn("WAITING", report["reason"])

    def test_antigravity_stream_needs_exactly_one_result(self):
        """Given an Antigravity stream with two result events, when verified, then it fails."""
        stream = self.fixture("antigravity-stream")
        last = stream.rstrip("\n").splitlines()[-1]
        code, report = self.verify("antigravity", stream + last + "\n")
        self.assertEqual(code, 1)
        self.assertIn("2 terminal", report["reason"])

    def test_malformed_stream_fails(self):
        """Given a Cursor stream with a truncated last line, when verified, then it fails naming the line."""
        stream = self.fixture("cursor-stream").rstrip("\n")[:-20]
        code, report = self.verify("cursor", stream)
        self.assertEqual(code, 1)
        self.assertIn("not JSON", report["reason"])

    def test_stderr_notice_is_reported_without_failing(self):
        """Given a successful run whose stderr mentions a soft-denied operation, when verified, then it completes but lists the notice and a reason to inspect."""
        code, report = self.verify("antigravity", self.fixture("antigravity-json"), stderr="warn: run_command was soft-denied; left at ask\n")
        self.assertEqual(code, 0)
        self.assertEqual(len(report["permission_notices"]), 1)
        self.assertIn("inspect", report["reason"])

    def test_text_format_only_checks_exit_and_output(self):
        """Given a text-format run with exit 0, when verified, then it completes with the text as the result and no session id."""
        code, report = self.verify("cursor", "The API has two functions.\n", "--format", "text", "--exit-code", "0")
        self.assertEqual(code, 0)
        self.assertIsNone(report["session_id"])
        self.assertEqual(Path(report["result_file"]).read_text(), "The API has two functions.\n")

    def test_unreadable_input_is_usage_error(self):
        """Given a missing stdout file or a missing exit code, when verified, then it exits 2."""
        completed = subprocess.run([sys.executable, str(SCRIPT), "--harness", "claude", "--stdout", str(self.tmp / "missing"), "--exit-code", "0"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        (self.tmp / "run.out").write_text(self.fixture("claude-json"))
        completed = subprocess.run([sys.executable, str(SCRIPT), "--harness", "claude", "--stdout", str(self.tmp / "run.out")], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)

    def test_non_json_output_fails_unless_text_was_requested(self):
        """Given stdout that is a JSON array or a banner where JSON was expected, when verified, then it fails instead of passing as text."""
        for stdout in ["[]\n", "null\n", "Error: workspace not trusted\n"]:
            with self.subTest(stdout=stdout):
                code, report = self.verify("cursor", stdout)
                self.assertEqual(code, 1, report)
                self.assertEqual(report["status"], "failed")

    def test_result_without_result_text_fails(self):
        """Given a Cursor success result missing its result field, when verified, then it fails naming the field."""
        result = json.loads(self.fixture("cursor-json"))
        del result["result"]
        code, report = self.verify("cursor", json.dumps(result))
        self.assertEqual(code, 1)
        self.assertIn("result text", report["reason"])

    def test_lifecycle_order_is_enforced(self):
        """Given an Antigravity stream whose result precedes init, or a Codex stream that continues after turn.completed, when verified, then both fail."""
        lines = self.fixture("antigravity-stream").rstrip("\n").splitlines()
        code, report = self.verify("antigravity", "\n".join([lines[-1], *lines[:-1]]) + "\n")
        self.assertEqual(code, 1)
        self.assertIn("init", report["reason"])
        codex = self.fixture("codex-stream") + json.dumps({"type": "turn.started"}) + "\n"
        code, report = self.verify("codex", codex)
        self.assertEqual(code, 1)
        self.assertIn("continues after", report["reason"])

    def test_cursor_sandbox_startup_error_fails(self):
        """Given a successful Cursor result but a sandbox startup error on stderr, when verified, then it fails."""
        code, report = self.verify("cursor", self.fixture("cursor-json"), stderr="sandbox startup error: unsupported on this host\n")
        self.assertEqual(code, 1)
        self.assertIn("sandbox", report["reason"])


if __name__ == "__main__":
    unittest.main()
