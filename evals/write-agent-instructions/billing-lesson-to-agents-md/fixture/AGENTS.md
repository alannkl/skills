# Agent instructions

- Python 3.12, managed with `uv`; run `uv run pytest` for tests.
- Run `make lint` before committing.
- Never push directly to `main`.
- Money is `Decimal`, never `float`.
- `src/billing/` talks to Stripe only through `src/billing/client.py`.
