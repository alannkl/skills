"""A trial's row separates infrastructure failures from graded behavior."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
import eval_instructions  # noqa: E402
from eval_instructions import (SETTINGS, agent_args, first_line, grade_trial, harbor_command,  # noqa: E402
                               instruction_files, missing_trials, report, stored_baseline, task_folder)
from tasks import task_digest, without_frontmatter  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SKILL = {"type": "skill", "name": "shorten-it"}
CONFIG = {"harness": "claude-code", "model": "anthropic/claude-haiku-5-5", "effort": "high"}


class GradeTrial(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.cases = root / "evals" / "shorten-it"
        case = self.cases / "shorten-doc"
        (case / "fixture" / "docs").mkdir(parents=True)
        (case / "fixture" / "docs" / "a.md").write_text("A long sentence that says very little.\n")
        (case / "graders.json").write_text(json.dumps({
            "expect_skill_loaded": {"with": True, "without": False},
            "graders": [{"name": "short", "type": "regex", "path": "docs/a.md", "pattern": "^Short\\.$", "flags": "m"},
                        {"name": "only-doc", "type": "unchanged_except", "allow": ["docs/a.md"]}]}))
        self.trial = root / "trial"
        (self.trial / "verifier" / "workspace" / "docs").mkdir(parents=True)
        (self.trial / "verifier" / "workspace" / "docs" / "a.md").write_text("Short.\n")
        (self.trial / "verifier" / "reward.json").write_text('{"snapshot": 1}')
        shutil.copytree(FIXTURES / "claude-code", self.trial / "agent")
        (self.trial / "config.json").write_text(json.dumps({"task": {"path": "/x/tasks/shorten-doc--with"}}))
        (self.trial / "result.json").write_text(json.dumps({"exception_info": None}))

    def test_graded_trial_reports_loaded_skill_and_grader_results(self):
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual((row["status"], row["case"], row["variant"]), ("ok", "shorten-doc", "with"))
        self.assertTrue(row["skill_loaded"])
        self.assertTrue(row["skill_loaded_expected"])
        self.assertEqual({k: v["pass"] for k, v in row["graders"].items()}, {"short": True, "only-doc": True})

    def test_minus_variant_is_graded_and_expected_like_the_with_arm(self):
        (self.trial / "config.json").write_text(json.dumps({"task": {"path": "/x/tasks/shorten-doc--minus-r"}}))
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual((row["variant"], row["skill_loaded_expected"]), ("minus-r", True))
        self.assertIn("short", row["graders"])

    def test_delivered_instruction_file_counts_as_part_of_the_starting_workspace(self):
        delivered = self.cases.parent / "tasks" / "shorten-doc--with" / "environment" / "instructions"
        delivered.mkdir(parents=True)
        (delivered / "AGENTS.md").write_text("# Keep it short\n")
        (self.trial / "verifier" / "workspace" / "AGENTS.md").write_text("# Keep it short\n")
        artifact = {"type": "instruction-file", "path": "AGENTS.md", "as": "AGENTS.md"}
        row = grade_trial(self.trial, "claude-haiku", CONFIG, artifact, self.cases, ["unused"])
        self.assertEqual((row["skill_loaded"], row["delivered"]), (None, True))
        self.assertTrue(row["graders"]["only-doc"]["pass"])

    def test_grading_starts_from_the_file_delivered_to_the_trials_harness(self):
        tasks_root = self.cases.parent / task_folder("CLAUDE.md")
        delivered = tasks_root / "shorten-doc--with" / "environment" / "instructions"
        delivered.mkdir(parents=True)
        (delivered / "CLAUDE.md").write_text("Keep it short\n")
        (self.trial / "verifier" / "workspace" / "CLAUDE.md").write_text("Keep it short\n")
        artifact = {"type": "instruction-file", "path": "constitution/SKILL.md"}
        row = grade_trial(self.trial, "claude-haiku", CONFIG, artifact, self.cases, ["unused"], tasks_root=tasks_root)
        self.assertTrue(row["graders"]["only-doc"]["pass"])
        # Without the setup's own task folder, the file looks added by the agent.
        row = grade_trial(self.trial, "claude-haiku", CONFIG, artifact, self.cases, ["unused"])
        self.assertFalse(row["graders"]["only-doc"]["pass"])

    def test_probe_marker_is_the_first_line_of_the_delivered_text(self):
        text = without_frontmatter("---\nname: constitution\ndescription: d\n---\n\n# Collaboration Constitution\n\nRules.\n")
        self.assertEqual(first_line(text), "Collaboration Constitution")
        self.assertEqual(first_line("\n\nYou answer support questions.\n"), "You answer support questions.")
        self.assertEqual(first_line(""), "")

    def test_report_lists_the_tokens_of_each_loaded_text(self):
        run_dir = Path(self._tmp.name) / "run-tokens"
        run_dir.mkdir()
        (run_dir / "grades.jsonl").write_text("")
        (run_dir / "run.json").write_text(json.dumps({"loaded_tokens": {
            "claude-code-opus-5.5-high": [{"path": "CLAUDE.md", "tokens": 1200, "method": "count_tokens endpoint"}],
            "codex-gpt-6-astra-high": [{"path": "AGENTS.md", "tokens": None, "not_counted": "tiktoken is not installed"}]}}))
        text = report(run_dir)
        self.assertIn("| load path | setup | tokens | method |", text)
        self.assertIn("| CLAUDE.md | claude-code-opus-5.5-high | 1200 | count_tokens endpoint |", text)
        self.assertIn("| AGENTS.md | codex-gpt-6-astra-high | not counted | tiktoken is not installed |", text)

    def test_runs_graded_together_share_judge_calls_and_record_their_usage(self):
        results = Path(self._tmp.name) / "results"
        runs = [results / "run-a", results / "run-b"]
        for run_dir in runs:
            run_dir.mkdir(parents=True)
        judged = []

        def judge_pending(rows, judges, cache_path):
            judged.append([r["run"] for r in rows])
            return [{"judge": "opus", "outputs": 2, "input_tokens": 1500, "output_tokens": 200}]
        with mock.patch.object(eval_instructions, "grade_rows", lambda run_dir, judges, gfr: [{"run": run_dir.name}]), \
                mock.patch.object(eval_instructions, "judge_pending", judge_pending), \
                mock.patch.object(eval_instructions, "report", lambda run_dir: ""):
            eval_instructions.grade(runs, ["opus"])
        self.assertEqual(judged, [["run-a", "run-b"]])
        usage = json.loads((runs[1] / "judge-usage.json").read_text())
        self.assertEqual(usage["graded_with"], ["run-a", "run-b"])
        lines = eval_instructions.judge_usage(usage, "run-b")
        self.assertIn("Judge calls in the last grading, shared with run-a:", lines)
        self.assertIn("- opus: 1 calls, 2 outputs, in 1.5k out 0.2k tokens", lines)

    def test_infrastructure_failure_is_not_graded(self):
        (self.trial / "result.json").write_text(json.dumps({"exception_info": {"exception_type": "AgentSetupTimeoutError"}}))
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual((row["status"], row["error"]), ("infra_error", "AgentSetupTimeoutError"))
        self.assertNotIn("graders", row)

    def test_attempts_harbor_never_produced_are_reported_missing(self):
        meta = {"tasks": ["shorten-doc--with", "shorten-doc--without"], "attempts": 2}
        graded = [{"case": "shorten-doc", "variant": "with"}]
        missing = missing_trials(meta, "claude-haiku", CONFIG, graded)
        self.assertEqual(sorted((m["variant"], m["status"]) for m in missing),
                         [("with", "missing"), ("without", "missing"), ("without", "missing")])

    def test_missing_or_partial_snapshot_is_missing_evidence(self):
        (self.trial / "verifier" / "reward.json").unlink()
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual(row["status"], "missing_evidence")
        shutil.rmtree(self.trial / "verifier")
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual(row["status"], "missing_evidence")

    def test_agent_timeout_with_a_snapshot_is_graded(self):
        (self.trial / "result.json").write_text(json.dumps({"exception_info": {"exception_type": "AgentTimeoutError"}}))
        row = grade_trial(self.trial, "claude-haiku", CONFIG, SKILL, self.cases, ["unused"])
        self.assertEqual((row["status"], row["timed_out"]), ("ok", True))
        self.assertIn("graders", row)

    def test_report_keeps_ungraded_runs_undecided_grades_and_collisions_apart(self):
        run_dir = Path(self._tmp.name) / "run-1"
        run_dir.mkdir()
        base = {"case": "c", "config": "claude-haiku", "status": "ok", "skill_loaded": True,
                "skill_loaded_expected": True, "foreign_copy_loaded": False, "harness_lists_skill": True,
                "evidence": {"cost_usd": 0.01}}
        rows = [
            {**base, "variant": "with", "graders": {"g": {"pass": True, "judges": {"a": {"pass": True}, "b": {"pass": False}}}}},
            {**base, "variant": "with", "graders": {"g": {"pass": None}}},
            {**base, "variant": "without", "skill_loaded": False, "skill_loaded_expected": False,
             "graders": {"g": {"pass": False}}},
            {"case": "c", "config": "claude-haiku", "variant": "without", "status": "infra_error", "error": "X"},
        ]
        (run_dir / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        text = report(run_dir)
        self.assertIn("c | claude-haiku | with: 2 ok | skill loaded 2/2 (expected True) | g 1/1 (1 undecided)", text)
        self.assertIn("c | claude-haiku | without: 1 ok, 1 not graded ['X']", text)
        self.assertIn("without: the harness lists a skill with this name", text)
        self.assertIn("Judge disagreements:", text)
        self.assertIn("claude-haiku: 0.0300", text)

    def test_report_gives_median_work_per_arm_retries_and_trigger_rates(self):
        run_dir = Path(self._tmp.name) / "run-2"
        run_dir.mkdir()
        (run_dir / "run.json").write_text(json.dumps({"trigger": True}))
        base = {"config": "opus", "status": "ok", "variant": "with", "graders": {}, "evidence": {}}
        usage = lambda n: {"agent_seconds": n / 1000, "evidence": {
            "usage": {"input_tokens": 1, "cache_read_input_tokens": n - 1, "output_tokens": n // 100},
            "tool_calls": n // 10_000, "retries": 2 if n == 300_000 else 0}}
        rows = [{**base, **usage(100_000), "case": "a", "skill_loaded": True, "skill_loaded_expected": True},
                {**base, **usage(300_000), "case": "a", "skill_loaded": False, "skill_loaded_expected": True},
                {**base, **usage(50_000), "case": "near", "skill_loaded": True, "skill_loaded_expected": False},
                {**base, "case": "near", "skill_loaded": None, "skill_loaded_expected": False}]
        (run_dir / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        text = report(run_dir)
        self.assertIn("a | opus | with: 2 ok | skill loaded 1/2 (expected True) | 200s 20 calls in 200k out 2.0k", text)
        self.assertIn("- opus: with 100s 10 calls in 100k out 1.0k", text)
        self.assertIn("- a / opus / with: 2 retries", text)
        self.assertIn("- opus: should-trigger 1/2, near-miss 1/1", text)


class InstructionFiles(unittest.TestCase):
    """Each setup gets the instruction file under the name its harness reads, unless the suite names one."""

    def test_each_harness_reads_its_own_name_unless_the_suite_gives_one(self):
        configs = ["claude-code-opus-5.5-high", "codex-gpt-6-astra-high", "openclaw-kimi-k3.1-pro-high-moonshotai"]
        artifact = {"type": "instruction-file", "path": "constitution/SKILL.md"}
        self.assertEqual(instruction_files(artifact, configs), dict(zip(configs, ["CLAUDE.md", "AGENTS.md", "AGENTS.md"])))
        self.assertEqual(set(instruction_files(artifact | {"as": "AGENTS.md"}, configs).values()), {"AGENTS.md"})
        self.assertEqual(set(instruction_files({"type": "skill", "name": "x"}, configs).values()), {None})
        self.assertEqual(len({task_folder(n) for n in (None, "CLAUDE.md", "AGENTS.md")}), 3)


class StoredBaseline(unittest.TestCase):
    """A without-skill task reuses earlier trials only when everything the agent saw is identical."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.results = Path(self._tmp.name)

    def prior_run(self, run_id, started, statuses, config=CONFIG, instruction="Shorten docs/a.md.", folder=None,
                  **row_extra):
        run = self.results / run_id
        task = run / (folder or "tasks") / "shorten-doc--without"
        task.mkdir(parents=True)
        (task / "instruction.md").write_text(instruction)
        (run / "run.json").write_text(json.dumps({"harbor": SETTINGS["harbor"], "started_at": started,
                                                  "configs": {"haiku": config},
                                                  "agent_args": {"haiku": agent_args(config)},
                                                  **({"task_dirs": {"haiku": folder}} if folder else {})}))
        rows = [{"config": "haiku", "case": "shorten-doc", "variant": "without", "status": s,
                 "trial": f"{run_id}-t{i}", **row_extra} for i, s in enumerate(statuses)]
        (run / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        return task

    def find(self, attempts):
        digest = task_digest(self.prior_run("current", "2026-10-25", []))
        return [t.name for t in stored_baseline(self.results, "current", CONFIG, "shorten-doc--without", digest, attempts)]

    def test_newest_graded_trials_of_an_identical_task_are_reused(self):
        self.prior_run("old", "2026-10-20", ["ok", "ok"])
        self.prior_run("new", "2026-10-22", ["ok", "infra_error"])
        self.assertEqual(self.find(2), ["new-t0", "old-t0"])

    def test_trials_are_found_in_the_task_folder_their_setup_used(self):
        self.prior_run("named", "2026-10-22", ["ok"], folder=task_folder("CLAUDE.md"))
        self.assertEqual(self.find(1), ["named-t0"])

    def test_too_few_matches_runs_fresh(self):
        self.prior_run("old", "2026-10-20", ["ok", "missing"])
        self.assertEqual(self.find(2), [])

    def test_changed_task_other_config_or_reused_rows_do_not_count(self):
        self.prior_run("edited", "2026-10-21", ["ok"], instruction="Shorten it more.")
        self.prior_run("sonnet", "2026-10-21", ["ok"], config={**CONFIG, "model": "anthropic/claude-sonnet"})
        self.prior_run("copy", "2026-10-21", ["ok"], reused_from="older/jobs/haiku/t")
        self.assertEqual(self.find(1), [])

    def test_runs_recorded_before_agent_arguments_were_stored_do_not_count(self):
        task = self.prior_run("legacy", "2026-10-21", ["ok"])
        meta = json.loads((task.parents[1] / "run.json").read_text())
        del meta["agent_args"]
        (task.parents[1] / "run.json").write_text(json.dumps(meta))
        self.assertEqual(self.find(1), [])

    def test_reused_tasks_are_excluded_from_the_harbor_job(self):
        cmd = harbor_command(CONFIG | {"harness": "claude-code"}, Path("t"), Path("j"), "haiku", 1, 1,
                             ["shorten-doc--without"])
        self.assertIn("shorten-doc--without", cmd)
        self.assertIn("*/shorten-doc--without", cmd)

    def test_report_counts_reused_trials_without_their_cost(self):
        run_dir = self.results / "run"
        run_dir.mkdir()
        row = {"case": "c", "config": "haiku", "variant": "without", "status": "ok", "skill_loaded": False,
               "skill_loaded_expected": False, "graders": {}, "evidence": {"cost_usd": 0.5}}
        rows = [row, {**row, "reused_from": "old/jobs/haiku/t"}]
        (run_dir / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        text = report(run_dir)
        self.assertIn("c | haiku | without: 2 ok (1 reused)", text)
        self.assertIn("haiku: 0.5000", text)


if __name__ == "__main__":
    unittest.main()
