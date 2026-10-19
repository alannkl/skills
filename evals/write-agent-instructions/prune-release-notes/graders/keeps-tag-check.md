---
type: llm
focus: {source: file, path: release-notes/SKILL.md}
---

Judge `release-notes/SKILL.md`. Before any notes are written, it confirms the release tag exists (for example with `git tag --list <version>`), and if the tag is missing it stops and asks the user.
