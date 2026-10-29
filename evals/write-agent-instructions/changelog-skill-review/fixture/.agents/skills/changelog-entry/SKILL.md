---
name: changelog-entry
description: "Adds an entry for the current branch's change to CHANGELOG.md. Use when asked to add, write, or update a changelog entry."
---

# Changelog entry

Add one line under `## [Unreleased]` in `CHANGELOG.md` saying what the branch changes for users, or report that it needs none.

1. Run `git fetch origin main`, then read the change with `git log --oneline origin/main..HEAD` and `git diff origin/main...HEAD`.
2. Decide whether users can see the change. Refactors, test-only changes, CI changes and dependency bumps with no behavior change need no entry: say so and stop.
3. Pick the section: `### Added` for new features, `### Changed` for changed behavior, `### Fixed` for bug fixes. If it is missing under `## [Unreleased]`, create it, keeping the order Added, Changed, Fixed.
4. Write one line in the present tense saying what users can now do or no longer hit, ending with the PR number when there is one: `- Export orders as CSV from the Orders page (#418)`.
5. Run `pnpm changelog:check` and fix what it reports.

Entries are copied verbatim into the app's What's New panel, so describe the effect users see, not the implementation: "Saved carts survive sign-out", not "Persist carts in Redis".

Never edit the section of a released version; a correction to a released entry goes in as a new `### Fixed` line under `## [Unreleased]`.
