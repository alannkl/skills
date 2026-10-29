# Rollback

1. Run `kubectl rollout undo deploy/api -n <env>` and wait for `kubectl rollout status deploy/api -n <env>`.
2. Run `make health ENV=<env>` to confirm the previous version is healthy.
3. Post in #deploys: the environment, the bad SHA, and the failing health numbers.
4. If the rollback itself fails health, stop and tell the user; do not try another version.
