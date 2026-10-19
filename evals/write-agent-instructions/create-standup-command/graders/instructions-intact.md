---
type: llm
focus: {source: file, path: skills/standup/SKILL.md}
---

Judge `skills/standup/SKILL.md`. It preserves the user's three requests: summarize what the user merged yesterday from git log; list open PRs they are reviewing with `gh pr list --search review-requested:@me` (quoting the search term is fine); draft three standup bullets. Added detail must not change whose work is summarized, widen the time interval, or invent plans or blockers that the gathered data does not support.
