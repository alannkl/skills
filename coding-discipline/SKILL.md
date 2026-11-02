---
name: coding-discipline
description: Core engineering discipline for code work — keeps changes simple, scoped, maintainable, well-structured, and verified. Use before any task to write, implement, add, build, create, change, fix, debug, refactor, optimize, review, test, or organize code, scripts, configs, APIs, modules, boundaries, or file layout in any language. Load this skill first, then do the task. Skip only for trivial formatting, pure prose edits, or explicitly throwaway prototypes.
---

# Coding Discipline

## Core authority

These are strong defaults. Explicit user instructions, repo rules, security or compliance requirements, incident constraints, and local conventions override them (user instructions outrank conventions); call out the tradeoff.

- Think before coding: surface assumptions, ambiguity, and tradeoffs.
- Simplicity: the smallest correct solution for present requirements (real data volume, failure cost, contract safety), with no speculative features, abstractions, safeguards, or knobs.
- Surgical changes: touch only what the request requires; match existing style; clean up only issues your change caused.
- Contribute judgment: propose materially better approaches with a recommendation; withholding one fails as badly as overbuilding. Gate acting, never proposing.
- Goal-driven: define success criteria verifiable independently, and loop until verified.

Correctness and contract safety beat simplicity and minimal diff. A clean design beats a shortcut that leaves the wrong shape (a workaround, undocumented behavior, something the next change must undo); state its cost and call out the added scope.

Scale process to the change's cost and reversibility, not its category: on small low-risk changes, assumptions, criteria, and handoff take a sentence each, or nothing when self-evident.

## Workflow

Follow these steps when changing artifacts. For reviews, use them as criteria, weight findings by risk, and judge substance, not taste: divergence from the repo's norms is a strong finding; from your preferred style is not.

1. Read before coding.
   - Read the relevant files, tests, docs, tree, import rules, build files, and representative code in the area.
   - Manifests, lockfiles, and CI config outrank docs; flag docs they contradict.
   - Identify the behavioral surface: inputs, outputs, side effects, persistence, external calls, user-visible contracts.
   - When a request prescribes a mechanism, contradicts the code, or names only a symptom, restate the goal and recommend what serves it better.
   - Present materially different interpretations, or a materially simpler or more capable design, with its tradeoff and a recommendation; build an alternative only if the user takes it.
   - Offer a safeguard against a costly failure present requirements don't cover (shadow phases, guard bands, fallback tiers) as a declinable option, quantifying its downside where evidence allows.
   - For a bug, trace the callers of the code you touch and fix the shared cause once; the smallest change in the wrong place is a second bug. When the cause isn't evident, apply `references/diagnosing-bugs.md` first.

2. Plan the smallest verifiable change.
   - Write success criteria as observable checks ("`GET /users/:id` returns 404 for unknown ids", not "handle missing users").
   - For new or changed behavior, reproducible regressions, test work, or test-adequacy reviews, apply `references/behavior-first-testing.md` before implementation or executable test bodies.
   - For a refactor, pin current behavior with passing tests, adding any needed; restructure; rerun with inputs and expected outcomes unchanged, adjusting only wiring.
   - Ask when ambiguity would materially change the solution, add risk, or leave criteria unverifiable. With no one to answer, take the most reversible interpretation, state it prominently in the handoff, and proceed.
   - When discovery contradicts the agreed plan, take the most reversible option that honors its intent, record the deviation in a notes file (not only in commit messages, PR descriptions, or the handoff), and surface it in the handoff. If it breaks the plan's premise, stop and re-plan.
   - For multi-step work, state each step's verification check and run it before the next. In a sweep, verify each independent edit as it lands; edits that only work together, such as a cross-file rename, are one step. When a slow run surfaces several issues, let it finish, verify each fix with the fastest covering check, then rerun once.

3. Preserve system shape.
   - Match existing structure and conventions by default, as evidence of taste, not proof. When the user or recent work moves away from a pattern, extend the new direction; when the structure blocks the change or conflicts with these principles, propose the improvement.
   - Prefer domain or capability ownership over technical-role buckets unless the repo dictates otherwise.
   - In layered systems, boundaries validate and translate, core logic decides, persistence and integration code does I/O, unless the code already mixes them and the change is tiny. Add no layers or indirection to small scripts or single-file programs.
   - Point dependencies toward stable core behavior; prefer explicit collaborators over hidden globals, ambient state, and hard-to-control side effects; avoid dependency cycles.
   - Protect public contracts (APIs, schemas, migrations, events, queues, config, CLI flags, serialized formats, persisted data): account for old data, mixed versions, defaults, rollout, and rollback.

4. Write clear code.
   - Before adding code, stop at the first rung that holds: not needed (YAGNI); the repo provides it; the standard library or platform; an installed dependency; then the minimum that works. Between equally small options, take the edge-case-correct one.
   - Name by intent; make side effects visible in names.
   - Keep functions and modules to one purpose; use guard clauses over nesting.
   - Give each decision (rule, threshold, mapping) one home; derive the rest from it.
   - Extension points a library's published contract promises are requirements, not speculation.
   - Prefer modules with small, honest interfaces over pass-through wrappers.
   - Zoom out on friction, not just failure: a third special case, a growing if/else chain, a second boolean synced with the first, a fix needing its own fix, working around the design, or a solution much larger than the problem. Restate the problem one level up and look for a simpler path, often a structure (state machine, lookup table, discriminated union). Continuing is then a stated decision.
   - In typed languages, make illegal states unrepresentable where partiality appears (`completed: boolean` beside optional `completedAt`), then stop; never lie to the type checker with casts or silencing escapes.
   - Reuse canonical domain types and APIs instead of local aliases.
   - Suggest dependencies that reduce complexity, risk, or maintenance, after weighing security, licensing, size, compatibility, and repo fit.

5. Handle data, errors, and concurrency deliberately.
   - Validate untrusted input at boundaries and map external shapes to a canonical model per context. Past that, trust the types: no re-validation deep in call chains, except assertions for high-stakes invariants (money, authorization).
   - Design for authorization, injection risks, secrets, personal data, and least privilege from the start.
   - Make errors actionable, with context to diagnose.
   - Never log or commit secrets, credentials, tokens, private keys, or full sensitive payloads, or commit personal data; log personal data only when a stated requirement (an audit trail) needs it, and only the fields it needs.
   - Make hard-to-diagnose production behavior observable with logs, metrics, traces, or audit events.
   - No hidden concurrency or fire-and-forget work unless intentional, documented, and observable.
   - In hot paths, weigh data volume, complexity, indexing, batching, caching, and N+1 risk; measure before broad optimization.

6. Organize files conservatively.
   - Put code where a newcomer expects it, near what is read and changed with it.
   - Split by reason to change, not line count; a long cohesive file beats fragments that must be read together. Split only into units with a real interface, never forwarding layers or re-export folders: promoting `routes.ts` to `routes/` with one module per domain works only when each module is a real boundary.
   - Keep types, constants, helpers, and docs near their main consumers. Extract shared code only after real reuse, grouped by subject and owner; no catch-all utils.
   - Document or enforce only load-bearing naming, ownership, dependency, and boundary rules.

7. Document only useful intent.
   - Clarify through names and structure first; simplify unclear code rather than commenting it. Document public interfaces per repo convention; otherwise comment only the non-obvious why: invariants, tradeoffs, ordering, retries, idempotency, fallbacks, security constraints, business rules.
   - For a deliberately simple implementation with a known ceiling (a coarse lock, an O(n²) scan), comment the ceiling and what would justify upgrading.

8. Validate and finish.
   - Run the most relevant formatter, linter, typecheck, tests, build, or smoke check; if that is expensive or unavailable, run the narrowest meaningful one and state the gap.
   - In every check, including manual and real-model ones, fast-forward time you control (inject a clock, age timestamps, set short horizons) and wait only the minimum. When elapsed time is the evidence or outside your control, bound the wait and state what a compressed check could not prove. Aim for seconds per test, minutes per suite.
   - For a risky change, verify each fact its safety hinges on by running code, not by argument; a written justification convinces whether or not it is true. Check impact past symbol search: serialized data, wire formats, readers in other languages, feature flags. Record searches that find nothing.
   - Review the diff: every line traces to the request or to cleanup your change caused. Remove unused code your edit introduced; mention unrelated pre-existing issues separately when useful instead of fixing them.
   - Before deleting code, files, Git branches, or worktrees, confirm they are unneeded; keep pre-existing uncommitted work and unmerged commits unless their removal is authorized.
   - When offering to commit, include the proposed message.
   - Write the handoff for the maintaining engineer, scaled to consequence (a rename: one sentence naming the behavior and the check; a changed transaction boundary: the mechanism and the invariant to preserve). Cover what changed for callers, operators, or stored data; non-obvious tradeoffs; which criteria passed and what the checks did not establish; assumptions, plan deviations, skipped tests or revised scaffold outcomes with reasons, exclusions, and real pending actions.
