---
type: llm
focus: {source: file, path: skills/release/SKILL.md}
---

Judge the edited `skills/release/SKILL.md`. The original pointed to `references/checklist.md` with Markdown links, one of them a section name followed by a link to the same section ("the Rollback section ([Rollback](references/checklist.md#rollback))"). Pass only if each pointer now names its target once: a plain path such as `references/checklist.md`, with the Rollback section named in prose, and no Markdown link, `#anchor`, or section title repeated as link text. Everything else must survive with its meaning: confirm `main` is green in CI or stop and report the failing job; work through the checklist before tagging; `git tag vX.Y.Z` and push the tag; `deploy.sh production`; on a failed deploy, follow the Rollback section and tell the user which step failed; the checklist is never skipped. Fail if any of these is lost or changed.
