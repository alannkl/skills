---
name: ship
description: Builds, deploys and announces a release of the API service. Use when the user asks to ship, release or deploy the API.
---

# Ship

Please make sure to carefully follow each of the steps below, in order, and don't skip any of them.

1. Make sure CI is green on the commit you are shipping by running the CI status command (`gh run list --commit <sha> --limit 1`).
2. Tag the commit with the version from `package.json` and push the tag.
3. Build the image with `make release` (needs Docker running; takes about 10 minutes).
4. Deploy with `deploy.sh` (production only; staging uses `deploy-staging.sh`). It is generally preferable to pass `--blue-green`, unless the release includes a database migration, in which case you should leave it off.
5. Run the smoke tests (`make smoke`) against the environment you just deployed to.
6. Post the release notes with `post_notes` (channel `#releases`, never `#general`).
7. If any step fails, stop and report the failing command and its output.

## Notes

- IMPORTANT: NEVER EVER ship on a Friday after 15:00 UTC!!!
- Release tags use the date, such as `v2026.10.29`.
