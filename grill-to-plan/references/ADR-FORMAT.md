# ADR Format

Use ADRs for durable architectural or boundary decisions that are hard to reverse, surprising without context, and based on a real trade-off.

## Location

- Default location: `docs/adr/`.
- In multi-context repos, use root `docs/adr/` for system-wide decisions and context-local `docs/adr/` when the decision belongs to one documented context.
- Use sequential files: `0001-slug.md`, `0002-slug.md`, and so on.
- Create `docs/adr/` lazily, only when the first ADR is needed.
- Create missing parent directories the first time you write an ADR.

## Shape

```md
# {Short Decision Title}

{One to three sentences explaining the context, the decision, and why it was chosen.}
```

## Optional Sections

Add these only when they clarify the decision:

```md
Status: proposed | accepted | deprecated | superseded by ADR-NNNN

## Considered Options

- {Option}: {why it was accepted or rejected}

## Consequences

- {Important downstream effect}
```

- `Status` sits directly under the title. When one ADR supersedes another, mark the old one `superseded by ADR-NNNN` rather than rewriting or deleting it.
- In `Consequences`, state trade-offs as "we accept {X} in exchange for {Y}", and name anything a future reader might mistake for an oversight.

## Staleness

ADRs outlive the code they describe: avoid file paths and code snippets, which go stale silently. Exception: inline a snippet when it encodes the decision more precisely than prose can — a state machine, schema, or type shape — trimmed to its decision-rich parts.

## Numbering

Scan `docs/adr/` for the highest existing ADR number and increment by one.

## What Qualifies

- Architectural shape, such as monorepo boundaries or event-sourced write models.
- Integration patterns between contexts, such as domain events instead of synchronous HTTP.
- Technology choices with meaningful lock-in, such as database, message bus, auth provider, or deployment target.
- Boundary and ownership decisions, such as which context owns customer data.
- Deliberate deviations from the obvious path, such as manual SQL instead of an ORM.
- Constraints not visible in code, such as compliance limits or external latency contracts.
- Rejected alternatives worth remembering because they are likely to be proposed again.
