# Rollback

Use when a rollout times out, pods crash-loop, or the smoke test fails after a deploy.

1. If the failed release ran a database migration, stop and ask the user before rolling back; the down migration may drop data.
2. Save the failing pods' logs: `kubectl logs -n <env> -l app=web --previous > rollback-<sha>.log`.
3. Roll back to the last good release: `scripts/rollback.sh --env <env> --to <previous-sha>`.
4. Tell the user what failed and which release is live now.
