# AGENTS.md

## Project

Orders API: a TypeScript service on Node 22 with Fastify and PostgreSQL. Source is in `src/`, database migrations in `migrations/`, docs in `docs/`.

## Commands

- Install: `pnpm install`
- Dev server: `pnpm dev` (needs `docker compose up -d db` first)
- Tests: `pnpm test`; one file: `pnpm test src/orders/service.test.ts`
- Lint and types: `pnpm lint && pnpm typecheck`

## Conventions

- Validate request bodies with the zod schemas in `src/schemas/`; never trust `req.body` past the route handler.
- Money is integer cents everywhere; format only at the API boundary.
- New migrations get the next number in `migrations/`; never edit an applied one.

## Documentation

- Keep `docs/` current with the code: update the doc for any endpoint, env var or command you change.
- `docs/architecture.md` describes modules and data flow; `docs/runbook.md` covers deploys and incident steps.

## Git

- Branch from `main`; open PRs against `main`.
- Commit messages follow Conventional Commits.
