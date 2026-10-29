# shopfront-api

Public REST API for partner integrations.

- `pnpm dev`, `pnpm test`
- `pnpm openapi:gen` writes `openapi.yaml` from the route schemas in `src/routes/`. The committed `openapi.yaml` is refreshed at release time.
- Routes without a response schema don't appear in the generated spec.
- Partner docs live in `docs/api/`, one file per spec tag. `pnpm docs:build` builds the docs site from them.
