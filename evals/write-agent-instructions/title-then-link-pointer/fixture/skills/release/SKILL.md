---
name: release
description: Cuts and deploys a release of the web app. Use when the user asks to release, ship, or deploy a new version.
---

# Release

1. Confirm `main` is green in CI. If it is not, stop and report the failing job.
2. Work through the release checklist ([release checklist](references/checklist.md)) before tagging.
3. Tag the release with `git tag vX.Y.Z` and push the tag.
4. Run `deploy.sh production`.
5. If the deploy fails, follow the Rollback section ([Rollback](references/checklist.md#rollback)) and tell the user which step failed.

It is very important that you never skip the checklist.
