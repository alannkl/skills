---
type: regex
pattern: 'name:\s*deploy-review\b'
flags: i
match: contains
target: {source: file, path: skills/deploy-review/SKILL.md}
---

The frontmatter name matches the directory.
