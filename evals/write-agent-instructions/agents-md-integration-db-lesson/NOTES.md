# agents-md-integration-db-lesson

**Family:** 4 (add a lesson to AGENTS.md, arriving conversationally). **Harness:** Codex, AGENTS.md. **Restraint:** small edit.

**User:** data engineer on a small team running a Python/Airflow ETL. Codex spent a while chasing integration-test failures that were only connection errors because the dockerised Postgres was down.

**Why realistic:** "not your change, the DB was down, write that down" is a common end-of-session note. AGENTS.md already half-says it ("Integration tests need a database.") without saying how, which is how real files drift.

**Good result:** the existing Testing line becomes something like "Integration tests need the local Postgres: run `make db-up` first (then `make test-integration`)." A concise prerequisite added right next to the existing line is equally fine. A line or two; only AGENTS.md changes.

**Plausible bad results:** a full restatement of the requirement elsewhere in the file, leaving it stated twice; an overgeneralized claim such as "connection errors always mean the DB is down"; a long troubleshooting essay; recording the "9 failures" anecdote; fixing the unrelated defect in `normalize_amounts` (it mutates its input, violating the Conventions section) or the stale README.

**Judgment calls:** a symptom hint (e.g. "connection refused here usually means the DB isn't up") is welcome but not required; "run `make db-up` first" alone prevents the wasted debugging. Absolute claims that every connection error means the DB is down fail. Either `make test-integration` or pytest is accepted as the run command, and the guidance need not say to restart an already-running DB.
