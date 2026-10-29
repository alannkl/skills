---
name: release
description: "Cuts a release of the acme CLI: writes the changelog entry, bumps the version, tags it, and pushes the tag so CI publishes to npm. Use when the user asks to release, cut, ship, or publish a new version."
---

# Release

1. Ask the user for the bump (`patch`, `minor` or `major`) unless they gave it.
2. Add a section for the new version at the top of `CHANGELOG.md`: `## [<version>] - <YYYY-MM-DD>`, then `### Added` and `### Fixed` with the user-facing changes from `git log --oneline $(git describe --tags --abbrev=0)..HEAD`. Commit it.
3. Run this skill's `scripts/release.sh <bump>`. It bumps `package.json`, commits, tags `v<version>` and pushes `main` and the tag; the publish workflow then releases to npm.
   - `--dry-run` after the bump prints the version it would release and changes nothing.
   - Exit 1: not on `main`, or the working tree is dirty. Fix that and rerun.
4. Post the new CHANGELOG section in #releases.
