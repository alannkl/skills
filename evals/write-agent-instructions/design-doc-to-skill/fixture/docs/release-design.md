# Release check design

Status: draft, not yet verified on a real release.

## Background

We chose a pre-release check after the 2.3 release shipped a lockfile that did not match the tag. We considered a CI-only check but chose an agent skill because releases are often cut from laptops.

## Checks

The agent runs these before any release:

1. Confirm the working tree is clean.
2. Confirm the version in `package.json` matches the tag being released.
3. Confirm `CHANGELOG.md` has an entry for that version.
4. Run `pnpm test` and stop if it fails.

We also learned that the lockfile drifts, so the agent must compare the tag's lockfile hash with the `main` branch's lockfile hash and stop on a mismatch. Because uploads time out under load, the agent retries the artifact upload; start with 3 retries and lower it after we measure real failure rates. Finally, the agent posts the release summary in `#releases` only after the upload succeeds.

## Review notes

> Reviewer (Dana): do we need the changelog check if the release bot writes it? Leaving it in for now.
