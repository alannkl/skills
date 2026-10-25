---
name: precommit
description: "Runs this repo's CI checks locally before a commit. Use before committing, or when asked to run precommit or pre-push checks."
---

# Precommit

Run the same checks CI runs, from the repository root, before every commit:

1. `npm run lint`
2. `npm run typecheck`
3. `npm test`

Fix any failure and rerun that check before committing; never commit with a failing check. Report each check's result in one line.
