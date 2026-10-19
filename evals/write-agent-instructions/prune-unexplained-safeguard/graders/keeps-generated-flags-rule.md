---
type: regex
pattern: 'flags\.generated\.json'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

The unexplained generated-file rule survives.
