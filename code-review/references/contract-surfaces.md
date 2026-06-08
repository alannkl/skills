# Contract Surfaces Review Overlay

Use this overlay when a change affects APIs, config, CLI flags, schemas, migrations, events, persisted records, serialized formats, SDKs, public types, or external integration behavior.

## Review Focus

- Contract ownership: identify which callers, clients, services, jobs, users, or external systems depend on the changed surface.
- Compatibility: check backward compatibility, forward compatibility, mixed-version deployments, default values, optional versus required fields, enum expansion, and behavior when old clients meet new servers or new clients meet old servers.
- Rollout and rollback: verify migration order, feature flags, dual-read/write needs, reversibility, and behavior after partial deployment or failed deployment.
- Schema and data shape: check nullability, validation, coercion, field renames, removed fields, precision loss, time zones, ordering, pagination, and stable identifiers.
- Error contracts: check status codes, error names, response bodies, CLI exit codes, retryability, and whether callers can distinguish expected from exceptional failures.
- Documentation and generated artifacts: check that source definitions, generated clients, docs, examples, and lockfiles are updated together when they are part of the contract.
- Tests: prefer contract tests, migration tests, old-data tests, client/server skew tests, and integration tests over implementation-only unit tests.

## Common Findings

- A field becomes required without a default or migration path for existing callers.
- An enum, status, or event type changes without checking downstream consumers.
- A migration assumes all application nodes deploy simultaneously.
- A CLI or API error shape changes in a way existing automation cannot parse.

Treat contract breakage as more severe than local implementation defects when it affects external users, persisted data, or rollout safety.
