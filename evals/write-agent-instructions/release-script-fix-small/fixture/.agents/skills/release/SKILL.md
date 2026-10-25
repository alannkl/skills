---
name: release
description: "Releases @acme/feature-flags to npm. Use when asked to release, publish, or cut a version of the package."
---

# Release

1. Make sure you are on `main` and the working tree is clean.
2. Run `scripts/release.sh` and follow its prompts. It runs the checks, bumps the version, updates `CHANGELOG.md`, and commits and tags the release locally.
3. Ask the user before publishing. After their ok, push with `git push origin main --follow-tags`; the user runs `npm publish` and enters the one-time password.
4. Tell the user the new version and paste the changelog section for `#releases`.
