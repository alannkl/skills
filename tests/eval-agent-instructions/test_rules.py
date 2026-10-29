"""The rule map resolves to exact text and real graders, minus copies lose only that text, results tabulate per rule,
and the regular set shrinks to the cheapest cases that keep every rule and gap covered."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
from rules import check_rules, guard_refs, min_set, minus_artifact, remove_text, tabulate  # noqa: E402

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

    def test_a_rule_text_inside_another_rules_text_is_reported(self):
        (self.skill / "SKILL.md").write_text("Run tests. Then lint.\n")
        rules = {"a": {"file": "SKILL.md", "text": ["Run tests. Then lint."], "graders": []},
                 "b": {"file": "SKILL.md", "text": ["Then lint."], "graders": []}}
        self.assertTrue(any("contains b's text" in p for p in check_rules(rules, self.skill, self.cases)))

    def test_overlapping_passages_are_reported(self):
        rules = {"r": {"file": "SKILL.md", "text": ["Run tests. Then lint.", "Then lint."], "graders": []}}
        (self.skill / "SKILL.md").write_text("Run tests. Then lint.\n")
        self.assertTrue(any("overlap" in p for p in check_rules(rules, self.skill, self.cases)))

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
        self.assertIn("| use-pnpm | haiku | 1/1 | 0/1 | 1/1 | 1/1 | 1 | removal matched the full artifact |", table)
        self.assertIn("| use-pnpm | deepseek | 1/1 | 1/1 |  |  |  | candidate: no difference |", table)
        self.assertIn("| other | haiku | 1/1 | 0/1 | 1/1 |  | 1 | the artifact helps, in fewer than 3 runs per arm |", table)
        self.assertIn("| ask-first | | | | | | | untested: no grader |", table)

    def test_table_tells_help_harm_and_shared_failure_apart(self):
        def run(results):
            return [{"status": "ok", "config": "haiku", "case": "case-a", "variant": variant, "trial": f"{variant}{i}",
                     "skill_loaded": True, "graders": {"uses-pnpm": {"pass": passed}}}
                    for variant, passes in results.items() for i, passed in enumerate(passes)]
        rules = {"use-pnpm": self.rule()}
        self.assertIn("| keep: the artifact helps |",
                      tabulate(rules, [({}, run({"with": [True] * 3, "without": [False] * 3}))]))
        self.assertIn("| the artifact did worse |",
                      tabulate(rules, [({}, run({"with": [False] * 3, "without": [True] * 3}))]))
        self.assertIn("| graders fail in both arms: check the wording or grader |",
                      tabulate(rules, [({}, run({"with": [False], "without": [False]}))]))

    def test_arms_count_only_graders_both_ran(self):
        # An earlier with-only run of another case, such as a draft round's, must not read as the artifact doing worse.
        def row(case, variant, passed):
            return {"status": "ok", "config": "opus", "case": case, "variant": variant, "trial": f"{case}-{variant}",
                    "skill_loaded": True, "graders": {"g": {"pass": passed}}}
        rules = {"r": self.rule("Run tests first.", ["case-a/g", "case-b/g"])}
        rows = [row("case-a", "with", True), row("case-a", "without", True), row("case-b", "with", False)]
        self.assertIn("| r | opus | 1/1 | 1/1 |  |  |  | candidate: no difference |", tabulate(rules, [({}, rows)]))
        self.assertIn("| r | opus | 0/1 |", tabulate(rules, [({}, rows[2:])]))

    def test_each_rule_is_judged_by_its_weakest_setup(self):
        from rules import across_setups
        tie = "candidate: no difference"
        self.assertEqual(across_setups({"opus": tie, "haiku": tie}),
                         "candidate on every setup run (2): no case shows its effect")
        self.assertEqual(across_setups({"opus": tie, "haiku": "keep: the artifact helps"}), "keep: helps on haiku")
        self.assertEqual(across_setups({"opus": "the artifact helps, in fewer than 3 runs per arm", "haiku": tie}),
                         "keep: helps on opus, in fewer than 3 runs per arm")
        self.assertIn("did worse on haiku", across_setups({"opus": "keep: the artifact helps",
                                                           "haiku": "the artifact did worse"}))

    def test_a_grader_counts_once_and_passes_only_in_every_attempt(self):
        rows = [{"status": "ok", "config": "haiku", "case": "case-a", "variant": "with", "trial": f"w{i}",
                 "skill_loaded": True, "graders": {"uses-pnpm": {"pass": p}}} for i, p in enumerate([True, False, True])]
        self.assertIn("| use-pnpm | haiku | 0/1 |", tabulate({"use-pnpm": self.rule()}, [({}, rows)]))

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


    def test_guards_are_left_out_of_the_comparison_they_cannot_inform(self):
        (self.cases / "case-a" / "graders.json").write_text(json.dumps({"graders": [
            {"name": "uses-pnpm", "type": "llm", "criteria": "c", "guard": "dictated: the request names pnpm"},
            {"name": "no-citing", "type": "llm", "criteria": "c", "variants": ["with"]},
            {"name": "read-docs", "type": "read", "marker": "m"},
            {"name": "open", "type": "llm", "criteria": "c"}]}))
        guards = guard_refs(self.cases)
        self.assertEqual(guards["without"], {"case-a/uses-pnpm", "case-a/no-citing", "case-a/read-docs"})
        self.assertEqual(guards["minus"], {"case-a/uses-pnpm", "case-a/read-docs"})

        def row(variant, trial, **passes):
            return {"status": "ok", "config": "opus", "case": "case-a", "variant": variant, "trial": trial,
                    "skill_loaded": True, "graders": {g: {"pass": p} for g, p in passes.items()}}
        rules = {"use-pnpm": self.rule(), "silent": self.rule("Run tests first.", ["case-a/no-citing"]),
                 "mixed": self.rule("Ask before deleting files.", ["case-a/uses-pnpm", "case-a/open"])}
        runs = [({}, [row("with", "w1", **{"uses-pnpm": True, "no-citing": False, "open": True}),
                      row("without", "o1", **{"uses-pnpm": True, "open": True})])]
        table = tabulate(rules, runs, guards)
        # A dictated grader passes in both arms whatever the text says, so the rule is under-tested, not a candidate.
        self.assertIn("| use-pnpm | under-tested: no case shows its effect |", table)
        # A with-only grader would read "did worse" against an arm that never ran it.
        self.assertIn("| silent | under-tested: only a --minus run can show its effect |", table)
        self.assertIn("| mixed | opus | 1/1 | 1/1 |  |  |  | candidate: no difference |", table)
        # A full-against-minus run can use the with-only grader, but never the dictated one.
        minus = [row("with", f"f{i}", **{"no-citing": True, "uses-pnpm": True}) for i in range(3)]
        minus += [row("minus-silent", f"m{i}", **{"no-citing": False}) for i in range(3)]
        minus += [row("minus-use-pnpm", f"u{i}", **{"uses-pnpm": True}) for i in range(3)]
        table = tabulate(rules, [({"minus": "silent"}, minus)], guards)
        self.assertIn("| silent | opus |  |  | 1/1 | 0/1 |  | removal did worse |", table)
        self.assertIn("| use-pnpm | under-tested: no case shows its effect |", table)

    def test_a_rule_shown_only_by_preference_graders_is_flagged_for_its_author(self):
        (self.cases / "case-a" / "graders.json").write_text(json.dumps({"graders": [
            {"name": "titled", "type": "llm", "criteria": "c", "preference": "a bare ID serves a reader who knows it"},
            {"name": "open", "type": "llm", "criteria": "c"}]}))
        guards = guard_refs(self.cases)
        self.assertEqual(guards["preference"], {"case-a/titled"})
        rows = [{"status": "ok", "config": "opus", "case": "case-a", "variant": variant, "trial": variant,
                 "skill_loaded": True, "graders": {"titled": {"pass": variant == "with"}, "open": {"pass": True}}}
                for variant in ("with", "without")]
        rules = {"titles": self.rule("Run tests first.", ["case-a/titled"]),
                 "mixed": self.rule("Ask before deleting files.", ["case-a/titled", "case-a/open"])}
        table = tabulate(rules, [({}, rows)], guards)
        self.assertRegex(table, r"\| titles \| keep: helps on opus.*; preference only: the author decides")
        self.assertNotIn("| mixed | keep: helps on opus, in fewer than 3 runs per arm; preference", table)


class MinSet(unittest.TestCase):
    @staticmethod
    def row(case, tokens, **passes):
        return {"status": "ok", "variant": "with", "case": case, "config": "opus", "skill_loaded": True,
                "evidence": {"usage": {"input_tokens": tokens}},
                "graders": {g: {"pass": p} for g, p in passes.items()}}

    def test_keeps_the_cheapest_cover_and_gaps_only_when_asked(self):
        rules = {"a": {"graders": ["big/x", "small/x"]}, "b": {"graders": ["big/y"]}, "c": {"graders": []}}
        acceptance = {"big": {"x", "y"}, "small": {"x"}, "redundant": {"z"}, "gappy": {"g"}}
        rows = [self.row("big", 900, x=True, y=True), self.row("small", 100, x=True),
                self.row("redundant", 50, z=True), self.row("gappy", 500, g=False)]
        chosen = min_set(rules, [({}, rows)], acceptance, gaps=True)
        # big alone covers a and b, so the cheaper small adds nothing; gappy holds a failing grader only it shows.
        self.assertEqual(chosen["kept"], ["big", "gappy"])
        self.assertEqual(chosen["dropped"], ["redundant", "small"])
        self.assertEqual(min_set(rules, [({}, rows)], acceptance)["kept"], ["big"])

    def test_a_guard_case_cannot_stand_in_for_the_case_that_shows_the_effect(self):
        rules = {"a": {"graders": ["cheap/x", "costly/y"]}}
        acceptance = {"cheap": {"x"}, "costly": {"y"}}
        rows = [self.row("cheap", 100, x=True), self.row("costly", 900, y=True)]
        self.assertEqual(min_set(rules, [({}, rows)], acceptance)["kept"], ["cheap"])
        self.assertEqual(min_set(rules, [({}, rows)], acceptance, guards={"cheap/x"})["kept"], ["costly"])

    def test_a_rule_tested_only_outside_the_candidates_is_reported(self):
        rules = {"a": {"graders": ["integration-case/x"]}}
        chosen = min_set(rules, [], {"other": {"y"}})
        self.assertEqual(chosen["rules_outside"], ["a"])
        self.assertEqual(chosen["kept"], [])


if __name__ == "__main__":
    unittest.main()
