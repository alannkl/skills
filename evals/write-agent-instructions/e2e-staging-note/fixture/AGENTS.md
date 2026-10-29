# AGENTS.md

Storefront web app: Next.js 15, TypeScript, pnpm.

## Commands

- `pnpm dev`: local server on :3000
- `pnpm test`: unit tests (vitest)
- `pnpm e2e`: Playwright suite against staging (https://staging.shopfront.dev)
- `pnpm e2e:local`: the same suite against `pnpm dev`; start the dev server first
- `pnpm lint && pnpm typecheck`

## Testing

- Add or update a unit test for every behavior change.
- Before opening a PR that touches `app/checkout/` or `app/account/`, run `pnpm e2e`.

## Git

- Branch from `main`; Conventional Commits.
