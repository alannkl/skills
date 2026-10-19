# Agent instructions

- Never push directly to main; open a pull request.
- Run `make test` before opening a pull request.
- Commit messages use Conventional Commits (`feat:`, `fix:`); the release bot parses the prefixes.

## Billing

- Amounts are integers in cents; never use floats for money.
- Every change to `src/billing/` needs a migration note in `docs/billing-changes.md`, newest entry first.
- Refund logic lives in `src/billing/refunds.py`; refunds over 500.00 require the `manual_review` flag set to `True`.
- Currency codes are ISO 4217 uppercase strings; reject anything else with `InvalidCurrency`.
- Never log full card numbers; log only the last four digits.

## API

- Public endpoints are versioned under `/v2/`; never change a `/v1/` response shape.
- Every new endpoint needs an OpenAPI entry in `docs/openapi.yaml`.
