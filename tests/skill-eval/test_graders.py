"""Graders decide from the saved workspace and final message; harness side files do not count as edits."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "skill-eval"))
import graders  # noqa: E402


class Graders(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.initial, self.workspace = root / "initial", root / "workspace"
        for d in (self.initial, self.workspace):
            (d / "docs").mkdir(parents=True)
            (d / "docs" / "guide.md").write_text("Use pnpm.\nRun tests.\n")
            (d / "AGENTS.md").write_text("- Use pnpm.\n")

    def grade(self, spec, harness="codex", message="", variant="with", writes=()):
        spec = {"name": "g", **spec}
        run = {"final_message": message, "writes": None if writes is None else list(writes)}
        return graders.run_graders([spec], variant, self.workspace, self.initial, harness, run, ["judge-a"])

    def test_regex_on_file_and_final_message(self):
        self.assertTrue(self.grade({"type": "regex", "path": "AGENTS.md", "pattern": "PNPM", "flags": "i"})["g"]["pass"])
        self.assertFalse(self.grade({"type": "regex", "path": "AGENTS.md", "pattern": "pnpm",
                                     "match": "not_contains"})["g"]["pass"])
        self.assertTrue(self.grade({"type": "regex", "pattern": "^Done", "flags": "m"},
                                   message="Summary\nDone.")["g"]["pass"])
        self.assertFalse(self.grade({"type": "regex", "path": "missing.md", "pattern": "x"})["g"]["pass"])

    def test_unchanged_except_detects_edits_and_new_files(self):
        spec = {"type": "unchanged_except", "allow": []}
        self.assertTrue(self.grade(spec)["g"]["pass"])
        (self.workspace / "docs" / "guide.md").write_text("Use npm.\n")
        self.assertFalse(self.grade(spec)["g"]["pass"])
        self.assertTrue(self.grade({**spec, "allow": ["docs/guide.md"]})["g"]["pass"])
        (self.workspace / "notes.md").write_text("new")
        self.assertFalse(self.grade({**spec, "allow": ["docs/guide.md"]})["g"]["pass"])

    def test_unchanged_except_ignores_harness_side_files_and_git(self):
        (self.workspace / "SOUL.md").write_text("openclaw bootstrap")
        (self.workspace / ".git").mkdir()
        (self.workspace / ".git" / "HEAD").write_text("ref")
        spec = {"type": "unchanged_except", "allow": []}
        self.assertTrue(self.grade(spec, harness="openclaw")["g"]["pass"])
        self.assertFalse(self.grade(spec, harness="codex")["g"]["pass"])

    def test_harness_cannot_hide_an_edit_to_a_file_the_case_started_with(self):
        (self.workspace / "AGENTS.md").write_text("- Use npm.\n")
        self.assertFalse(self.grade({"type": "unchanged_except", "allow": []}, harness="openclaw")["g"]["pass"])

    def test_file_exists(self):
        self.assertTrue(self.grade({"type": "file_exists", "path": "AGENTS.md"})["g"]["pass"])
        self.assertTrue(self.grade({"type": "file_exists", "path": "gone.md", "exists": False})["g"]["pass"])

    def test_grader_limited_to_a_variant_is_skipped_elsewhere(self):
        spec = {"type": "file_exists", "path": "AGENTS.md", "variants": ["with"]}
        self.assertIn("g", self.grade(spec, variant="with"))
        self.assertNotIn("g", self.grade(spec, variant="without"))

    def test_llm_passes_original_and_result_to_each_judge(self):
        calls = []

        def fake_judge(model, criteria, original, subject, label):
            calls.append((model, original, subject, label))
            return {"pass": model == "judge-a", "reason": model}
        (self.workspace / "AGENTS.md").write_text("- Use pnpm.\n- New rule.\n")
        with mock.patch.object(graders, "judge", fake_judge):
            result = graders.run_graders([{"name": "g", "type": "llm", "path": "AGENTS.md", "criteria": "c"}],
                                         "with", self.workspace, self.initial, "codex",
                                         {"final_message": "", "writes": []}, ["judge-a", "judge-b"])
        self.assertTrue(result["g"]["pass"])
        self.assertEqual(set(result["g"]["judges"]), {"judge-a", "judge-b"})
        self.assertEqual(calls[0][1:], ("- Use pnpm.\n", "- Use pnpm.\n- New rule.\n", "AGENTS.md"))

    def test_final_message_graders_are_undecided_without_a_complete_transcript(self):
        self.assertIsNone(self.grade({"type": "regex", "pattern": "x"}, message=None)["g"]["pass"])
        self.assertIsNone(self.grade({"type": "llm", "criteria": "c"}, message=None)["g"]["pass"])
        self.assertTrue(self.grade({"type": "regex", "path": "AGENTS.md", "pattern": "pnpm"}, message=None)["g"]["pass"])

    def test_no_writes_reads_the_transcript_not_the_end_state(self):
        self.assertTrue(self.grade({"type": "no_writes"})["g"]["pass"])
        self.assertFalse(self.grade({"type": "no_writes"}, writes=["/app/AGENTS.md"])["g"]["pass"])
        self.assertIsNone(self.grade({"type": "no_writes"}, writes=None)["g"]["pass"])
        self.assertTrue(self.grade({"type": "no_writes"}, harness="openclaw",
                                   writes=["/app/MEMORY.md", "/tmp/scratch.txt"])["g"]["pass"])
        self.assertFalse(self.grade({"type": "no_writes"}, writes=["docs/guide.md"])["g"]["pass"])

    def test_judge_verdict_must_be_a_boolean(self):
        self.assertTrue(graders.parse_verdict('{"pass": true, "reason": "ok"}')["pass"])
        self.assertFalse(graders.parse_verdict('Sure: {"pass": false, "reason": "no"}')["pass"])
        for reply in ('{"pass": "false"}', '{"pass": null}', '{"reason": "x"}', "{not json}", "no json"):
            self.assertIsNone(graders.parse_verdict(reply)["pass"], reply)

    def test_failed_judge_call_is_undecided(self):
        import urllib.error
        with mock.patch.object(graders, "_post", side_effect=urllib.error.URLError("down")):
            self.assertIsNone(graders.judge("claude-x", "c", "o", "s", "f")["pass"])

    def test_initial_workspace_runs_scaffold_beside_its_fixture(self):
        case = Path(self._tmp.name) / "case"
        (case / "fixture").mkdir(parents=True)
        (case / "fixture" / "a.txt").write_text("a")
        (case / "scaffold.sh").write_text('cp -R "$(dirname "$0")/fixture/." . && echo b > b.txt\n')
        with graders.temporary_initial_workspace(case) as initial:
            self.assertEqual(sorted(p.name for p in initial.iterdir()), ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
