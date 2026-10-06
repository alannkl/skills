"""cleanup-worktree.mjs removes a review worktree only when nothing in it would be lost."""
import unittest

from fixtures import PreparedReview


class CleanupWorktree(unittest.TestCase):
    def setUp(self):
        self.review = PreparedReview()
        self.addCleanup(self.review.close)

    def assert_retained(self, code, result):
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "retained")
        self.assertTrue(self.review.worktree.is_dir())

    def test_inspection_keeps_worktree(self):
        """Given an untouched review worktree, when inspected without --remove, then it is eligible and still exists."""
        code, result = self.review.cleanup()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "eligible")
        self.assertTrue(self.review.worktree.is_dir())

    def test_removes_untouched_worktree_and_private_refs(self):
        """Given an untouched review worktree, when removed, then the worktree and its private refs are gone."""
        self.assertNotEqual(self.review.private_refs(), "")
        code, result = self.review.cleanup("--remove")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "removed")
        self.assertFalse(self.review.worktree.exists())
        self.assertEqual(self.review.private_refs(), "")

    def test_unpushed_commit_blocks_removal(self):
        """Given a commit in the worktree that the PR head does not contain, when removed, then the worktree is retained at that commit."""
        commit = self.review.commit_in_worktree()
        self.assert_retained(*self.review.cleanup("--remove"))
        self.assertEqual(self.review.git(self.review.worktree, "rev-parse", "HEAD"), commit)

    def test_pushed_commit_allows_removal(self):
        """Given a commit in the worktree that was pushed to the PR head, when removed, then the worktree is gone."""
        commit = self.review.commit_in_worktree()
        self.review.git(self.review.worktree, "push", "-q", str(self.review.remote),
                        f"{commit}:refs/pull/1/head")
        code, result = self.review.cleanup("--remove")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "removed")
        self.assertFalse(self.review.worktree.exists())

    def test_uncommitted_edit_blocks_removal(self):
        """Given an uncommitted edit to a tracked file, when removed, then the worktree and the edit survive."""
        (self.review.worktree / "a.txt").write_text("edited\n")
        self.assert_retained(*self.review.cleanup("--remove"))
        self.assertEqual((self.review.worktree / "a.txt").read_text(), "edited\n")

    def test_untracked_file_blocks_removal(self):
        """Given an untracked file, when removed, then the worktree and the file survive."""
        (self.review.worktree / "notes.txt").write_text("evidence\n")
        self.assert_retained(*self.review.cleanup("--remove"))
        self.assertTrue((self.review.worktree / "notes.txt").exists())

    def test_ignored_file_needs_discard_flag(self):
        """Given an ignored file, when removed without --discard-ignored, then it is retained; with the flag, it is removed."""
        (self.review.worktree / "check.log").write_text("output\n")
        self.assert_retained(*self.review.cleanup("--remove"))
        self.assertTrue((self.review.worktree / "check.log").exists())
        code, result = self.review.cleanup("--remove", "--discard-ignored")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "removed")
        self.assertFalse(self.review.worktree.exists())


if __name__ == "__main__":
    unittest.main()
