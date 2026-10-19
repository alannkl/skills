---
type: regex
pattern: 'disable-model-invocation:\s*true'
flags: i
match: contains
target: {source: file, path: skills/standup/SKILL.md}
arm: with-only
---

Convention check, not scored: Claude Code treats it as a user-invoked slash command.
