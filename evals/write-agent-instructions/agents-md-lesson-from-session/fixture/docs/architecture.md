# Architecture

Requests enter through Fastify routes in `src/routes/`, which validate input with zod and call services in `src/<domain>/service.ts`. Services own business rules and talk to PostgreSQL through repositories in `src/<domain>/repo.ts`. Background jobs run from `src/jobs/` on a BullMQ queue backed by Redis.

## Modules

- `orders`: order lifecycle, from cart checkout to fulfilment.
- `payments`: Stripe intents and webhooks; amounts in integer cents.
- `inventory`: stock reservations, released after 15 minutes without payment.
