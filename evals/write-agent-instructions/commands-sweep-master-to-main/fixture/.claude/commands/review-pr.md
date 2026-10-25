---
description: Review the current branch before opening a PR
---

Review the changes on this branch.

1. Run `git diff master...HEAD` and read every changed file in full, not just the hunks.
2. Check for missing tests, N+1 queries (look for loops over associations in views), and irreversible migrations.
3. Report findings as a numbered list, most serious first. Don't fix anything.
