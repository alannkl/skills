# Promoting staging to prod

Prod runs the image staging has already verified; we never build for prod directly. Promote at most once a day, before 16:00 SGT, and never on Fridays.

## Before promoting

1. CI is green for the commit staging runs: `gh run list --branch main --commit <staging-sha> --json conclusion` shows `success`.
2. Staging is healthy: `curl -fsS https://staging.acme.dev/healthz` prints `ok`.
3. No migration needs a manual step: `fly ssh console -a acme-staging -C "bin/rails db:migrate:status"` lists nothing marked `manual`.
4. Nobody has posted a hold in #deploys today. Ask in the channel if unsure.

## Promote

5. `fly deploy -a acme-prod --image "$(fly releases -a acme-staging --json | jq -r '.[0].ImageRef')"`
6. Watch `https://api.acme.dev/healthz` for five minutes. If it fails twice in a row, roll back with `fly releases rollback -a acme-prod` and post in #incidents.
7. Post in #deploys: `promoted <sha> to prod` with `git log --oneline <old-prod-sha>..<sha>`.

## Background

We moved from Heroku pipelines to Fly in March 2025. `heroku pipelines:promote` no longer applies.

## Quarterly: rotate the Fly deploy token

1. `fly tokens create deploy -a acme-prod --expiry 2160h`
2. Update `FLY_API_TOKEN` in the GitHub Actions secrets.
3. Revoke the old token: `fly tokens revoke <id>`.
