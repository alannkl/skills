---
type: regex
pattern: 'push[^\n]*main|main[^\n]*push'
flags: i
match: contains
target: {source: file, path: CLAUDE.md}
---

The rule against pushing to main survives.
