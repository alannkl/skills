---
type: regex
pattern: 'not yet verified|after we measure|reviewer|dana|2\.3 release|we considered'
flags: i
match: not_contains
target: {source: file, path: skills/release-check/SKILL.md}
---

Draft status, staged values, reviewer notes and design history stay out of the skill.
