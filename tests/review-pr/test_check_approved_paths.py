"""check-approved-paths.mjs reports every worktree change outside the approved file list."""
import json
import unittest

from fixtures import PreparedReview


class CheckApprovedPaths(unittest.TestCase):
    def setUp(self):
        self.review = PreparedReview()
        self.addCleanup(self.review.close)
        self.approved = self.review.root / "approved.txt"

    def check(self, *paths):
        self.approved.write_text("".join(f"{path}\n" for path in paths))
        result = self.review.node("check-approved-paths.mjs", "--in", self.review.record, "--approved", str(self.approved))
        return result.returncode, json.loads(result.stdout) if result.stdout else result.stderr

    def test_changes_within_the_list_pass(self):
        """Given an edit to an approved PR file, when checked, then it is within scope with no unexpected paths."""
        (self.review.worktree / "a.txt").write_text("fixed\n")
        code, result = self.check("a.txt")
        self.assertEqual(code, 0, result)
        self.assertEqual((result["status"], result["unexpected"], result["outside_pr"]), ("within", [], []))

    def test_unapproved_untracked_and_staged_edits_are_unexpected(self):
        """Given an untracked file and a staged edit outside the list, when checked, then both are unexpected and the exit code is 1."""
        (self.review.worktree / "a.txt").write_text("fixed\n")
        (self.review.worktree / "scratch.txt").write_text("notes\n")
        (self.review.worktree / ".gitignore").write_text("*.log\n*.tmp\n")
        self.review.git(self.review.worktree, "add", ".gitignore")
        code, result = self.check("a.txt")
        self.assertEqual(code, 1)
        self.assertEqual(result["unexpected"], [".gitignore", "scratch.txt"])

    def test_unknown_flag_exits_two(self):
        """Given an unknown option, when run, then it exits 2 without a traceback."""
        result = self.review.node("check-approved-paths.mjs", "--in", self.review.record, "--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertIn("bogus", json.loads(result.stdout)["reason"])

    def test_renames_count_under_both_names_and_outside_pr_is_reported(self):
        """Given a staged rename of a PR file to a path outside the PR, when both names are approved, then it passes and the new name is reported as outside the PR."""
        self.review.git(self.review.worktree, "mv", "a.txt", "b.txt")
        code, result = self.check("a.txt", "b.txt")
        self.assertEqual(code, 0, result)
        self.assertEqual(sorted(result["changed"]), ["a.txt", "b.txt"])
        self.assertEqual(result["outside_pr"], ["b.txt"])
        code, result = self.check("b.txt")
        self.assertEqual((code, result["unexpected"]), (1, ["a.txt"]))


if __name__ == "__main__":
    unittest.main()
