---
type: regex
pattern: 'billing-changes\.md|manual_review'
flags: i
match: not_contains
target: {source: file, path: AGENTS.md}
---

The billing-only migration and refund rules no longer sit in the root file.
