# package-claude-md-dedupe

**Family:** 5 (remove rules another always-loaded file already covers). **Harness:** Claude Code, root + nested CLAUDE.md. **Domain:** TypeScript monorepo (Next.js + Fastify).

**User:** developer on the team who noticed the package file drifting into a copy of the root one.

**Why realistic:** nested CLAUDE.md files often start as copies of the root file. The user states the premise (both load) themselves.

**Good result:** packages/web/CLAUDE.md keeps the app-router line, server components, Tailwind, lib/api.ts, and the default-export exception for Next.js route files (on its own, or as "named exports per root, except ..."). Removes pnpm-only, no-deps, no-any/strict, conventional commits, lint+test. Root file untouched.

**Plausible bad results:** deleting the named-exports line wholesale because the root says "Use named exports"; the route-file exception is new information and Next.js requires it. Also: editing the root file, or "improving" the remaining rules.

**Judgment calls:** keeping the full near-duplicate line ("Use named exports, except ...") unchanged passes; it carries the qualifier. Leaving one of the five pure duplicates in fails `duplicates-removed`.
