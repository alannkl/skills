---
type: regex
pattern: '\$\{toolList\.join\(''[^'']*''\)\}'
flags: ''
match: contains
target: {source: file, path: prompts/support.ts}
---

The tool list interpolation survives.
