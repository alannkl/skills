# CLAUDE.md

Shopfront — Next.js 14 storefront + admin for small merch shops.

## Commands
- `pnpm dev` — dev server on :3000
- `pnpm test` — vitest
- `pnpm lint`
- `pnpm db:studio` — Prisma Studio

## Stack
- Next.js app router, server actions for mutations
- Prisma + Postgres (local Postgres runs in docker compose)
- Tailwind, no CSS modules

## Conventions
- Server actions live in `app/**/actions.ts`, never inline in components
- Money is stored as integer cents (`priceCents`); format with `formatMoney()` from `lib/money.ts`
- Don't add new dependencies without asking

## Database
- Schema is in `prisma/schema.prisma`
- After changing the schema, create a migration with `pnpm prisma migrate dev --name <change>`
- Seed data: `pnpm db:seed`
