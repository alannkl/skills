---
name: release-notes
description: "Writes release notes for a tagged version from its merged pull requests. Use when the user asks for release notes."
---

# Release notes

1. Confirm the tag exists with `git tag --list <version>`; if it does not, stop and ask.
2. List merged PRs since the previous tag: `git log --merges --oneline <previous-tag>..<version>`.
3. Add a `## [<version>] - <YYYY-MM-DD>` section at the top of `CHANGELOG.md` with `### Added`, `### Fixed` and `### Breaking`, one line per PR ending in `(#<number>)`.
4. Leave out internal ticket IDs such as `OPS-1234`.
