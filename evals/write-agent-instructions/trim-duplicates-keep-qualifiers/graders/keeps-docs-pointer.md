---
type: regex
pattern: 'docs/architecture\.md'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

The docs pointer survives.
