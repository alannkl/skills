---
description: Bring the current branch up to date
---

1. Make sure the working tree is clean; if not, stop and tell me.
2. `git fetch origin`
3. `git rebase origin/master`
4. If there are conflicts, stop and list the conflicting files. Don't resolve them yourself.
5. Run `bin/rails test` and report the result.
