---
name: deploy
description: Deploys the web service to staging or production. Use when the user asks to deploy, ship to staging, or release to production.
---

# Deploy

1. Check CI passed on the commit: `gh run list --commit <sha> --limit 1`.
2. Build and push the image: `make image TAG=<sha>`.
3. Deploy: `make deploy ENV=<staging|production> TAG=<sha>`. Production needs the user's go-ahead in this conversation.
4. Watch the rollout: `kubectl rollout status deploy/web -n <env> --timeout=5m`.
5. Run `make smoke ENV=<env>`; it must exit 0.
6. Report the environment, tag and smoke-test result.

## References

- [Rollback](references/rollback.md) - more information about rollbacks.
