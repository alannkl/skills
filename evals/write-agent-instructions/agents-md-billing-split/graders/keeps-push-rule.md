---
type: regex
pattern: 'push[^\n]*main|main[^\n]*push'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

The universal push rule stays in AGENTS.md.
