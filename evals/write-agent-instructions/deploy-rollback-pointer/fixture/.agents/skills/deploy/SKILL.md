---
name: deploy
description: "Deploys the api service to staging or production. Use when the user asks to deploy, ship, or roll out the api."
---

# Deploy

1. Confirm the branch is merged to `main` and CI is green: `gh run list --branch main --limit 1`.
2. Build and push the image: `make image TAG=$(git rev-parse --short HEAD)`.
3. Deploy: `make deploy ENV=<staging|production> TAG=<tag>`. Production needs the user's go-ahead first.
4. Watch the rollout: `kubectl rollout status deploy/api -n <env> --timeout=5m`.
5. Smoke test: `make smoke ENV=<env>`; it must exit 0.
6. Report the environment, tag, and smoke-test result.

See `references/rollback.md` for more.
