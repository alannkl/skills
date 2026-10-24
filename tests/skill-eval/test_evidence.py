"""Each harness's evidence extractor reports which skills actually reached the agent, and from where."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "skill-eval"))
from evidence import claude_code, codex, openclaw  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class Extractors(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def copy(self, harness: str) -> Path:
        dest = self.tmp / harness
        shutil.copytree(FIXTURES / harness, dest)
        return dest

    def rewrite_lines(self, path: Path, edit) -> None:
        lines = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        kept = [edit(e) for e in lines]
        path.write_text("\n".join(json.dumps(e) for e in kept if e is not None) + "\n")

    def test_claude_code_counts_skill_injected_from_installed_directory(self):
        e = claude_code(FIXTURES / "claude-code")
        self.assertTrue(e["complete"])
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), (["shorten-it"], []))
        self.assertEqual(e["models"], ["claude-haiku-5-5"])
        self.assertIn("shorten-it", e["skills_listed"])
        self.assertIsNotNone(e["cost_usd"])

    def test_claude_code_reports_same_named_skill_from_elsewhere_as_foreign(self):
        agent = self.copy("claude-code")

        def move_base_dir(e):
            return json.loads(json.dumps(e).replace("/logs/agent/sessions/skills/shorten-it", "/opt/builtin/shorten-it"))
        self.rewrite_lines(agent / "claude-code.txt", move_base_dir)
        e = claude_code(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), ([], ["shorten-it"]))

    def test_codex_counts_a_read_that_returned_the_skill(self):
        e = codex(FIXTURES / "codex")
        self.assertEqual(e["skills_loaded"], ["shorten-it"])
        self.assertEqual(e["models"], ["gpt-6-luna"])

    def test_codex_records_file_change_writes(self):
        agent = self.copy("codex")
        change = {"type": "item.completed", "item": {"id": "x", "type": "file_change", "status": "completed",
                                                      "changes": [{"path": "/app/AGENTS.md", "kind": "update"}]}}
        with open(agent / "codex.txt", "a") as f:
            f.write(json.dumps(change) + "\n")
        self.assertEqual(codex(agent)["writes"], ["/app/AGENTS.md"])

    def test_codex_command_that_names_the_skill_without_reading_it_is_not_a_load(self):
        agent = self.copy("codex")

        def existence_check_only(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = "/bin/bash -lc 'test -f /root/.agents/skills/shorten-it/SKILL.md'"
                item["aggregated_output"] = ""
            return e
        self.rewrite_lines(agent / "codex.txt", existence_check_only)
        self.assertEqual(codex(agent)["skills_loaded"], [])

    def test_codex_reading_only_the_frontmatter_is_not_a_load(self):
        agent = self.copy("codex")

        def head_only(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["aggregated_output"] = "---\nname: shorten-it\n"
            return e
        self.rewrite_lines(agent / "codex.txt", head_only)
        self.assertEqual(codex(agent)["skills_loaded"], [])

    def test_codex_same_named_copy_outside_the_install_root_is_foreign(self):
        agent = self.copy("codex")

        def elsewhere(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = item["command"].replace("/root/.agents/skills/", "/opt/builtin/.agents/skills/")
            return e
        self.rewrite_lines(agent / "codex.txt", elsewhere)
        e = codex(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), ([], ["shorten-it"]))

    def test_codex_read_of_the_task_skills_dir_counts_as_the_installed_copy(self):
        agent = self.copy("codex")

        def from_skills_dir(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = item["command"].replace("/root/.agents/skills/", "/skills/")
            return e
        self.rewrite_lines(agent / "codex.txt", from_skills_dir)
        e = codex(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), (["shorten-it"], []))

    def test_codex_transcript_without_turn_completed_is_unknown(self):
        agent = self.copy("codex")
        self.rewrite_lines(agent / "codex.txt", lambda e: None if e.get("type") == "turn.completed" else e)
        e = codex(agent)
        self.assertFalse(e["complete"])
        self.assertIsNone(e["skills_loaded"])
        self.assertIsNone(e["writes"])

    def test_openclaw_counts_reads_but_not_writes_that_mention_the_skill(self):
        e = openclaw(FIXTURES / "openclaw")
        self.assertEqual(e["skills_loaded"], ["shorten-it"])
        self.assertEqual(e["models"], ["deepseek/deepseek-v4.1-flash-1017"])
        self.assertIs(e["rerouted"], False)
        self.assertEqual(e["thinking"], "high")
        agent = self.copy("openclaw")

        def note_instead_of_read(e):
            args = e["data"].get("args", {})
            if "SKILL.md" in args.get("path", ""):
                e["data"]["name"] = "write"
            return e
        self.rewrite_lines(agent / "openclaw-trajectory" / "events.jsonl", note_instead_of_read)
        e = openclaw(agent)
        self.assertEqual(e["skills_loaded"], [])
        self.assertIn("$OPENCLAW_STATE_DIR/skills/shorten-it/SKILL.md", e["writes"])

    def test_openclaw_log_line_inside_the_json_envelope_is_skipped(self):
        agent = self.copy("openclaw")
        path = agent / "openclaw.txt"
        lines = path.read_text().splitlines(keepends=True)
        middle = next(i for i, line in enumerate(lines) if line.startswith("  ") and i > 5)
        lines.insert(middle, " [agents/agent-command] [agent] run x ended with stopReason=stop\n")
        path.write_text("".join(lines))
        e = openclaw(agent)
        self.assertTrue(e["complete"])
        self.assertEqual(e["thinking"], "high")

    def test_openclaw_export_without_its_end_event_is_unknown(self):
        agent = self.copy("openclaw")
        self.rewrite_lines(agent / "openclaw-trajectory" / "events.jsonl",
                           lambda e: None if e["type"] == "session.ended" else e)
        e = openclaw(agent)
        self.assertFalse(e["complete"])
        self.assertIsNone(e["writes"])

    def test_missing_transcript_is_unknown_not_absent(self):
        agent = self.copy("openclaw")
        shutil.rmtree(agent / "openclaw-trajectory")
        self.assertIsNone(openclaw(agent)["skills_loaded"])
        self.assertIsNone(claude_code(self.tmp / "empty")["skills_loaded"])
        self.assertIsNone(codex(self.tmp / "empty")["skills_loaded"])


if __name__ == "__main__":
    unittest.main()
