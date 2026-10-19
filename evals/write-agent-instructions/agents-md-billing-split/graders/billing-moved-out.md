---
type: regex
pattern: 'ISO 4217'
flags: i
match: not_contains
target: {source: file, path: AGENTS.md}
---

Billing-only detail no longer sits in the root file.
