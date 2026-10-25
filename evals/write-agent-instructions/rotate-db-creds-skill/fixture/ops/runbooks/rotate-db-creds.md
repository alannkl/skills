# Rotate Postgres app credentials (orders)

Owner: platform. Last run: 2026-03-02 (jt)

We use Vault's database secrets engine with static roles. Rotation = tell Vault to rotate, then make the consumers pick up the new password. Static-role rotation is immediate: the old password stops working right away, so do the restart steps straight after rotating.

Do staging first, then prod. Never both at once.

## Prereqs
- `vault login -method=oidc` (platform-admins group)
- kube context for the env: `kubectl config use-context staging` (or `prod`)

## Steps (ENV = staging or prod)
1. Check the role exists and note `last_vault_rotation`: `vault read database/static-roles/orders-app-ENV`
2. Rotate: `vault write -f database/rotate-role/orders-app-ENV`
3. External Secrets only refreshes every 1h, so force a sync:
   `kubectl -n orders annotate externalsecret orders-db force-sync=$(date +%s) --overwrite`
4. Restart consumers: `kubectl -n orders rollout restart deploy/orders-api deploy/orders-worker`
5. Wait: `kubectl -n orders rollout status deploy/orders-api --timeout=5m` (same for `orders-worker`)
6. Verify: `kubectl -n orders logs deploy/orders-api --since=5m | grep -i "password authentication failed"` should print nothing. Check the Orders dashboard error rate is flat.

## If it goes wrong
Pods crashlooping with auth errors = they still have the old secret. Re-run step 3, then step 4. Don't rotate again; that just makes it worse.

## Notes
- The migrate job (`orders-migrate`) also uses these creds but only runs on deploy; nothing to do.
- There used to be a `rotate.sh` in this folder. It's gone; do it by hand.
