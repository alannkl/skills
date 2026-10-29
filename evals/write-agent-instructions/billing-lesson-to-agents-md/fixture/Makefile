.PHONY: lint test stripe-fixtures

lint:
	uv run ruff check . && uv run mypy src

test:
	uv run pytest

stripe-fixtures:
	stripe fixtures tests/fixtures/stripe.json --api-key "$$STRIPE_TEST_KEY"
