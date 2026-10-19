---
type: regex
pattern: 'push[^\n]*main|main[^\n]*push'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

The push rule survives.
