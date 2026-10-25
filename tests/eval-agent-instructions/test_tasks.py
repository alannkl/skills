"""Task directories differ between arms only by the skill under test, and never carry graders."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
from tasks import PROBE_CASE, build_tasks, load_suite  # noqa: E402


class Tasks(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        for skill in ("target", "dep"):
            (self.repo / skill).mkdir(parents=True)
            (self.repo / skill / "SKILL.md").write_text(f"---\nname: {skill}\n---\n")
        cases = self.repo / "evals" / "target"
        (cases / "edit-case" / "fixture").mkdir(parents=True)
        (cases / "edit-case" / "fixture" / "AGENTS.md").write_text("- rule\n")
        (cases / "edit-case" / "expected").mkdir()
        (cases / "edit-case" / "instruction.md").write_text("Add a rule.\n")
        (cases / "edit-case" / "graders.json").write_text(json.dumps(
            {"agent_timeout_sec": 300, "expect_skill_loaded": {"with": True, "without": False}, "graders": []}))
        (cases / "eval.json").write_text(json.dumps({"dependencies": ["dep"]}))
        self.cases = cases
        self.out = Path(self._tmp.name) / "tasks"

    def build(self, case_names):
        return build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / n for n in case_names],
                           ["with", "without"], "base:test", self.out)

    def test_arms_differ_only_by_the_target_skill(self):
        names = self.build(["edit-case"])
        self.assertEqual(names, ["edit-case--with", "edit-case--without"])
        installed = {v: sorted(p.name for p in (self.out / f"edit-case--{v}" / "environment" / "skills").iterdir())
                     for v in ("with", "without")}
        self.assertEqual(installed, {"with": ["dep", "target"], "without": ["dep"]})

    def test_only_the_workspace_source_enters_the_image(self):
        self.build(["edit-case"])
        env = self.out / "edit-case--with" / "environment"
        self.assertEqual(sorted(p.name for p in (env / "case").iterdir()), ["fixture"])
        self.assertIn("FROM base:test", (env / "Dockerfile").read_text())
        task = self.out / "edit-case--with"
        self.assertEqual((task / "instruction.md").read_text(), "Add a rule.\n")
        self.assertIn("timeout_sec = 300.0", (task / "task.toml").read_text())
        self.assertIn('skills_dir = "/skills"', (task / "task.toml").read_text())

    def test_minus_variant_installs_the_given_copy_under_the_skill_name(self):
        copy = Path(self._tmp.name) / "minus" / "target"
        copy.mkdir(parents=True)
        (copy / "SKILL.md").write_text("---\nname: target\n---\ntrimmed\n")
        build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / "edit-case"], ["minus-x"], "base:test", self.out,
                    {"minus-x": copy}, "Use the target skill for this task.\n\n")
        task = self.out / "edit-case--minus-x"
        skills = task / "environment" / "skills"
        self.assertEqual(sorted(p.name for p in skills.iterdir()), ["dep", "target"])
        self.assertIn("trimmed", (skills / "target" / "SKILL.md").read_text())
        self.assertEqual((task / "instruction.md").read_text(), "Use the target skill for this task.\n\nAdd a rule.\n")

    def test_instruction_file_is_placed_in_the_workspace_only_in_the_with_arm(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "agents.md").write_text("# Rules\n")
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "docs/agents.md", "as": "CLAUDE.md"}}))
        self.build(["edit-case", PROBE_CASE])
        with_env = self.out / "edit-case--with" / "environment"
        self.assertEqual((with_env / "instructions" / "CLAUDE.md").read_text(), "# Rules\n")
        self.assertIn("COPY instructions/ /app/", (with_env / "Dockerfile").read_text())
        without_env = self.out / "edit-case--without" / "environment"
        self.assertFalse((without_env / "instructions").exists())
        self.assertNotIn("instructions", (without_env / "Dockerfile").read_text())
        self.assertIn("quote their first line", (self.out / f"{PROBE_CASE}--with" / "instruction.md").read_text())

    def test_instruction_file_that_the_fixture_already_has_is_refused(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "AGENTS.md"}}))
        (self.repo / "AGENTS.md").write_text("# Rules\n")
        with self.assertRaises(SystemExit):
            self.build(["edit-case"])

    def test_probe_case_needs_no_case_folder(self):
        self.build([PROBE_CASE])
        task = self.out / f"{PROBE_CASE}--with"
        self.assertIn("List the skills", (task / "instruction.md").read_text())
        self.assertEqual(list((task / "environment" / "case").iterdir()), [])

    def test_suite_names_the_setups_it_must_support(self):
        self.assertEqual(load_suite(self.repo, "target")["setups"], {})
        (self.cases / "eval.json").write_text(json.dumps({"setups": {"run": ["a"], "full": ["a", "b"]}}))
        self.assertEqual(load_suite(self.repo, "target")["setups"], {"run": ["a"], "full": ["a", "b"]})
        (self.cases / "eval.json").write_text(json.dumps({"setups": {"default": ["a"]}}))
        with self.assertRaises(SystemExit):
            load_suite(self.repo, "target")


if __name__ == "__main__":
    unittest.main()
