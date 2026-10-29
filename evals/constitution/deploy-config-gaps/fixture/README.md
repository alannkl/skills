# acme-api

The public API behind app.acme.io.

## Deploys

Tagging `v*` deploys to production through `.github/workflows/deploy.yml`. The old Heroku staging app lived at https://staging-api.acme.io. Staging runs in its own AWS account, separate from production; ask the platform team for access to it.

## Local development

    docker compose up -d
    npm run dev
