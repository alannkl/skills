---
type: regex
pattern: '^description: (?![\"''>|])[^\n]*\s#'
flags: 'm'
match: not_contains
target: {source: file, path: skills/release-check/SKILL.md}
---

An unquoted description containing " #" is cut off by YAML at that point.
