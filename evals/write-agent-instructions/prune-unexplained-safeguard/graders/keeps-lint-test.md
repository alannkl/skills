---
type: regex
pattern: 'make lint[\s\S]*make test|make test[\s\S]*make lint'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

The lint and test rule survives.
