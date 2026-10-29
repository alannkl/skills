---
name: commit-message
description: Drafts a Conventional Commit message from the staged diff. Use when the user asks for a commit message or is about to commit.
---

1. Read the staged diff with `git diff --cached`. If nothing is staged, say so and stop.
2. Pick the type from what changed: `feat`, `fix`, `refactor`, `docs`, `test` or `chore`. Add a scope when one directory owns the change.
3. Write a subject under 72 characters, imperative mood, no trailing period.
4. Add a body only when the why is not obvious from the diff; wrap it at 72 characters.
5. Mention a breaking change in a `BREAKING CHANGE:` footer.
6. Show the message and wait; do not run `git commit` unless asked.
