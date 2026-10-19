---
type: llm
focus: {source: file, path: skills/release-check/SKILL.md}
---

Judge `skills/release-check/SKILL.md`. It tells the agent to do all seven of these before a release: confirm a clean working tree; confirm the `package.json` version matches the tag; confirm `CHANGELOG.md` has an entry for that version; run `pnpm test` and stop on failure; compare the tag's lockfile hash with `main`'s and stop on a mismatch; retry the artifact upload a definite number of times; post the summary in `#releases` only after the upload succeeds. If its description says it also applies to checking whether a release is ready, a readiness check stops before uploading or posting.
