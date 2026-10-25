# Runbook

## Deploy

1. Merge to `main`; CI builds and pushes the image.
2. Run `pnpm migrate:prod` from the release job.
3. Watch error rate on the Orders dashboard for 15 minutes.

## Webhook retry storm (2026-09-14, 2026-10-02)

Stripe retried a failed webhook 2,000+ times after a deploy at 14:02.

- 14:05 alerts fired on queue depth
- 14:11 rolled back
- 14:20 queue drained; root cause: missing `STRIPE_WEBHOOK_SECRET` in the new task definition
- 2026-10-02: same thing again at 09:40, fixed at 09:58

Steps: check `STRIPE_WEBHOOK_SECRET` in the task definition, redeploy, then replay failed events from the Stripe dashboard.
