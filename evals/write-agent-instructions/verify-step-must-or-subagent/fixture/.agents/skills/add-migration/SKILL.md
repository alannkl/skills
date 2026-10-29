---
name: add-migration
description: "Adds a PostgreSQL schema migration to the orders API. Use when a change needs a new table, column, index, or constraint, or the user asks for a migration."
---

# Add migration

1. Create the next numbered file in `migrations/`, e.g. `0043_add_order_notes.sql`, with an `-- up` section and a `-- down` section. Never edit an applied migration.
2. Write the schema change in `-- up` and its exact reverse in `-- down`. Add new columns as nullable or with a default so existing rows stay valid.
3. Apply it to the local database: `pnpm db:migrate`.
4. Verify the migration works and everything looks good.
5. Update the types in `src/db/schema.ts` to match, then run `pnpm typecheck && pnpm test`.
6. Commit the migration and the schema change together.
