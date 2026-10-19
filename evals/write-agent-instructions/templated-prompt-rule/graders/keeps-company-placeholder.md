---
type: regex
pattern: '\{\{company_name\}\}'
flags: ''
match: contains
target: {source: file, path: prompts/support.ts}
---

The render placeholder survives.
