---
type: regex
pattern: '- Use pnpm, never npm or yarn\.\n- Run `pnpm test` before opening a pull request\.\n- Open pull requests against `develop`\.'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

Existing rules are unchanged.
