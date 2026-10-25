# Rollback

Use when a rollout times out, pods crash-loop, or the smoke test fails.

1. Do not retry the same tag. Roll back first: `kubectl rollout undo deploy/api -n <env>`.
2. Wait for it: `kubectl rollout status deploy/api -n <env> --timeout=5m`.
3. Run `make smoke ENV=<env>` against the previous version.
4. Collect the failing pods' logs: `kubectl logs -n <env> -l app=api --previous --tail=200 > rollback-<tag>.log`.
5. Tell the user: the failed tag, the step that failed, the rollback result, and the log path. Do not redeploy until the user decides.

Database migrations are not rolled back by `rollout undo`. If the failed tag ran a migration, say so and ask before doing anything else.
