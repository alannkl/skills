---
type: regex
pattern: 'src/billing/AGENTS\.md'
match: contains
target: {source: file, path: AGENTS.md}
---

The root file points to the billing file, since agents read only the root file.
