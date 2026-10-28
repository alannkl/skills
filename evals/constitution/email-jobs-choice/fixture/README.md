# Tally

Invoicing for small studios. Flask + Postgres, Redis for caching.

Production is one VM running `docker compose up -d`; deploys are `git pull && docker compose up -d --build`.

## Email

Transactional email goes through Postmark's SMTP relay (`SMTP_*` in `.env`). We send about 300 emails a day: welcome emails, invoice emails, and password resets.
