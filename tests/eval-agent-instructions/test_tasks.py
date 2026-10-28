"""Task directories differ between arms only by the skill under test, and never carry graders."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
from tasks import PROBE_CASE, build_tasks, load_suite, workspace_name  # noqa: E402


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

    def build(self, case_names, instruction_file=None, out=None):
        return build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / n for n in case_names],
                           ["with", "without"], "base:test", out or self.out, instruction_file=instruction_file)

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
                    {"minus-x": copy}, pin=True)
        task = self.out / "edit-case--minus-x"
        skills = task / "environment" / "skills"
        self.assertEqual(sorted(p.name for p in skills.iterdir()), ["dep", "target"])
        self.assertIn("trimmed", (skills / "target" / "SKILL.md").read_text())
        self.assertEqual((task / "instruction.md").read_text(),
                         "Use the skill at /skills/target/SKILL.md for this task.\n\nAdd a rule.\n")

    def test_pinned_build_names_the_skill_only_where_it_is_installed(self):
        build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / "edit-case", self.cases / PROBE_CASE],
                    ["with", "without"], "base:test", self.out, pin=True)
        read = lambda task: (self.out / task / "instruction.md").read_text()
        self.assertEqual(read("edit-case--with"), "Use the skill at /skills/target/SKILL.md for this task.\n\nAdd a rule.\n")
        self.assertEqual(read("edit-case--without"), "Add a rule.\n")
        self.assertTrue(read(f"{PROBE_CASE}--with").startswith("List the skills"))

    def test_instruction_file_is_placed_in_the_workspace_only_in_the_with_arm(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "agents.md").write_text("# Rules\n")
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "docs/agents.md", "as": "CLAUDE.md"}}))
        self.build(["edit-case", PROBE_CASE], workspace_name(load_suite(self.repo, "target")["artifact"], "AGENTS.md"))
        with_env = self.out / "edit-case--with" / "environment"
        self.assertEqual((with_env / "instructions" / "CLAUDE.md").read_text(), "# Rules\n")
        self.assertIn("COPY instructions/ /app/", (with_env / "Dockerfile").read_text())
        without_env = self.out / "edit-case--without" / "environment"
        self.assertFalse((without_env / "instructions").exists())
        self.assertNotIn("instructions", (without_env / "Dockerfile").read_text())
        self.assertIn("quote their first line", (self.out / f"{PROBE_CASE}--with" / "instruction.md").read_text())

    def test_instruction_file_that_the_fixture_already_has_under_the_delivered_name_is_refused(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "rules.md"}}))
        (self.repo / "rules.md").write_text("# Rules\n")
        with self.assertRaises(SystemExit):
            self.build(["edit-case"], "AGENTS.md")
        self.build(["edit-case"], "CLAUDE.md", out=self.out / "claude")
        self.assertTrue((self.out / "claude" / "edit-case--with" / "environment" / "instructions" / "CLAUDE.md").is_file())

    def test_instruction_file_takes_the_harness_name_and_is_delivered_without_frontmatter(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "target/SKILL.md"}}))
        (self.repo / "target" / "SKILL.md").write_text("---\nname: target\ndescription: d\n---\n\n# Rules\n\n- one\n")
        artifact = load_suite(self.repo, "target")["artifact"]
        self.assertEqual([workspace_name(artifact, f) for f in ("CLAUDE.md", "AGENTS.md")], ["CLAUDE.md", "AGENTS.md"])
        self.build(["edit-case"], "CLAUDE.md")
        delivered = self.out / "edit-case--with" / "environment" / "instructions"
        self.assertEqual(sorted(p.name for p in delivered.iterdir()), ["CLAUDE.md"])
        self.assertEqual((delivered / "CLAUDE.md").read_text(), "# Rules\n\n- one\n")

    def test_instruction_file_goes_below_the_harness_template(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "target/SKILL.md"}}))
        (self.repo / "target" / "SKILL.md").write_text("---\nname: target\n---\n# Rules\n")
        (self.cases / "edit-case" / "fixture" / "AGENTS.md").unlink()
        build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / "edit-case"], ["with", "without"],
                    "base:test", self.out, instruction_file="AGENTS.md", template="# Your Workspace\n\nNotes.\n")
        self.assertEqual((self.out / "edit-case--with" / "environment" / "instructions" / "AGENTS.md").read_text(),
                         "# Your Workspace\n\nNotes.\n\n# Rules\n")
        self.assertFalse((self.out / "edit-case--without" / "environment" / "instructions").exists())

    def test_minus_copy_of_an_instruction_file_is_delivered_without_frontmatter(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "target/SKILL.md"}}))
        copy = Path(self._tmp.name) / "minus" / "SKILL.md"
        copy.parent.mkdir()
        copy.write_text("---\nname: target\n---\n# Rules\n")
        build_tasks(self.repo, load_suite(self.repo, "target"), [self.cases / "edit-case"], ["minus-x"], "base:test",
                    self.out, {"minus-x": copy}, instruction_file="CLAUDE.md")
        self.assertEqual((self.out / "edit-case--minus-x" / "environment" / "instructions" / "CLAUDE.md").read_text(),
                         "# Rules\n")

    def test_text_without_frontmatter_is_delivered_byte_for_byte(self):
        (self.cases / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "instruction-file", "path": "rules.md"}}))
        (self.repo / "rules.md").write_bytes(b"# Rules\r\n---\r\n- one\r\n")
        self.build(["edit-case"], "CLAUDE.md")
        self.assertEqual((self.out / "edit-case--with" / "environment" / "instructions" / "CLAUDE.md").read_bytes(),
                         b"# Rules\r\n---\r\n- one\r\n")

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
