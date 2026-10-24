"""Graders decide from the saved workspace and final message; harness side files do not count as edits."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
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

    def test_llm_outputs_with_one_criterion_go_to_each_judge_in_one_call(self):
        calls = []

        def fake_judge(model, criteria, original, subjects, label):
            calls.append((model, original, sorted(subjects), label))
            return [{"pass": model == "judge-a" and s.endswith("New rule.\n"), "reason": model} for s in subjects]
        spec = [{"name": "g", "type": "llm", "path": "AGENTS.md", "criteria": "c"}]
        rows = [{"graders": graders.run_graders(spec, "with", self.workspace, self.initial, "codex",
                                                {"final_message": "", "writes": []}, ["judge-a", "judge-b"])}]
        (self.workspace / "AGENTS.md").write_text("- Use pnpm.\n- New rule.\n")
        rows.append({"graders": graders.run_graders(spec, "with", self.workspace, self.initial, "codex",
                                                    {"final_message": "", "writes": []}, ["judge-a", "judge-b"])})
        with mock.patch.object(graders, "judge", fake_judge):
            graders.judge_pending(rows, ["judge-a", "judge-b"])
        self.assertEqual([c[0] for c in calls], ["judge-a", "judge-b"])
        self.assertEqual(calls[0][1:], ("- Use pnpm.\n", ["- Use pnpm.\n", "- Use pnpm.\n- New rule.\n"], "AGENTS.md"))
        self.assertEqual([r["graders"]["g"]["pass"] for r in rows], [False, True])
        self.assertEqual(set(rows[1]["graders"]["g"]["judges"]), {"judge-a", "judge-b"})
        self.assertNotIn("pending", rows[1]["graders"]["g"])

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

    def test_each_judge_verdict_must_be_a_boolean(self):
        verdicts = graders.parse_verdicts('Sure: [{"id": 2, "pass": false, "reason": "no"}, '
                                          '{"id": 1, "pass": true}, {"id": 3, "pass": "true"}]', 4)
        self.assertEqual([v["pass"] for v in verdicts], [True, False, None, None])
        for reply in ('{"pass": true}', "[not json]", "no json"):
            self.assertEqual([v["pass"] for v in graders.parse_verdicts(reply, 2)], [None, None], reply)

    def test_failed_judge_call_is_undecided(self):
        import urllib.error
        with mock.patch.object(graders, "_post", side_effect=urllib.error.URLError("down")):
            self.assertEqual([v["pass"] for v in graders.judge("claude-x", "c", "o", ["s", "t"], "f")], [None, None])

    def test_large_groups_split_across_calls(self):
        results = [{"pending": {"subject": "x" * (graders.BATCH_CHARS // 2 + 1)}} for _ in range(3)]
        self.assertEqual([len(b) for b in graders._batches(results)], [1, 1, 1])

    def test_initial_workspace_runs_scaffold_beside_its_fixture(self):
        case = Path(self._tmp.name) / "case"
        (case / "fixture").mkdir(parents=True)
        (case / "fixture" / "a.txt").write_text("a")
        (case / "scaffold.sh").write_text('cp -R "$(dirname "$0")/fixture/." . && echo b > b.txt\n')
        with graders.temporary_initial_workspace(case) as initial:
            self.assertEqual(sorted(p.name for p in initial.iterdir()), ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
