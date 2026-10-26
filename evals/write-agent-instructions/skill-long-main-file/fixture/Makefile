migration:
	migrate create -ext sql -dir db/migrations -seq=false $(name)

migrate-check:
	./scripts/migrate-check.sh

migrate-down:
	migrate -path db/migrations -database "$$DATABASE_URL" down $(steps)

migrate-status:
	migrate -path db/migrations -database "$$DATABASE_URL" version

snapshot:
	./scripts/snapshot.sh $(table)

smoke:
	go test ./smoke/... -env $(env)

test:
	go test ./...
