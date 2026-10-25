.PHONY: db-up db-down test test-integration lint

db-up:
	docker compose up -d warehouse
	./scripts/wait-for-pg.sh localhost 5433

db-down:
	docker compose down

test:
	pytest tests/unit

test-integration:
	WAREHOUSE_URL=postgresql://ledger:ledger@localhost:5433/ledger pytest tests/integration

lint:
	ruff check .
	mypy ledgerflow
