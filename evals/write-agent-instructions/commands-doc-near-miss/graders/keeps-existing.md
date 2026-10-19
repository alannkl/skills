---
type: regex
pattern: '/changelog[\s\S]*/release-notes'
flags: i
match: contains
target: {source: file, path: docs/commands.md}
---

Existing entries survive.
