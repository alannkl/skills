---
name: db-migrate
description: "Write and run Postgres schema migrations for the orders service. Use when adding, changing or removing tables, columns, indexes or constraints, when backfilling data into a changed column, or when rolling back a migration."
---

# Database migrations

Migrations live in `db/migrations/` and run with `migrate` (golang-migrate). Every change to the schema goes through a migration; never edit the database by hand.

## Writing a migration

1. Create the pair of files with `make migration name=<snake_case_description>`. It writes `db/migrations/<timestamp>_<name>.up.sql` and `.down.sql`.
2. Write the `up` file. Keep one logical change per migration.
3. Write the `down` file so it fully reverses `up`. If a change cannot be reversed, such as dropping a column with data, say so in a comment at the top of `down.sql` and stop to ask the user before continuing.
4. Wrap DDL in a transaction unless it uses `CREATE INDEX CONCURRENTLY`, which cannot run inside one.
5. Run `make migrate-check`. It applies `up`, `down`, then `up` again against a throwaway database and fails on any error.
6. Run `make test` to make sure the repository layer still compiles against the new schema.

## Naming and style

- Table names are plural snake_case (`order_items`); column names are singular snake_case.
- Every table has `id bigint generated always as identity primary key`, `created_at timestamptz not null default now()` and `updated_at timestamptz not null default now()`.
- Foreign keys are named `fk_<table>_<column>` and indexes `idx_<table>_<columns>`.
- Money is `numeric(12,2)`, never `float`.
- Use `text` instead of `varchar(n)` unless a length limit is a business rule.
- Enum-like columns use a `check` constraint, not a Postgres enum type, so values can be added without a migration lock.

## Adding columns

- A new column on an existing table must be nullable or have a constant default. A volatile default (such as `now()` on an existing table) rewrites the table and locks it.
- Add `not null` in a later migration, after the backfill, using `alter table ... add constraint ... check (col is not null) not valid` followed by `validate constraint`.
- Never rename a column in one step. Add the new column, dual-write from the application, backfill, switch reads, then drop the old column in a later release.

## Indexes

- Create indexes on tables over 100k rows with `CREATE INDEX CONCURRENTLY` in a migration of its own, outside a transaction (start the file with `-- migrate:no-transaction`).
- Drop indexes with `DROP INDEX CONCURRENTLY`.
- Name the columns in the order the queries filter on them.

## Constraints

- Add foreign keys as `not valid`, then `validate constraint` in a second statement so the validation does not hold a lock on both tables.
- Unique constraints on large tables: build a unique index concurrently first, then `add constraint ... unique using index`.

## Backfilling large tables

Use this only when a migration needs existing rows filled in, such as a new column derived from others, and the table has more than 100k rows. Smaller tables can be backfilled with a single `update` inside the migration.

1. Do not backfill inside the schema migration. Write the backfill as a Go job in `cmd/backfill/<name>/main.go` using the template in `cmd/backfill/_template`.
2. Process rows in batches of 5,000 ordered by `id`, keeping the last processed `id` in the `backfill_progress` table so the job can resume after a crash.
3. Sleep 200 ms between batches. During business hours (08:00 to 20:00 UTC), sleep 1 s instead.
4. Each batch runs in its own transaction with `set local statement_timeout = '5s'`.
5. Make the job idempotent: the update must skip rows already backfilled, for example `where new_col is null`.
6. Run it first against staging with `go run ./cmd/backfill/<name> -env staging -dry-run`, which prints the number of rows it would touch and the first and last `id`.
7. Then run against staging without `-dry-run` and compare the row count with the dry run.
8. Production backfills are started by the on-call engineer, not by an agent. Write the exact command in the PR description under a "Backfill" heading, with the expected row count and duration estimate (rows divided by 5,000, times the sleep, plus about 50 ms per batch).
9. Watch replication lag on the `orders-replica` dashboard while it runs; if lag passes 30 s, the job pauses on its own and resumes when lag drops under 5 s.
10. After the backfill finishes, the `not null` constraint migration can ship.

Backfill jobs must not:

- call external services;
- update `updated_at` (set it explicitly to its current value so the trigger does not bump it);
- hold locks across batches.

If a backfill touches the `payments` table, also get a review from someone on the payments team before merging.

## Rolling back a migration

Use this only when a deployed migration has to be undone.

1. Check whether the application release that depends on the migration has been rolled back first. A schema rollback under an application that still uses the new schema causes errors; roll back the application first.
2. Find the migration version with `migrate -path db/migrations -database "$DATABASE_URL" version`.
3. In staging, run `make migrate-down steps=1` and confirm with `make migrate-status` that the version went back by one.
4. Run the application's smoke tests against staging: `make smoke env=staging`.
5. Production rollbacks need the on-call engineer. Give them the version, the exact `migrate down 1` command, and whether `down.sql` loses data.
6. If `down.sql` drops a column or table that has received writes since the deploy, take a snapshot first: `make snapshot table=<name>` writes a copy to the `rollback_snapshots` schema.
7. After the rollback, open an incident note in `docs/incidents/` with the date, the version, why it was rolled back, and whether any data was lost.
8. If the migration was half-applied (the `schema_migrations` row says `dirty = true`), do not run `down`. Fix the state by hand with `migrate force <previous_version>` only after checking which statements of `up` actually ran, and ask the user before forcing.

## Reviewing a migration PR

- The PR description names the migration files and says whether `down` is lossless.
- Large-table changes say how many rows the table has in production (from `docs/table-sizes.md`, refreshed weekly).
- Any lock-taking statement on a table over 100k rows is called out explicitly.

## Final message

Tell the user which migration files you created or changed, whether `make migrate-check` and `make test` passed, and anything that needs a human: an irreversible `down`, a production backfill to schedule, or a payments-team review.
