---
name: deps
description: "Goes through open Dependabot PRs and merges the safe ones. Use when the user asks to handle, merge or clean up dependency update PRs."
---

# Dependabot PRs

1. List open Dependabot PRs: `gh pr list --author app/dependabot --state open --json number,title`.
2. For each PR, check CI with `gh pr checks <number>`. Skip PRs whose checks are pending; note failed ones.
3. Read the update type from the title (`from 1.2.3 to 1.2.4`): patch, minor or major.
4. Merge each patch or minor update with green CI: `gh pr merge <number> --squash --delete-branch`.
5. For each major update with green CI, read the release notes in the PR body (`gh pr view <number> --json body`) and search `src/` with `rg` for every API the notes say changed or was removed. Merge only if none is used; otherwise comment on the PR with the affected files (`gh pr comment <number> --body ...`) and leave it open.
6. Report what was merged, what was left open and why, and which PRs failed CI.
