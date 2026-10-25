---
name: db-migration
description: Write a Postgres schema migration for fleetapi. Use when adding or changing tables, columns, or indexes.
---

# DB migration

1. `make migration name=<snake_case_name>` creates `migrations/<timestamp>_<name>.up.sql` and `.down.sql`.
2. Every `up` needs a working `down`.
3. Index creation on existing tables uses `CREATE INDEX CONCURRENTLY` in its own migration (no transaction).
4. Run `make migrate-up && make migrate-down && make migrate-up` locally to check the round trip.
5. Update the matching queries in `internal/store/queries/` and run `make generate`.
