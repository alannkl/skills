# Review-PR tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/review-pr -v
```

The suite runs the bundled scripts with Node.js against disposable Git repositories. A fake `gh` answers from fixture JSON, and a fake SSH transport serves `github.com` fetches from a local bare repository, so nothing reaches GitHub.

`test_cleanup_worktree.py` covers removal eligibility: unpushed commits, uncommitted edits, untracked files and ignored files keep the worktree; pushed commits and untouched worktrees allow removal with their private refs.

`test_submit_review.py` covers inline anchoring in `--dry-run`: lines must fall inside a hunk on their own side, ranges need both ends in the diff, and comments on files without a patch or outside the PR move into the review body. It also covers submission: Request changes on the viewer's own PR posts a Comment review, the duplicate guard applies to that fallback, and a rejected review reports GitHub's reason.
