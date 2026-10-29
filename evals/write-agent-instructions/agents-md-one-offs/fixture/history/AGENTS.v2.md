# AGENTS.md

- Use `uv run` for every Python command; never `pip install` into the system interpreter.
- Run `make check` (ruff and pytest) before you commit.
- New endpoints go in `app/api/v2/`; `app/api/v1/` is frozen for the mobile app's old clients.
- Use the fixtures in `tests/conftest.py`; don't add new database fixtures.
- The `legacy/` importer is being deleted this sprint, so don't bother fixing its tests.
- Note from the invoices session: don't "clean up" the rounding in `app/billing/proration.py`. It rounds each line item half-up on purpose.
- When I say "ship it", run `make release-dry` and show me the output before `make release`.
- Prefer f-strings over `.format()`.
- Sort imports.
- Remember: `make check` before committing!
- Use type hints.
- Never paste the Stripe keys into code or chat; the test key is in 1Password under "Stripe test".
