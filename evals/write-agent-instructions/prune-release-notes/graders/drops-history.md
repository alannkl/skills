---
type: regex
pattern: 'March|January'
flags: i
match: not_contains
target: {source: file, path: release-notes/SKILL.md}
---

History lines are removed.
