# AGENTS.md

`fleetapi` — REST API for the Fleetwise vehicle-tracking app. Go 1.23, chi router, Postgres via sqlc.

## Commands
- `make test` — unit tests (`go test ./...`)
- `make lint` — golangci-lint
- `make generate` — regenerates sqlc queries and the OpenAPI server stubs
- `make run` — runs the server on :8080 against the local db

## Layout
- `cmd/server/` — main
- `internal/http/` — router (`routes.go`) and handlers
- `internal/httpx/` — shared HTTP helpers (errors, JSON, pagination)
- `internal/store/` — sqlc-generated queries (don't edit `*.sql.go` by hand)
- `api/openapi.yaml` — the API contract; source of truth for request/response shapes

## Conventions
- Errors: wrap with `fmt.Errorf("...: %w", err)`; don't log and return.
- Pass `ctx` through everything; no `context.Background()` outside `main`.
- Don't add dependencies without asking.

## Adding an endpoint

1. Add the path and operation to `api/openapi.yaml` first. Request and response bodies go under `components/schemas`; reuse `Error` and `Page` instead of defining new ones.
2. Run `make generate`. This updates `internal/http/gen/server.gen.go`; your handler has to satisfy the generated interface.
3. Write the handler in `internal/http/handlers/<resource>.go`. One file per resource.
4. Handlers must:
   - return errors with `httpx.WriteError(w, r, err)`, which maps `store.ErrNotFound` to 404 and validation errors to 422. Never call `http.Error` directly.
   - decode JSON with `httpx.DecodeJSON`, which enforces the 1 MB body limit and rejects unknown fields.
   - get the caller from `auth.FromContext(r.Context())`, never from headers.
5. If the endpoint lists things, use `httpx.ParsePage(r)` and return a `Page`; max page size is 100.
6. Register the route in `internal/http/routes.go` under the right `r.Group` (authenticated vs public). Admin-only routes go under the `RequireRole("admin")` group.
7. If it needs new queries, add them to `internal/store/queries/<resource>.sql` and run `make generate` again.
8. Add a table-driven test in `internal/http/handlers/<resource>_test.go` using `testutil.NewServer(t)`; cover the happy path, 404, and one validation error at minimum.
9. Add a line to `CHANGELOG.md` under "Unreleased".
10. `make lint test` before you're done.
