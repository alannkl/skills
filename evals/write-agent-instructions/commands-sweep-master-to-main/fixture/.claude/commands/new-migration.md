---
description: Generate a reversible migration
argument-hint: <MigrationName> <what it should do>
---

1. `bin/rails generate migration $ARGUMENTS`
2. Fill in `change` so it is reversible; use `up`/`down` only when `change` can't express it.
3. Run `bin/rails db:migrate && bin/rails db:rollback && bin/rails db:migrate` to prove the round trip.
