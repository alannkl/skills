---
type: regex
pattern: '^export\ const\ POLICY\ =\ \{\ refundCap:\ 200,\ currency:\ ''EUR''\ \}\ as\ const;\n\nexport\ const\ ESCALATION_MARKER\ =\ ''\[\[ESCALATE\]\]'';\n$'
flags: ''
match: contains
target: {source: file, path: prompts/policy.ts}
---

The policy constants are untouched.
