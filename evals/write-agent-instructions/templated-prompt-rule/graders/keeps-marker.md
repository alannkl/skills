---
type: regex
pattern: '\$\{ESCALATION_MARKER\}'
flags: ''
match: contains
target: {source: file, path: prompts/support.ts}
---

The escalation marker is still interpolated.
