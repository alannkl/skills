"""push-fixes.mjs pushes review-worktree commits to the PR's source branch only as a fast-forward."""
import json
import unittest
from pathlib import Path

from fixtures import PreparedReview


class PushFixes(unittest.TestCase):
    def setUp(self):
        self.review = PreparedReview()
        self.addCleanup(self.review.close)

    def test_dry_run_lists_commits_without_pushing(self):
        """Given one fix commit in the worktree, when run with --dry-run, then it reports the repository, branch and commit and the remote branch is unchanged."""
        commit = self.review.commit_in_worktree()
        code, result = self.review.push_fixes("--dry-run")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "ready")
        self.assertEqual((result["repository"], result["branch"], result["refspec"]), ("o/r", "feature", "HEAD:refs/heads/feature"))
        self.assertEqual([c["sha"] for c in result["commits"]], [commit])
        self.assertEqual(self.review.remote_branch(), self.review.pr_head)

    def test_push_advances_the_source_branch(self):
        """Given one fix commit, when pushed, then the remote feature branch points at it."""
        commit = self.review.commit_in_worktree()
        code, result = self.review.push_fixes()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "pushed")
        self.assertEqual(self.review.remote_branch(), commit)

    def test_nothing_to_push_exits_four(self):
        """Given an untouched worktree, when pushed, then it exits 4 and the remote branch is unchanged."""
        code, result = self.review.push_fixes()
        self.assertEqual(code, 4, result)
        self.assertEqual(self.review.remote_branch(), self.review.pr_head)

    def test_moved_head_blocks_push(self):
        """Given the PR head advanced to a commit the worktree does not contain, when pushed, then it exits 3 and nothing is pushed."""
        self.review.commit_in_worktree()
        seed = self.review.root / "seed"
        (seed / "b.txt").write_text("author\n")
        self.review.git(seed, "add", "b.txt")
        self.review.git(seed, "commit", "-q", "-m", "author push")
        moved = self.review.git(seed, "rev-parse", "HEAD")
        self.review.git(seed, "push", "-q", str(self.review.remote), f"{moved}:refs/pull/1/head", f"{moved}:refs/heads/feature")
        self.review.set_gh({"pr": {**self.review.pr, "headRefOid": moved}})
        code, result = self.review.push_fixes()
        self.assertEqual(code, 3, result)
        self.assertIn("not an ancestor", result["reason"])
        self.assertEqual(self.review.remote_branch(), moved)

    def test_rewound_head_blocks_push(self):
        """Given the author rewound the PR branch to before the reviewed head, when pushed, then it exits 3 and the remote branch stays rewound."""
        self.review.commit_in_worktree()
        base = self.review.git(self.review.root, "--git-dir", str(self.review.remote), "rev-parse", "refs/heads/main")
        self.review.git(self.review.root, "--git-dir", str(self.review.remote), "update-ref", "refs/heads/feature", base)
        self.review.git(self.review.root, "--git-dir", str(self.review.remote), "update-ref", "refs/pull/1/head", base)
        self.review.set_gh({"pr": {**self.review.pr, "headRefOid": base}})
        code, result = self.review.push_fixes()
        self.assertEqual(code, 3, result)
        self.assertIn("reviewed head", result["reason"])
        self.assertEqual(self.review.remote_branch(), base)

    def test_second_push_follows_earlier_fixes(self):
        """Given fixes already pushed and a further fix commit, when pushed again, then the remote branch advances to the new commit."""
        first = self.review.commit_in_worktree()
        self.assertEqual(self.review.push_fixes()[0], 0)
        self.review.git(self.review.root, "--git-dir", str(self.review.remote), "update-ref", "refs/pull/1/head", first)
        self.review.set_gh({"pr": {**self.review.pr, "headRefOid": first}})
        (self.review.worktree / "a.txt").write_text("one\ntwo\nthree\nfour\n")
        self.review.git(self.review.worktree, "commit", "-q", "-am", "fix again")
        second = self.review.git(self.review.worktree, "rev-parse", "HEAD")
        code, result = self.review.push_fixes()
        self.assertEqual(code, 0, result)
        self.assertEqual([c["sha"] for c in result["commits"]], [second])
        self.assertEqual(self.review.remote_branch(), second)

    def test_push_publishes_no_tags_despite_follow_tags(self):
        """Given push.followTags enabled and an annotated tag on the fix commit, when pushed, then the branch advances and the remote has no tags."""
        commit = self.review.commit_in_worktree()
        self.review.git(self.review.worktree, "config", "push.followTags", "true")
        self.review.git(self.review.worktree, "tag", "-a", "unapproved-release", "-m", "release")
        code, result = self.review.push_fixes()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.review.remote_branch(), commit)
        self.assertEqual(self.review.git(self.review.root, "--git-dir", str(self.review.remote), "tag", "--list"), "")

    def test_dirty_worktree_blocks_push(self):
        """Given an uncommitted edit beside a fix commit, when pushed, then it exits 2 naming the file."""
        self.review.commit_in_worktree()
        (self.review.worktree / "notes.txt").write_text("draft\n")
        code, result = self.review.push_fixes()
        self.assertEqual(code, 2, result)
        self.assertIn("notes.txt", result["reason"])

    def test_missing_source_metadata_exits_two_until_refreshed_with_pr(self):
        """Given a record whose PR lacks head repository metadata, when pushed, then it exits 2; with --pr naming a fresh read-pr file for the same PR, it pushes."""
        commit = self.review.commit_in_worktree()
        record = json.loads(Path(self.review.record).read_text())
        del record["pr"]["headRepository"]
        Path(self.review.record).write_text(json.dumps(record))
        code, result = self.review.push_fixes()
        self.assertEqual(code, 2, result)
        self.assertIn("--pr", result["reason"])
        code, result = self.review.push_fixes("--pr", str(self.review.root / "read-pr.json"))
        self.assertEqual(code, 0, result)
        self.assertEqual(self.review.remote_branch(), commit)

    def test_fork_pr_pushes_through_the_remote_matching_the_fork(self):
        """Given a cross-repository PR from fork f/r and a second remote whose push URL points at that fork, when pushed, then the fork's branch advances and the base repository's does not."""
        commit = self.review.commit_in_worktree()
        fork = self.review.add_fork()
        self.review.git(self.review.worktree, "remote", "add", "fork", "ssh://git@github.com/f/r.git")
        record = json.loads(Path(self.review.record).read_text())
        record["pr"].update(headRepositoryOwner={"login": "f"}, isCrossRepository=True)
        Path(self.review.record).write_text(json.dumps(record))
        code, result = self.review.push_fixes()
        self.assertEqual(code, 0, result)
        self.assertEqual((result["repository"], result["remote"]), ("f/r", "fork"))
        self.assertEqual(self.review.remote_branch(repository=fork), commit)
        self.assertEqual(self.review.remote_branch(), self.review.pr_head)

    def test_remote_with_a_second_push_url_elsewhere_is_rejected(self):
        """Given origin carrying a second push URL at another repository, when pushed, then it exits 2 and nothing is pushed."""
        self.review.commit_in_worktree()
        self.review.git(self.review.worktree, "remote", "set-url", "--add", "--push", "origin", "ssh://git@github.com/o/r.git")
        self.review.git(self.review.worktree, "remote", "set-url", "--add", "--push", "origin", "ssh://git@github.com/x/mirror.git")
        code, result = self.review.push_fixes()
        self.assertEqual(code, 2, result)
        self.assertIn("push URL", result["reason"])
        self.assertEqual(self.review.remote_branch(), self.review.pr_head)

    def test_rejected_push_reports_the_remote_reason(self):
        """Given a remote hook that rejects every push, when pushed, then it exits 1 with the hook's message."""
        self.review.commit_in_worktree()
        hook = self.review.remote / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\necho 'branch is protected' >&2\nexit 1\n")
        hook.chmod(0o755)
        code, result = self.review.push_fixes()
        self.assertEqual(code, 1, result)
        self.assertIn("branch is protected", result["reason"])
        self.assertEqual(self.review.remote_branch(), self.review.pr_head)

    def test_unknown_flag_exits_two(self):
        """Given an unknown option, when run, then it exits 2 with a JSON reason instead of a traceback."""
        code, result = self.review.push_fixes("--force")
        self.assertEqual(code, 2)
        self.assertIn("force", result["reason"])


if __name__ == "__main__":
    unittest.main()
