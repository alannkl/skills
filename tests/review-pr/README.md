# Review-PR tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/review-pr -v
```

The suite runs the bundled scripts with Node.js against disposable Git repositories. A fake `gh` answers from fixture JSON, and a fake SSH transport serves `github.com` fetches from a local bare repository, so nothing reaches GitHub.

`test_cleanup_worktree.py` covers removal eligibility: unpushed commits, uncommitted edits, untracked files and ignored files keep the worktree; pushed commits and untouched worktrees allow removal with their private refs.

`test_check_approved_paths.py` covers the approved-path boundary: edits within the list pass, unapproved staged and untracked files are unexpected, and a rename counts under both names.

`test_push_fixes.py` covers pushing fixes: a dry run lists the commits without pushing, a push fast-forwards the remote source branch without publishing tags, a second push follows earlier fixes, and a moved or rewound PR head, a dirty worktree, missing source metadata or nothing to push each stop before any push.

`test_submit_review.py` covers inline anchoring in `--dry-run`: only the ending line must fall inside a hunk on its own side, supplied ranges remain in the comment text, and invalid ending anchors move into the review body with their location. It also covers submission: Request changes on the viewer's own PR posts a Comment review, the duplicate guard applies to that fallback, and a rejected review reports GitHub's reason.

`test_api_host.py` covers github.com routing with normal and overridden `GH_HOST`, including REST and GraphQL pagination, thread replies, and review submission. The posted payload uses only single-line anchors.
