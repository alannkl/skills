.PHONY: check release-dry release db-local

check:
	uv run ruff check . && uv run pytest

release-dry:
	uv run python -m scripts.release --dry-run

release:
	uv run python -m scripts.release

db-local:
	docker compose up -d db
