# Release checklist

## Before tagging

- Update `CHANGELOG.md` with every merged pull request since the last tag.
- Bump the version in `package.json`.

## Rollback

1. Run `deploy.sh production --version <previous tag>`.
2. Confirm the health check at `/healthz` returns 200.
3. Open an incident issue labelled `release-rollback`.
