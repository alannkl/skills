# Ledger API

Ledger is the invoicing backend: a TypeScript (Node 22) HTTP API on Postgres 16.

## Commands

- `make dev` starts the API and a local Postgres in Docker on port 5433.
- `make test` runs unit and contract tests; `make lint` runs eslint and tsc.
- Run `make lint` and `make test` before every commit.

## Git

- Never push directly to `main`; open a pull request.
- Write commit messages in Conventional Commits format (`feat:`, `fix:`, `chore:`); release-please builds the changelog from them.
- Put the Linear issue ID (such as `LED-412`) in the PR title.
- Keep each PR to one change.

## Code style

- Write clean, readable, well-structured code.
- Use TypeScript strict mode; never use `any`, use `unknown` and narrow it.
- Prefer named exports.
- Make sure your code works before you say you are done.
- Money is integer cents (`amountCents: number`) everywhere; never use floats for money.
- Dates go over the wire as ISO 8601 strings in UTC.

## API handlers

Handlers live in `src/api/handlers/`, one file per resource.

- Every handler calls `requireAuth(req)` first, except routes listed in `PUBLIC_ROUTES` in `src/api/routes.ts`.
- Return errors with `ApiError` (`throw new ApiError(404, "invoice_not_found", "...")`); it renders the `{ "error": { "code", "message" } }` envelope clients parse. Never send a bare string or a stack trace.
- Never log request or response bodies; they carry customer PII. Log the request ID and route only.
- Validate input with the zod schema next to the handler; never trust `req.body` types.

### Adding an endpoint

1. Add the handler in `src/api/handlers/<resource>.ts`.
2. Register it in `src/api/routes.ts`.
3. Describe it in `openapi.yaml`; the contract tests read the spec.
4. Add a contract test in `tests/contract/<resource>.test.ts`.
5. Run `make client` to regenerate the TypeScript client in `clients/ts/`, and commit the result.

## Database migrations

Migrations live in `db/migrations/` as numbered SQL files (`0042_add_invoice_due_date.sql`), each with an `-- up` and a `-- down` section.

1. Create the next number with `make migration name=<snake_case_name>`; never pick the number by hand.
2. Never edit a migration that has merged to `main`; write a new one.
3. New columns on existing tables must be nullable or have a default; `invoices` has 40M rows and a NOT NULL column without a default locks it for minutes.
4. Create indexes with `CREATE INDEX CONCURRENTLY`, in a migration of its own, with `-- no-transaction` as its first line.
5. Never drop a column in the same release that stops using it: first deploy the code that no longer reads it, then drop it in a later migration.
6. Run `make migrate`, then `make migrate-down`, then `make migrate` locally to check the down section works.
7. Update `src/db/schema.ts` to match and run `make test`.
8. Backfills over 100k rows go in `scripts/backfills/`, not in a migration, in batches of 5,000 rows with a 200 ms sleep between batches.

## Releasing

Releases are cut from `main` on Tuesdays and Thursdays.

1. Check CI is green on `main`: `gh run list --branch main --limit 1`.
2. Merge the open release-please PR (titled `chore(main): release x.y.z`); it bumps the version and tags the release.
3. Wait for the `deploy-production` workflow to finish: `gh run watch`.
4. Check `https://api.ledger.example/health` returns the new version.
5. Post the changelog section to `#ledger-releases`.
6. If the health check fails, run `make rollback` and tell the on-call engineer in `#ledger-oncall`; never push a fix forward during a failed release.

## Incident hotfixes

Only when the user says production is broken:

1. Branch from the latest release tag, not `main`: `git switch -c hotfix/<issue> vX.Y.Z`.
2. Make the smallest fix; no refactors.
3. Open the PR against `main` with the `hotfix` label; CI cherry-picks it onto a release branch.
4. Ask the user before merging; a hotfix merge deploys straight to production.

## Notes

- This file was rewritten in August after the agent kept breaking the generated client.
- Please always remember to follow all of the rules above carefully.
- Be careful.
