---
type: regex
pattern: '\]\('
flags: ''
match: not_contains
target: {source: file, path: skills/release/SKILL.md}
---

No pointer is written as a Markdown link; each is a plain path, with any section named in prose.
