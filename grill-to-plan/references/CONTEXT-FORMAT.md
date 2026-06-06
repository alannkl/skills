# CONTEXT.md Format

Use `CONTEXT.md` as a glossary for domain language only.

## Location

- Single-context repo: create or update `/CONTEXT.md`.
- Multi-context repo: if `/CONTEXT-MAP.md` exists, use it to find the relevant context and update that context's `CONTEXT.md`.
- Create the file lazily, only when the first domain term is resolved.
- If multiple contexts exist and the right one is unclear, ask before writing.

## Shape

```md
# {Context Name}

{One or two sentences describing what this domain context is.}

## Language

**Canonical Term**: One or two sentences defining what the concept is.
_Avoid_: AmbiguousTerm, LegacyTerm

**Another Term**: A tight definition of the project-specific concept.
```

## Rules

- Include only project-specific domain concepts, not general programming terms.
- Define what the term is, not implementation behavior.
- Prefer one canonical term and list rejected synonyms under `_Avoid_`.
- Group terms under subheadings only when natural clusters emerge.
- Do not store requirements, implementation decisions, roadmap notes, or open questions here.

## Context Map Shape

Use this shape when a repo has multiple contexts:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments

## Relationships

- **Ordering -> Billing**: Ordering emits `OrderPlaced`; Billing consumes it to generate invoices.
```

Root `docs/adr/` can hold system-wide decisions. Context-specific ADRs can live beside the relevant context when the repo already follows that pattern.
