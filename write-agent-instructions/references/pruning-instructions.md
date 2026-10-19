# Pruning instructions

Use this for a structural revision of an existing instruction artifact: removing or merging requirements, sections, or steps; reordering them; changing output formats; or moving material between always-loaded text and references. The pruning rules in step 5 of `SKILL.md` decide what may go; this reference covers the baseline, consumers, and comparison.

## Baseline

- Before editing, list the original requirements: outcomes and terminal states, explicit user preferences, constraints and permissions, necessary ordering, safeguards, output formats and section names, triggers and load conditions, and pointers.
- Keep the original text retrievable for comparison, such as through version control or a copy in a location the task permits writing. Treat uncommitted changes to the artifact as part of the baseline and carry them into the revision.

## Consumers

- Before removing or renaming anything, search for what relies on it: skills, instruction files, scripts, tests, docs, or code that load the artifact, cite its section or step names or numbers, parse its output, or depend on its trigger.
- Update each consumer in scope, or keep the contract it relies on. Report consumers outside the requested scope instead of editing them.

## Unusually specific rules

- A rule that looks oddly specific often encodes a past failure or a user preference. Before deleting one, check its origin in version history, linked issues, or with the user.
- When the origin stays unknown and the rule guards a costly failure, keep it or ask.

## Restructure

- Decide for each baseline requirement: keep, merge, move behind a pointer, inline, or remove under step 5 of `SKILL.md`. Place moved and inlined material per step 4.
- Update every pointer, step or section reference, and template that the moves or renumbering affect.

## Compare and report

- Compare the original with the pruned draft: every baseline requirement is kept, moved, merged, or intentionally removed. Then compare the pruned draft with the polished text per step 5 of `SKILL.md`.
- For each intentional removal or changed requirement, report what replaces it, if anything.
