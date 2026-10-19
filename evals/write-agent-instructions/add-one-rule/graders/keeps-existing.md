---
type: regex
pattern: '- Use pnpm, never npm or yarn\.[\s\S]*- Run `pnpm test` before opening a pull request\.[\s\S]*- Open pull requests against `develop`\.'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

Existing rules are unchanged and keep their order; the new rule may go anywhere in the list.
