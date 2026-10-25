# AGENTS.md

## Project
`ledgerflow` — nightly ETL that pulls transactions from the payments API, normalises them, and loads them into the warehouse (Postgres locally, Redshift in prod).

## Layout
- `ledgerflow/extract/` — API clients
- `ledgerflow/transform/` — pure functions, no IO
- `ledgerflow/load/` — warehouse writers
- `dags/` — Airflow DAG definitions
- `tests/unit/`, `tests/integration/`

## Setup
    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"

## Testing
- `pytest tests/unit` — fast, run before every commit
- Integration tests need a database.
- `ruff check .` and `mypy ledgerflow` must pass

## Conventions
- Transforms take and return DataFrames; never mutate the input
- All timestamps are UTC; convert at the extract boundary
- New DAGs need an `owner` in `default_args`
