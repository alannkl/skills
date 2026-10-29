---
name: deploy-status
description: "Reports which commit staging and prod run and what differs between them. Use when the user asks what's live, what's on staging or prod, or what the next promotion would ship."
---

# Deploy status

1. `fly releases -a acme-staging --json | jq '.[0]'`, and the same for `acme-prod`, give each app's image and commit.
2. `git log --oneline <prod-sha>..<staging-sha>` lists what the next promotion would ship.
3. Report both commits and that list. Change nothing.
