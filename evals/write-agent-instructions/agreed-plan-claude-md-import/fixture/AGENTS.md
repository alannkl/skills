# AGENTS.md

Quillnote API — FastAPI + Postgres backend for the Quillnote notes app.

## Setup

    pip install -r requirements.txt
    uvicorn app.main:app --reload

Needs a local Postgres; copy `.env.example` to `.env`.

## Testing

- Run `pytest` from the repo root.
- Tests use a separate database, `quillnote_test`, created by the `db` fixture in `tests/conftest.py`.
- Run the whole suite before you finish: `pytest`.
- Every bug fix needs a regression test.
- The `db` fixture creates `quillnote_test` for you; don't point tests at the dev database.

## Conventions

- Routers in `app/routers/`, one per resource. Business logic in `app/services/`.
- Pydantic v2 models for all request and response bodies.
- Use `async def` handlers and the async SQLAlchemy session from `app.db.get_session`.
