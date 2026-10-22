---
name: ship
description: Builds and deploys the API service and announces the release. Use when the user asks to ship or deploy the API.
---

# Ship

Please make sure to carefully follow each of the steps below, in order.

1. Build the image with `make release` (needs Docker running; takes about 10 minutes).
2. Run `deploy.sh` (production only; staging uses `deploy-staging.sh`).
3. Post the release notes with `post_notes` (channel `#releases`, never `#general`).
4. If any step fails, stop and report the failing command and its output to the user.
