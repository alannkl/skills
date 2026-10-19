---
type: regex
pattern: 'gh pr list --search ["'']?review-requested:@me'
flags: i
match: contains
target: {source: file, path: skills/standup/SKILL.md}
---

The user's exact gh command survives.
