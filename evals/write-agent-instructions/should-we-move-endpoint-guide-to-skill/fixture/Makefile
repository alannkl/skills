.PHONY: test lint generate run migration migrate-up migrate-down

test:
	go test ./...

lint:
	golangci-lint run

generate:
	sqlc generate
	oapi-codegen -config api/oapi-codegen.yaml api/openapi.yaml

run:
	go run ./cmd/server
