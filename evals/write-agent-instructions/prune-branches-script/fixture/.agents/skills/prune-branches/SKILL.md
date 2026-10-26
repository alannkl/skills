---
name: prune-branches
description: "Deletes git branches that are already merged into main, locally and on origin. Use when the user asks to clean up, prune or delete old or merged branches."
---

# Prune merged branches

Run these from the repository root, one at a time, and check each output before the next.

1. `git fetch --prune origin` to drop remote-tracking refs for branches already deleted on origin.
2. `git checkout main && git pull --ff-only` so main is current.
3. `git branch --merged main` to list local branches merged into main. Remove `main` and any `release/*` branch from the list; those are never deleted.
4. For each remaining branch: `git branch -d <branch>`.
5. `git branch -r --merged origin/main` to list remote branches merged into main. Remove `origin/main`, `origin/HEAD` and any `origin/release/*`.
6. Show the user the remote branches you are about to delete and wait for their ok.
7. For each one they approve: `git push origin --delete <branch>`.
8. Tell the user how many local and remote branches were deleted.
