---
name: deploy
description: "Deploys the api service to staging or production with kubectl. Use when the user asks to deploy, ship, or roll out the api."
---

# Deploy

This skill was written after the March outage, when a deploy went out with a broken migration. Follow every step carefully.

1. Before anything else, read `references/canary.md`, `references/rollback.md` and `references/hotfix.md` in full so you have the whole picture.
2. Confirm the environment (`staging` or `production`) and the commit SHA. A production deploy needs the user's explicit "yes, deploy to production" in this conversation; never infer it from earlier messages.
3. Run `make migrate-check ENV=<env>`. If it reports a migration that is not backward compatible, stop and ask the user.
4. Deploy:
   - Run `kubectl set image deploy/api api=registry.internal/api:<sha> -n <env>`, then `kubectl rollout status deploy/api -n <env> --timeout=5m`.
   - For production, deploy the canary first, as `references/canary.md` describes.
5. Health gate:
   - Run `kubectl logs deploy/api -n <env> --since=15m --all-containers` and keep the full output in your notes for the report.
   - Run `make health ENV=<env>`. The gate passes when the error rate stays under 1% and p95 latency under 400 ms for 10 minutes.
6. If the health gate in step 5 fails, roll back as `references/rollback.md` describes. Do not retry the deploy.
7. Report: summarize what you did, then end with one line, `DEPLOY: ok <env> <sha>` or `DEPLOY: rolled-back <env> <sha>`.

## Notes

- Production is important, so be careful and double-check everything.
- Hotfix deploys skip the canary but still run the health gate; see `references/hotfix.md`.
- We deployed with Helm until May.
