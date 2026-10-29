.PHONY: dev test lint client migration migrate migrate-down rollback

dev:
	docker compose up -d db
	DATABASE_URL=postgres://ledger:ledger@localhost:5433/ledger npx tsx watch src/server.ts

test:
	npx vitest run

lint:
	npx eslint . && npx tsc --noEmit

client:
	npx openapi-typescript-codegen --input openapi.yaml --output clients/ts

migration:
	@test -n "$(name)" || (echo "usage: make migration name=<snake_case_name>" >&2; exit 2)
	npx node-pg-migrate create "$(name)" --migrations-dir db/migrations --migration-file-language sql

migrate:
	npx node-pg-migrate up --migrations-dir db/migrations

migrate-down:
	npx node-pg-migrate down --migrations-dir db/migrations

rollback:
	gh workflow run rollback-production.yml
