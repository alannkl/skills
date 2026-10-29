---
name: release-notes
description: Writes and publishes release notes for this project from merged changes. Use when the user asks for release notes, a changelog entry, a release summary, or to check the notes before a release.
---

# Release notes

This skill was added in March after the team kept writing inconsistent release notes. It is very important that you follow every step carefully and thoroughly.

## Workflow

1. Understand the request.
   - Read the user's request carefully and make sure you understand it.
   - Be thorough and use good judgment.
   - Identify the version being released.

2. Collect the changes.
   - Run `git log --oneline <previous-tag>..HEAD` to list merged changes.
   - The project's scripts are `npm run build`, `npm run test`, and `npm run lint`, defined in `package.json`.
   - Read each commit message carefully.
   - For monorepo releases, load `references/monorepo.md`.

3. Confirm the tag.
   - Run `git tag --list <version>` before writing anything. If the tag does not exist, stop and ask the user; publishing notes for an untagged version overwrites the previous release's notes on the CDN.

4. Write the notes to `notes/<version>.md`.
   - Start with a `## Release <version>` heading, followed by `### Added`, `### Fixed`, and `### Breaking`, in that order. `scripts/publish.py` parses these exact headings.
   - Never mention internal ticket IDs such as `OPS-1234`; the user does not want them in public notes.
   - Write in a clear, professional tone.
   - Make sure the notes are accurate.
   - Remember to keep the headings exactly as specified above, because the publish script parses them.
   - Do not include ticket IDs.

5. Publish.
   - Run `python scripts/publish.py notes/<version>.md`. It uploads the notes to the CDN, replacing what is there for that version.

6. Finish.
   - Double-check your work.
   - Tell the user you are done.

## Notes

- We tried free-form notes in January but the publish script broke.
- Always be careful.
