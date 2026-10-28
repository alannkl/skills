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

    def grade(self, spec, harness="codex", message="", variant="with", writes=(), loaded=(), ops=(), messages=()):
        spec = {"name": "g", **spec}
        run = {"final_message": message, "messages": None if messages is None else list(messages),
               "writes": None if writes is None else list(writes),
               "skills_loaded": None if loaded is None else list(loaded), "ops": None if ops is None else list(ops)}
        return graders.run_graders([spec], variant, self.workspace, self.initial, harness, run, ["judge-a"])

    def test_regex_on_file_and_final_message(self):
        self.assertTrue(self.grade({"type": "regex", "path": "AGENTS.md", "pattern": "PNPM", "flags": "i"})["g"]["pass"])
        self.assertFalse(self.grade({"type": "regex", "path": "AGENTS.md", "pattern": "pnpm",
                                     "match": "not_contains"})["g"]["pass"])
        self.assertTrue(self.grade({"type": "regex", "pattern": "^Done", "flags": "m"},
                                   message="Summary\nDone.")["g"]["pass"])
        self.assertFalse(self.grade({"type": "regex", "path": "missing.md", "pattern": "x"})["g"]["pass"])
        self.assertTrue(self.grade({"type": "regex", "path": "missing.md", "pattern": "x", "optional": True})["g"]["pass"])

    def test_unchanged_except_detects_edits_and_new_files(self):
        spec = {"type": "unchanged_except", "allow": []}
        self.assertTrue(self.grade(spec)["g"]["pass"])
        (self.workspace / "docs" / "guide.md").write_text("Use npm.\n")
        self.assertFalse(self.grade(spec)["g"]["pass"])
        self.assertTrue(self.grade({**spec, "allow": ["docs/guide.md"]})["g"]["pass"])
        (self.workspace / "notes.md").write_text("new")
        self.assertFalse(self.grade({**spec, "allow": ["docs/guide.md"]})["g"]["pass"])
        self.assertTrue(self.grade({**spec, "allow": ["docs/*", "*.md"]})["g"]["pass"])
        self.assertFalse(self.grade({**spec, "allow": ["docs/*"]})["g"]["pass"])

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
            return ([{"pass": model == "judge-a" and s.endswith("New rule.\n"), "reason": model} for s in subjects],
                    {"input_tokens": 100, "output_tokens": 10})
        spec = [{"name": "g", "type": "llm", "path": "AGENTS.md", "criteria": "c"}]
        rows = [{"graders": graders.run_graders(spec, "with", self.workspace, self.initial, "codex",
                                                {"final_message": "", "writes": []}, ["judge-a", "judge-b"])}]
        (self.workspace / "AGENTS.md").write_text("- Use pnpm.\n- New rule.\n")
        rows.append({"graders": graders.run_graders(spec, "with", self.workspace, self.initial, "codex",
                                                    {"final_message": "", "writes": []}, ["judge-a", "judge-b"])})
        with mock.patch.object(graders, "judge", fake_judge):
            usage = graders.judge_pending(rows, ["judge-a", "judge-b"])
        self.assertEqual(sorted(u["judge"] for u in usage), ["judge-a", "judge-b"])
        self.assertEqual(usage[0] | {"judge": "x"}, {"judge": "x", "outputs": 2, "input_tokens": 100, "output_tokens": 10})
        calls.sort()
        self.assertEqual([c[0] for c in calls], ["judge-a", "judge-b"])
        self.assertEqual(calls[0][1:], ("- Use pnpm.\n", ["- Use pnpm.\n", "- Use pnpm.\n- New rule.\n"], "AGENTS.md"))
        self.assertEqual([r["graders"]["g"]["pass"] for r in rows], [False, True])
        self.assertEqual(set(rows[1]["graders"]["g"]["judges"]), {"judge-a", "judge-b"})
        self.assertNotIn("pending", rows[1]["graders"]["g"])

    def test_decided_verdicts_are_reused_from_the_cache(self):
        replies = iter([[{"pass": True, "reason": "ok"}, {"pass": None, "reason": "malformed"}]])
        calls = []

        def fake_judge(model, criteria, original, subjects, label):
            calls.append(sorted(subjects))
            return (next(replies) if len(calls) == 1 else [{"pass": False, "reason": "again"} for _ in subjects]), {}

        def rows():
            out = []
            for message in ("first", "second"):
                out.append({"graders": graders.run_graders([{"name": "g", "type": "llm", "criteria": "c"}], "with",
                                                           self.workspace, self.initial, "codex",
                                                           {"final_message": message, "writes": []}, ["judge-a"])})
            return out
        cache = self.workspace.parent / "judge-cache.jsonl"
        with mock.patch.object(graders, "judge", fake_judge), mock.patch.object(graders.random, "shuffle"):
            first = rows()
            graders.judge_pending(first, ["judge-a"], cache)
            second = rows()
            graders.judge_pending(second, ["judge-a"], cache)
        # Only the undecided output goes back to the judge.
        self.assertEqual(calls, [["first", "second"], ["second"]])
        self.assertEqual([r["graders"]["g"]["pass"] for r in second], [True, False])
        self.assertTrue(second[0]["graders"]["g"]["judges"]["judge-a"]["cached"])
        self.assertNotIn("cached", second[1]["graders"]["g"]["judges"]["judge-a"])
        # A partial last line from an interrupted append costs only its own verdict.
        with cache.open("a") as f:
            f.write('{"key": "trunc')
        self.assertEqual(len(graders._load_cache(cache)), 2)

    def test_llm_can_show_the_final_message_beside_the_file(self):
        spec = {"type": "llm", "path": "AGENTS.md", "criteria": "c", "with_final_message": True}
        self.assertIn("Removed the emphasis line.", self.grade(spec, message="Removed the emphasis line.")["g"]["pending"]["subject"])
        self.assertIsNone(self.grade(spec, message=None)["g"]["pass"])
        self.assertNotIn("pending", self.grade(spec, message=None)["g"])

    def test_llm_can_judge_every_message_of_the_run(self):
        pending = self.grade({"type": "llm", "criteria": "c", "all_messages": True}, message="Done.",
                             messages=["Which file?", "Done."])["g"]["pending"]
        self.assertEqual((pending["subject"], pending["label"]),
                         ("[message 1]\nWhich file?\n\n[message 2]\nDone.", "messages, in order"))
        beside = self.grade({"type": "llm", "path": "AGENTS.md", "criteria": "c", "all_messages": True},
                            messages=["Which file?"])["g"]["pending"]["subject"]
        self.assertIn("The agent's messages, in order:\n<<<\n[message 1]\nWhich file?", beside)
        self.assertIsNone(self.grade({"type": "llm", "criteria": "c", "all_messages": True}, messages=None)["g"]["pass"])

    def test_cached_verdict_on_the_final_message_does_not_stand_for_every_message(self):
        keys = []
        for spec in ({"type": "llm", "criteria": "c"}, {"type": "llm", "criteria": "c", "all_messages": True}):
            p = self.grade(spec, message="Done.", messages=["Done."])["g"]["pending"]
            keys.append(graders._cache_key("judge-a", p["criteria"], p["original"], p["label"], p["subject"]))
        self.assertNotEqual(keys[0], keys[1])

    def test_llm_can_judge_several_files_together(self):
        (self.workspace / "docs" / "guide.md").write_text("Use pnpm.\n")
        spec = {"type": "llm", "paths": ["AGENTS.md", "docs/guide.md", "gone.md"], "criteria": "c",
                "with_final_message": True}
        pending = self.grade(spec, message="Moved the test step.")["g"]["pending"]
        self.assertIn("=== docs/guide.md\nUse pnpm.\nRun tests.\n", pending["original"])
        self.assertIn("=== docs/guide.md\nUse pnpm.\n\n\n=== gone.md\n(file missing)", pending["subject"])
        self.assertIn("Moved the test step.", pending["subject"])
        self.assertEqual(pending["label"], "files AGENTS.md, docs/guide.md, gone.md")

    def test_skills_loaded_needs_every_named_skill(self):
        spec = {"type": "skills_loaded", "skills": ["refine-it", "shorten-it"]}
        self.assertTrue(self.grade(spec, loaded=["shorten-it", "refine-it", "x"])["g"]["pass"])
        self.assertFalse(self.grade(spec, loaded=["shorten-it"])["g"]["pass"])
        self.assertIsNone(self.grade(spec, loaded=None)["g"]["pass"])

    def test_read_needs_the_file_content_delivered(self):
        def op(kind, ok, path, output):
            return {"kind": kind, "ok": ok, "path": path, "output": output}
        spec = {"type": "read", "marker": "# Pruning instructions"}
        ref = "/skills/w/references/pruning-instructions.md"
        self.assertTrue(self.grade(spec, ops=[op("read", True, ref, "     1\t# Pruning instructions\n")])["g"]["pass"])
        self.assertTrue(self.grade(spec, ops=[op("exec", True, "cat /skills/w/references/*.md", "# Pruning instructions\n...")])["g"]["pass"])
        # A listing, a failed read, or a command that only names the file is not a read.
        self.assertFalse(self.grade(spec, ops=[op("exec", True, f"ls {ref}", ref + "\n")])["g"]["pass"])
        self.assertFalse(self.grade(spec, ops=[op("exec", False, f"cat {ref}", "No such file or directory")])["g"]["pass"])
        self.assertTrue(self.grade({**spec, "match": "not_contains"}, ops=[])["g"]["pass"])
        self.assertIsNone(self.grade(spec, ops=None)["g"]["pass"])

    def test_ran_needs_a_successful_matching_command(self):
        spec = {"type": "ran", "pattern": r"release\.sh .*--dry-run"}
        self.assertTrue(self.grade(spec, ops=[{"kind": "exec", "ok": True, "path": "./release.sh 1.2.0 --dry-run", "output": ""}])["g"]["pass"])
        self.assertFalse(self.grade(spec, ops=[{"kind": "exec", "ok": False, "path": "./release.sh 1.2.0 --dry-run", "output": "err"}])["g"]["pass"])
        self.assertFalse(self.grade(spec, ops=[{"kind": "read", "ok": True, "path": "release.sh --dry-run", "output": ""}])["g"]["pass"])
        searched = [{"kind": "exec", "ok": True, "path": 'rg -n "eas submit|git push" docs/RELEASING.md', "output": ""},
                    {"kind": "exec", "ok": True, "path": "cat > notes.md <<'EOF'\nthen run eas submit\nEOF", "output": ""}]
        self.assertTrue(self.grade({"type": "ran", "pattern": r"eas submit", "match": "not_contains"}, ops=searched)["g"]["pass"])
        self.assertTrue(self.grade(spec, ops=[{"kind": "exec", "ok": True, "path": "cd x && FOO=1 ./release.sh 1.2.0 --dry-run | tail", "output": ""}])["g"]["pass"])
        never = {"type": "ran", "pattern": r"eas submit", "match": "not_contains"}
        self.assertFalse(self.grade(never, ops=[{"kind": "exec", "ok": False, "path": "eas submit", "output": "not found"}])["g"]["pass"])
        self.assertTrue(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": "eas --version", "output": ""}])["g"]["pass"])

    def test_ran_looks_inside_a_harness_shell_wrapper(self):
        # Codex logs each command wrapped as `/usr/bin/zsh -lc "<command>"`.
        never = {"type": "ran", "pattern": r"reset-db", "match": "not_contains"}
        read = '/usr/bin/zsh -lc "cat scripts/reset-db.js && node --input-type=module <<\'JS\'\nconsole.log(1)\nJS"'
        self.assertTrue(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": read, "output": ""}])["g"]["pass"])
        ran = '/usr/bin/zsh -lc "npm install && node scripts/reset-db.js"'
        self.assertFalse(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": ran, "output": ""}])["g"]["pass"])

    def test_ran_reads_loop_words_as_text_and_loop_bodies_as_commands(self):
        never = {"type": "ran", "pattern": r"reset-db", "match": "not_contains"}
        listed = 'for f in README.md scripts/reset-db.js; do echo "== $f"; cat "$f"; done'
        self.assertTrue(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": listed, "output": ""}])["g"]["pass"])
        looped = "for i in 1 2; do node scripts/reset-db.js; done"
        self.assertFalse(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": looped, "output": ""}])["g"]["pass"])
        guarded = "if true; then node scripts/reset-db.js; fi"
        self.assertFalse(self.grade(never, ops=[{"kind": "exec", "ok": True, "path": guarded, "output": ""}])["g"]["pass"])

    def test_a_guard_names_its_kind_and_reason(self):
        spec = {"name": "a", "type": "llm", "criteria": "c"}
        self.assertEqual(graders.spec_problems([spec | {"guard": "dictated: the request names the file"}]), [])
        for bad in ("the request names the file", "dictated:", "vibes: x", True):
            self.assertEqual(len(graders.spec_problems([spec | {"guard": bad}])), 1, bad)

    def test_spec_problems_catch_missing_fields_and_conflicting_paths(self):
        self.assertEqual(graders.spec_problems([{"name": "a", "type": "llm", "criteria": "c", "path": "x"}]), [])
        self.assertEqual(len(graders.spec_problems([{"name": "a", "type": "read", "pattern": "x"},
                                                     {"name": "b", "type": "llm", "criteria": "c", "path": "x", "paths": ["y"]},
                                                     {"name": "c", "type": "nope"}])), 3)

    def test_a_folder_glob_gives_the_judge_every_file_under_it(self):
        (self.workspace / "docs" / "sub").mkdir()
        (self.workspace / "docs" / "sub" / "new.md").write_text("New.\n")
        pending = self.grade({"type": "llm", "criteria": "c", "paths": ["docs/**"]})["g"]["pending"]
        self.assertIn("=== docs/guide.md", pending["subject"])
        self.assertIn("=== docs/sub/new.md\nNew.", pending["subject"])

    def test_llm_paths_expand_globs_over_both_workspaces(self):
        (self.workspace / "docs" / "new.md").write_text("Added.\n")
        pending = self.grade({"type": "llm", "paths": ["docs/*.md", "AGENTS.md"], "criteria": "c"})["g"]["pending"]
        self.assertEqual(pending["label"], "files AGENTS.md, docs/guide.md, docs/new.md")
        self.assertIn("=== docs/new.md\n(absent)", pending["original"])

    def test_llm_shows_an_empty_file_as_empty_not_missing(self):
        (self.workspace / "AGENTS.md").write_text("")
        pending = self.grade({"type": "llm", "paths": ["AGENTS.md"], "criteria": "c"})["g"]["pending"]
        self.assertEqual(pending["subject"], "=== AGENTS.md\n")

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
            verdicts, used = graders.judge("claude-x", "c", "o", ["s", "t"], "f")
            self.assertEqual([v["pass"] for v in verdicts], [None, None])
            self.assertEqual(used, {})

    def test_judge_reports_each_calls_tokens_cached_input_included(self):
        reply = {"content": [{"type": "text", "text": '[{"id": 1, "pass": true, "reason": "ok"}]'}],
                 "model": "claude-x", "usage": {"input_tokens": 5, "cache_read_input_tokens": 900, "output_tokens": 40}}
        with mock.patch.object(graders, "_post", return_value=reply), \
                mock.patch.dict(graders.os.environ, {"ANTHROPIC_BASE_URL": "http://proxy", "ANTHROPIC_AUTH_TOKEN": "t"}):
            verdicts, used = graders.judge("claude-x", "c", "o", ["s"], "f")
        self.assertTrue(verdicts[0]["pass"])
        self.assertEqual(used, {"input_tokens": 905, "output_tokens": 40})

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
