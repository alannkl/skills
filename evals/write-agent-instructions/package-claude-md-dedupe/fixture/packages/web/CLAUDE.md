# packages/web

Next.js 14 with the app router.

- pnpm only, never npm or yarn.
- Use named exports, except Next.js route files (`page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`), which must use a default export.
- Server components by default; add `"use client"` only for state, effects or browser APIs.
- Styling is Tailwind; no CSS modules or styled-components.
- No `any`. TypeScript is strict.
- All data fetching goes through `lib/api.ts`; never call `fetch` directly in components.
- Don't add deps without asking.
- Commit messages follow conventional commits.
- Run `pnpm -r lint` and `pnpm -r test` before you're done.
