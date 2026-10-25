---
name: deploy-check
description: "Checks a pending orders-api deploy for risky migrations and missing env vars. Use when asked to check, review, or approve a deploy or release of orders-api."
---

# Deploy check

1. List the commits going out: `git log --oneline origin/production..origin/main`.
2. For each new migration under `migrations/`, check it is backward compatible with the running code (no dropped or renamed columns the old code reads).
3. Compare new `process.env` reads in the diff with `infra/env/production.env`; every new variable needs a value there.
4. Report each risk with the commit and file, or "ready to deploy" when there are none.
