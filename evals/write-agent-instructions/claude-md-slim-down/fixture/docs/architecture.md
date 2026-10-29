# Architecture

Ledger is one Node 22 service. Express routes in `src/api/routes.ts` dispatch to handlers in `src/api/handlers/`, which read and write Postgres 16 through the query layer in `src/db/`.
Stripe webhooks arrive at `/webhooks/stripe` and update invoice payment status.
The public contract is `openapi.yaml`; `clients/ts/` is generated from it and published to the internal registry.
Production runs on two containers behind a load balancer; `deploy-production` in GitHub Actions ships each release tag.
