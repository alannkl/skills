# ADR 007: Repositories for data access

Status: accepted, 2026-09-14

Route handlers no longer call `src/db/raw.js` directly. Each table gets a repository in `src/repos/` that owns its SQL and returns plain objects with camelCase fields. Existing handlers migrate when they are next reworked; new code uses repositories from the start.
