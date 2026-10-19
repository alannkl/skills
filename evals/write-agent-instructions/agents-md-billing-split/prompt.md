---
tags: [structural, context-design]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write]
---

Our agents read only the root AGENTS.md when a session starts. Restructure it so billing-only guidance moves to `src/billing/AGENTS.md` and loads only when an agent works on billing code; keep any requirement that other code also needs available to that code. Keep everything it requires.
