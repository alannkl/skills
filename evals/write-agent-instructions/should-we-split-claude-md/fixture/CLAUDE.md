# CLAUDE.md

Tallyho — invoicing SaaS for freelancers. Django 5 monolith, Postgres, Celery for background jobs, HTMX on the frontend (no SPA).

## Setup

    uv sync
    cp .env.example .env
    docker compose up -d db redis
    uv run manage.py migrate
    uv run manage.py runserver

Python 3.10+.

## Commands

- `uv run pytest` — full test suite (~2 min)
- `uv run pytest apps/<app>` — one app
- `uv run ruff check . && uv run ruff format --check .` — lint/format
- `uv run mypy apps` — types
- `uv run manage.py makemigrations <app>` — new migration
- `uv run celery -A config worker -l info` — run workers locally

## Layout

- `config/` — settings, urls, celery app
- `apps/<app>/` — one Django app per domain: `accounts`, `billing`, `core`
- `templates/` — shared templates; app templates live in `apps/<app>/templates/<app>/`
- `static/` — CSS (Tailwind build output is committed)

## Code style

- Business logic goes in `services.py` per app, not in views or models. Views stay thin.
- Use `select_related`/`prefetch_related` in list views; we've had N+1s in prod before.
- Money is `Decimal`, never float. Use `core.money.Money` for anything with a currency.
- Timestamps are timezone-aware UTC. Use `django.utils.timezone.now()`, never `datetime.now()`.
- No raw SQL unless there's a comment explaining why the ORM can't do it.
- Type hints on all new functions.

## Tests

- pytest + pytest-django; factories in `apps/<app>/tests/factories.py` (factory_boy)
- Every bug fix gets a regression test.
- Don't hit the network in tests; Stripe and email are mocked via fixtures in `conftest.py`.
- Celery runs eagerly in tests (`CELERY_TASK_ALWAYS_EAGER`), so tasks can be tested by calling them.

## Migrations

- One migration per PR per app; squash locally if you made several.
- Never edit a migration that's been merged to main.
- Data migrations must be reversible (provide `reverse_code`), or explain why not.
- Large table changes (`billing_invoice`, `billing_lineitem`) need a separate, non-locking migration plan; ask first.

## Background jobs

- Tasks live in `apps/<app>/tasks.py`.
- Tasks must be idempotent; they can be retried.
- Pass IDs to tasks, not model instances.

## Git / PRs

- Branch from `main`, name `feat/...` or `fix/...`.
- Conventional commits.
- Don't commit `.env` or anything under `media/`.
- Run lint, types and tests before saying you're done.
