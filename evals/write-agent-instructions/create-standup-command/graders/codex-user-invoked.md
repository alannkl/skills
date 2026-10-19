---
type: regex
pattern: 'allow_implicit_invocation:\s*false'
flags: i
match: contains
target: {source: file, path: skills/standup/agents/openai.yaml}
arm: with-only
---

Convention check, not scored: Codex treats it as user-invoked.
