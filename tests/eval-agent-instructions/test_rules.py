"""The rule map resolves to exact text and real graders, minus copies lose only that text, and results tabulate per rule."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
from rules import check_rules, minus_artifact, remove_text, tabulate  # noqa: E402

SKILL = """---
name: target
---
# Target

- Use pnpm. Run tests first.
- Ask before deleting files.
"""


class Rules(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.skill = root / "target"
        (self.skill / "references").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(SKILL)
        (self.skill / "references" / "x.md").write_text("Reference.\n")
        self.cases = root / "evals"
        (self.cases / "case-a").mkdir(parents=True)
        (self.cases / "case-a" / "graders.json").write_text(json.dumps({"graders": [{"name": "uses-pnpm"}]}))

    def rule(self, text="Use pnpm.", graders=("case-a/uses-pnpm",)):
        return {"file": "SKILL.md", "text": [text] if isinstance(text, str) else text, "graders": list(graders)}

    def test_sound_map_has_no_problems(self):
        self.assertEqual(check_rules({"use-pnpm": self.rule()}, self.skill, self.cases), [])

    def test_missing_or_repeated_text_unknown_grader_and_bad_name_are_reported(self):
        rules = {"gone": self.rule("Use yarn."), "Bad_Name": self.rule(),
                 "repeated": self.rule("- "), "no-grader": self.rule(graders=["case-a/nope"]),
                 "fragment": self.rule("Run tests"), "mid-sentence": self.rule("pnpm. Run")}
        problems = "\n".join(check_rules(rules, self.skill, self.cases))
        for expected in ("gone: text occurs 0 times", "Bad_Name: rule names", "repeated: text occurs 2 times",
                         "no-grader: no grader case-a/nope", "fragment: text is not whole sentences",
                         "mid-sentence: text is not whole sentences"):
            self.assertIn(expected, problems)

    def test_removing_text_leaves_no_stray_space_or_empty_item(self):
        self.assertEqual(remove_text("- Use pnpm. Run tests first.\n", "Use pnpm."), "- Run tests first.\n")
        self.assertEqual(remove_text("- Use pnpm. Run tests first.\n", "Run tests first."), "- Use pnpm.\n")
        self.assertEqual(remove_text("- A.\n- B.\n- C.\n", "B."), "- A.\n- C.\n")
        self.assertEqual(remove_text("1. A.\n2. B.\n", "B."), "1. A.\n")

    def test_minus_copy_differs_only_by_the_rule_text(self):
        dest = Path(self._tmp.name) / "minus" / "target"
        minus_artifact(self.skill, self.rule(["Use pnpm.", "Ask before deleting files."]), dest)
        self.assertEqual((dest / "SKILL.md").read_text(), SKILL.replace("Use pnpm. ", "").replace(
            "- Ask before deleting files.\n", ""))
        self.assertEqual((dest / "references" / "x.md").read_text(), "Reference.\n")
        self.assertEqual((self.skill / "SKILL.md").read_text(), SKILL)

    def test_minus_copy_of_an_instruction_file(self):
        dest = Path(self._tmp.name) / "minus" / "AGENTS.md"
        minus_artifact(self.skill / "SKILL.md", self.rule("Ask before deleting files."), dest)
        self.assertEqual(dest.read_text(), SKILL.replace("- Ask before deleting files.\n", ""))

    def test_table_classifies_each_rule_per_configuration(self):
        def row(variant, passed, config="haiku"):
            nonlocal n
            n += 1
            return {"status": "ok", "config": config, "case": "case-a", "variant": variant, "trial": f"t{n}",
                    "skill_loaded": variant != "without", "graders": {"uses-pnpm": {"pass": passed}}}
        n = 0
        rules = {"use-pnpm": self.rule(), "ask-first": {"file": "SKILL.md", "text": ["x"], "graders": []},
                 "other": self.rule()}
        rows = ([row("with", True) for _ in range(2)] + [row("without", False) for _ in range(3)]
                + [row("with", True, "deepseek"), row("without", True, "deepseek")]
                + [row("with", None), {**row("with", True), "reused_from": "old/jobs/haiku/t1"}]
                + [{**row("with", False), "skill_loaded": False}])
        minus_run = [row("with", True) for _ in range(3)] + [row("minus-use-pnpm", True) for _ in range(3)]
        table = tabulate(rules, [({}, rows), ({"minus": "use-pnpm"}, minus_run)])
        self.assertIn("| use-pnpm | haiku | 2/2 | 0/3 | 3/3 | 3/3 | 1 | removal matched the full artifact |", table)
        self.assertIn("| use-pnpm | deepseek | 1/1 | 1/1 |  |  |  | candidate: no difference |", table)
        self.assertIn("| other | haiku | 2/2 | 0/3 | 3/3 |  | 1 | keep: the artifact helps |", table)
        self.assertIn("| ask-first | | | | | | | untested: no grader |", table)

    def test_removal_needs_three_runs_per_arm_and_no_worse_result(self):
        def row(variant, passed, trial):
            return {"status": "ok", "config": "haiku", "case": "case-a", "variant": variant, "trial": trial,
                    "skill_loaded": True, "graders": {"uses-pnpm": {"pass": passed}}}
        rules = {"use-pnpm": self.rule()}
        full = [row("with", True, f"w{i}") for i in range(3)]
        worse = full + [row("minus-use-pnpm", True, "m1"), row("minus-use-pnpm", True, "m2"),
                        row("minus-use-pnpm", False, "m3")]
        self.assertIn("removal did worse", tabulate(rules, [({"minus": "use-pnpm"}, worse)]))
        # Three graded results from two runs are still two runs.
        short = full + [row("minus-use-pnpm", True, "m1"), row("minus-use-pnpm", True, "m2"),
                        row("minus-use-pnpm", True, "m2")]
        self.assertIn("removal: fewer than 3 runs per arm", tabulate(rules, [({"minus": "use-pnpm"}, short)]))


if __name__ == "__main__":
    unittest.main()
