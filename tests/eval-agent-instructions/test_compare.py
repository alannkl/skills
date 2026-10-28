"""A candidate is compared with a baseline on acceptance graders only, each trial counted once."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
import compare  # noqa: E402


class Compare(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        case = self.root / "suite" / "c"
        case.mkdir(parents=True)
        (case / "graders.json").write_text(json.dumps({"graders": [
            {"name": "keeps", "type": "llm", "criteria": "x"},
            {"name": "style", "type": "llm", "criteria": "y", "diagnostic": True},
            {"name": "loaded", "type": "skills_loaded", "skills": ["s"]}]}))

    def run_dir(self, name, passes, reused_from=None):
        run = self.root / name
        run.mkdir()
        rows = [{"status": "ok", "variant": "with", "config": "opus", "case": "c", "trial_path": f"jobs/t{i}",
                 "reused_from": reused_from, "evidence": {},
                 "graders": {"keeps": {"pass": p}, "style": {"pass": not p}, "loaded": {"pass": False}}}
                for i, p in enumerate(passes)]
        rows.append({"status": "ok", "variant": "without", "config": "opus", "case": "c", "graders": {}})
        (run / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        return run

    def test_only_acceptance_graders_count_and_drops_are_listed(self):
        base, cand = self.run_dir("base", [True, True, True]), self.run_dir("cand", [True, False, False])
        text = compare.compare([base], [cand], self.root / "suite")
        # The grader counts once per side: three passes are one pass, one failure in three is a failure.
        self.assertIn("baseline 1/1, candidate 0/1", text)
        self.assertIn("- c/keeps: 1/1 -> 0/1", text)
        self.assertNotIn("style", text)
        self.assertNotIn("loaded", text)

    def test_a_trial_reused_by_a_later_run_counts_once(self):
        first = self.run_dir("first", [True])
        later = self.run_dir("later", [True], reused_from="first/jobs/t0")
        self.assertEqual(len(compare.with_rows([first, later])), 1)
        self.assertEqual(len(compare.with_rows([later])), 1)

    def test_work_counts_each_case_once_however_often_it_ran(self):
        (self.root / "suite" / "d").mkdir()
        (self.root / "suite" / "d" / "graders.json").write_text((self.root / "suite" / "c" / "graders.json").read_text())

        def run(name, attempts):
            (self.root / name).mkdir()
            rows = [{"status": "ok", "variant": "with", "config": "opus", "case": case, "trial_path": f"jobs/{case}{i}",
                     "evidence": {"usage": {"input_tokens": tokens}}, "graders": {"keeps": {"pass": True}}}
                    for case, tokens in (("c", 10_000), ("d", 100_000)) for i in range(attempts[case])]
            (self.root / name / "grades.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
            return self.root / name

        text = compare.compare([run("base", {"c": 3, "d": 1})], [run("cand", {"c": 1, "d": 1})], self.root / "suite")
        self.assertIn("baseline: in 55k", text)
        self.assertIn("candidate: in 55k", text)
        self.assertIn("Median change in input per case: +0k (0 of 2 cases lower)", text)

    def test_pairwise_maps_the_judges_letter_back_to_the_side(self):
        rows = lambda side: [{"config": "opus", "case": "c", "run_dir": side, "side": side}]
        for draw, expected in ((0.0, "cand"), (0.9, "base")):
            with mock.patch.object(compare.random.Random, "random", lambda self: draw), \
                    mock.patch.object(compare, "complete", lambda model, prompt: ('{"better": "A"}', model, {})), \
                    mock.patch.object(compare, "output_text", lambda row: row["side"]), \
                    mock.patch.object(Path, "read_text", lambda self: "request"):
                self.assertEqual(compare.pairwise(rows("base"), rows("cand"), "judge")[0]["better"], expected)


if __name__ == "__main__":
    unittest.main()
