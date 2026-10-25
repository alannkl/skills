# CLAUDE.md

Tidepool monorepo (pnpm workspaces):
- `packages/web` — Next.js 14 frontend
- `packages/api` — Fastify API
- `packages/shared` — types and zod schemas shared by both

## Rules
- pnpm only; never npm or yarn.
- Don't add dependencies without asking.
- TypeScript strict mode; no `any` (use `unknown` and narrow).
- Use named exports.
- Conventional commits, scoped by package: `feat(web): ...`, `fix(api): ...`.
- Before saying you're done, run `pnpm -r lint` and `pnpm -r test`.
