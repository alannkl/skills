---
name: prepare-pr
description: "Prepares the current branch for a pull request: checks the working tree, runs lint, types and tests, and opens the PR against main. Use when the user asks to prepare, open, or create a PR."
---

# Prepare PR

1. Run `git status --porcelain` and read the output.
2. Run `git fetch origin main`.
3. Run `git log --oneline origin/main..HEAD` to list the commits that will go into the PR.
4. Run `git diff --stat origin/main...HEAD` to see the changed files.
5. Run `pnpm lint`.
6. Run `pnpm typecheck`.
7. Run `pnpm test`.
8. Run `pnpm build`.
9. If the working tree has uncommitted changes, ask the user whether to commit them, leave them out, or stop.
10. If lint, typecheck, tests or build failed, show the failures and stop.
11. Run `git rebase origin/main` if the branch is behind `origin/main`. On conflicts, stop and show them.
12. Run `git push -u origin HEAD`.
13. Draft the PR title and body from the commits and the diff stat: a Conventional Commits title, then a summary and a test plan.
14. Show the draft to the user and wait for approval.
15. Run `gh pr create --base main --title "<title>" --body "<body>"`.
16. Report the PR URL.
