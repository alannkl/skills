# Releasing

Releases go out from an up-to-date, clean `main`.

1. Pick the bump from the Unreleased changelog entries: breaking changes are major, new features minor, fixes patch.
2. Run `.agents/skills/release/scripts/release.sh` from the repo root and answer its prompts.
3. Post the changelog section in `#releases`.

npm publish needs a one-time password from the authenticator app; the person releasing enters it.
