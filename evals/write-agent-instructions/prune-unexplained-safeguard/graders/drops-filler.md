---
type: regex
pattern: 'clean, readable|try your best|double-check your work'
flags: i
match: not_contains
target: {source: file, path: AGENTS.md}
---

Filler lines are gone.
