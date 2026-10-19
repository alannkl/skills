---
type: regex
pattern: 'name:\s*standup\b'
flags: i
match: contains
target: {source: file, path: skills/standup/SKILL.md}
---

The frontmatter name matches the directory.
