---
type: regex
pattern: 'name:\s*release-check\b'
flags: i
match: contains
target: {source: file, path: skills/release-check/SKILL.md}
---

The frontmatter name matches the directory.
