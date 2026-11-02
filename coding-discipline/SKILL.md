---
name: coding-discipline
description: Core engineering discipline for code work — keeps changes simple, scoped, maintainable, well-structured, and verified. Use before any task to write, implement, add, build, create, change, fix, debug, refactor, optimize, review, test, or organize code, scripts, configs, APIs, modules, boundaries, or file layout in any language. Load this skill first, then do the task. Skip only for trivial formatting, pure prose edits, or explicitly throwaway prototypes.
---

# Coding Discipline

## Core authority

These are strong defaults. When they conflict with explicit user instructions, repo rules, security/compliance requirements, production incident constraints, or established local conventions, follow that requirement (user instructions outrank conventions) and call out the tradeoff:

- Think before coding: surface assumptions, ambiguity, and tradeoffs first.
- Simplicity first: the smallest correct solution for present requirements — real data volume, failure cost, contract safety — not anticipated ones, with no speculative machinery: features, abstractions, safeguards, or knobs no present requirement demands. Elegance is economy.
- Surgical changes: touch only what the request requires; match existing style; clean up only issues your change caused.
- Contribute judgment: propose materially better approaches, framings, or designs with a clear recommendation; withholding a better idea fails as badly as overbuilding. Gate acting unilaterally, never proposing.
- Goal-driven execution: define success criteria strong enough to verify independently, and loop until verified.

When these principles conflict, correctness and contract safety beat simplicity and minimal diff, and the clean design beats a shortcut that leaves the wrong shape (a workaround, reliance on undocumented behavior, or something the next change must undo); state its cost against the shortcut, and call out the added scope rather than expanding silently.

Scale process to risk: the bar tracks the change's actual cost and reversibility, not its category. On small, low-risk changes, assumptions, success criteria, and handoff notes can each be a sentence, or skipped when self-evident; reserve full rigor for contract-touching, multi-step, or hard-to-reverse work.

## Workflow

Follow these steps when changing artifacts; for reviews, use these principles as criteria and weight findings by risk.

1. Read before coding: files, tests, docs, conventions.
   - Before choosing where code belongs, inspect the tree, import/dependency rules, build files, tests, and representative files in the area.
   - Manifests, lockfiles, and CI config outrank docs; flag any doc they contradict.
   - Identify the behavioral surface: inputs, outputs, side effects, persistence, external calls, and user-visible contracts.
   - State assumptions that affect implementation or risk; don't hide confusion.
   - When the request prescribes a mechanism ("add a retry loop here"), contradicts the code, or names only a symptom, restate the goal it serves before planning, and recommend what serves it better.
   - Present materially different interpretations with a recommendation instead of picking silently.
   - Present a materially simpler or more capable design with its tradeoff and a recommendation; build it only if the user takes the bet.
   - When a failure present requirements don't cover would be costly, offer a safeguard (shadow phases, guard bands, fallback tiers) as a separate option the user can decline, quantifying its downside where evidence allows.
   - For a bug fix, treat the report as a symptom: trace the callers of the code you touch and fix the shared cause once, not just the reported path — the smallest change in the wrong place is a second bug.
   - When the cause isn't evident, apply `references/diagnosing-bugs.md` before fixing.

2. Define the smallest verifiable plan.
   - Write success criteria as observable checks — a command, an expected output, or an assertion — not vague goals ("`GET /users/:id` returns 404 for unknown ids", not "handle missing users").
   - For new or changed behavior, reproducible regressions, test work, or reviews of test adequacy, apply `references/behavior-first-testing.md` before implementation or executable test bodies.
   - For a refactor, first pin current behavior with passing tests, adding any needed; restructure, then rerun them with inputs and expected outcomes unchanged, adjusting only test wiring.
   - Stay surgical: the narrowest change that satisfies the criteria without worsening system shape.
   - Ask when ambiguity would materially change the solution, create risk, or leave criteria too weak to verify. If no one can answer, take the most reversible interpretation, state the assumption prominently in the handoff, and proceed.
   - When discovery mid-implementation contradicts the agreed plan, take the most reversible option that honors its intent, record the deviation in a notes file (preferred over commit messages or PR descriptions; the handoff summary is not a record), and surface it in the handoff. If it invalidates the plan's premise, stop and re-plan.
   - For multi-step work, state each step's verification check and run it before the next step. In a sweep, verify each independent edit as it lands, never all at the end; edits that only work together, such as a rename across files, are one step, verified once complete. When a slow run (a full or real-model suite) surfaces several issues, let it finish, verify each fix with the fastest check that covers it, then rerun the slow run once.

3. Preserve system shape.
   - Treat existing structure and conventions — the system shape — as evidence of taste, not proof: match them by default; when the user's word or recent work moves away from a pattern, extend the destination, not the legacy majority; when the structure blocks the change or conflicts with these principles, propose the improvement with its reason.
   - Prefer domain or capability ownership over scattered technical-role buckets unless the repo dictates otherwise.
   - Where the system is layered, keep responsibilities separate — boundary adapters validate and translate, core logic decides, persistence or integration code performs I/O — unless it already mixes them and the change is tiny. Add no layers or indirection to small scripts or single-file programs.
   - Point dependencies toward stable core behavior and away from volatile edges; prefer explicit collaborators over hidden globals, ambient state, or hard-to-control side effects.
   - Avoid dependency cycles; they make separate parts change as one unit.
   - Protect public contracts: APIs, schemas, migrations, events, config, CLI flags, serialized formats, and persisted data need compatibility, rollout, and rollback care.

4. Write clear code.
   - The best code is the code never written. Before adding code, stop at the first rung that holds: does it need to exist (YAGNI); does the repo provide it; the standard library or platform; an installed dependency. Only then write the minimum that works. Smaller never means flimsier: between equally small options, take the edge-case-correct one.
   - Name by intent; make side effects visible in names.
   - Keep functions and modules focused on one purpose, with guard clauses to reduce nesting.
   - Give each decision (a rule, threshold, or mapping) one home; derive the rest from it.
   - Add no speculative machinery until duplication, risk, contracts, or complexity prove it needed: "send one email" needs a function call, not a pluggable `NotificationProvider` interface with retry config.
   - In library or public-API code, extension points the published contract promises are requirements, not speculation.
   - Prefer meaningful modules with small, honest interfaces over shallow pass-through wrappers.
   - If the solution would look overcomplicated in review or grows much larger than the problem suggests, stop and simplify.
   - Zoom out on friction, not just failure: a third special case on one mechanism, a growing if/else chain, a second boolean that must stay in sync with the first, a fix that needs its own fix, or working around the existing design rather than with it signals a wrong path even while each step succeeds. Restate the problem one level up — the outcome the code serves, not the mechanism — and look for a simpler path; often a structure (a state machine, lookup table, or discriminated union) replaces the branch pile. Staying the course is then a stated decision, not a default.
   - In typed languages, make illegal states unrepresentable where partiality appears (`completed: boolean` beside an optional `completedAt` invites impossible combinations), and never lie to the type system with casts or silencing escapes; strengthen a type only where partiality shows, then stop.
   - Reuse official or canonical domain types and APIs; don't invent local aliases that drift from the source of truth.
   - Suggest or add high-quality dependencies that reduce complexity, risk, or maintenance burden, after weighing security, licensing, bundle size, compatibility, and repo fit.

5. Handle data, errors, and concurrency deliberately.
   - Validate untrusted input at boundaries and map external shapes to a canonical model within each context. Past a validated boundary, trust the types: no re-validation deep in call chains. High-stakes invariants (money, authorization) can still earn internal assertions.
   - Treat authorization, injection risks, secrets, personal data, and least-privilege access as part of the design, not as afterthoughts.
   - When changing stored data, configs, queues, or external contracts, account for old data, mixed versions, migrations, defaults, and rollback.
   - Make errors actionable, with enough context to diagnose.
   - Never log or commit secrets, credentials, tokens, private keys, or full sensitive payloads, and never commit personal data; log personal data only when a stated requirement, such as an audit trail, needs it, and only the fields it needs.
   - Make production behavior observable with logs, metrics, traces, or audit events where it would otherwise be hard to diagnose.
   - Avoid hidden concurrency and fire-and-forget work unless intentional, documented, and observable.
   - In hot paths, consider data volume, algorithmic complexity, indexing, batching, caching, and N+1 risks; measure before broad optimization.

6. Organize files conservatively.
   - Put new code where a newcomer would expect it, near the code and tests read and changed with it; tree distance should track conceptual distance.
   - Split by reason-to-change, not line count: unusual size prompts a look for hidden seams, not a split; a long cohesive file beats fragments that must be understood together.
   - Split only when the new unit has a real interface with leverage; no forwarding layers or navigation-only abstractions.
   - A new unit can be a directory of cohesive modules: promoting `routes.ts` to `routes/` with one module per domain (`users`, `admin`) is sound when each module is a real boundary, not when the pieces are arbitrary slices or the folder only re-exports them.
   - Keep types, constants, helpers, and docs near their primary consumers unless shared use justifies extraction.
   - Extract shared code only after real reuse, grouped by cohesive subject and ownership; no catch-all helper or utility dumping grounds.
   - Document or enforce only load-bearing naming, ownership, dependency, and boundary rules.

7. Document only useful intent.
   - Make code clear through names and structure first. Document public interfaces as the repo's conventions expect; otherwise comment only non-obvious why: invariants, tradeoffs, ordering, retries, idempotency, fallbacks, security constraints, or business rules.
   - When you deliberately choose a simpler implementation with a known ceiling (a coarse lock, an O(n²) scan, a naive heuristic), comment the ceiling and the condition that would justify upgrading, so the shortcut reads as a decision, not an oversight.
   - Don't comment obvious syntax or trivial control flow; simplify unclear code instead of commenting it.

8. Validate and finish cleanly.
   - Run the most relevant formatter, linter, typecheck, test, build, or targeted smoke check; if a full check is expensive or unavailable, run the narrowest meaningful one and state the gap.
   - In every check — automated, manual, or against a real model — fast-forward time you control (inject a clock, age timestamps, set short horizons) and wait only the minimum the check needs. When elapsed time is the evidence (a soak, a latency measurement) or outside your control (an external system's window), bound the wait and state what a compressed check could not prove. Treat runtime as a cost: aim for a single test in seconds and the full suite in minutes.
   - For a risky change, name each fact its safety hinges on and verify it by running code, not by argument — a written justification reads as convincing whether or not it is true. Check impact where symbol search stops: serialized data, wire formats, readers in other languages, feature flags. Record a search that finds nothing.
   - Review the diff: every changed line traces to the request or to cleanup your change caused.
   - Keep changes reviewable: no unrelated churn; explain non-obvious tradeoffs; make contract and migration effects explicit.
   - Remove unused imports, variables, functions, and branches your edit introduced.
   - Before deleting code, files, Git branches, or worktrees, confirm they are no longer needed; keep pre-existing uncommitted work and unmerged commits unless their removal is authorized.
   - Leave unrelated pre-existing issues untouched; mention them separately when useful.
   - Weigh findings by substance, not taste: a divergence from the repo's own norms is a strong finding; a difference from your preferred style is not.
   - Confirm every scaffolded scenario has an executable test body or a documented reason to stay skipped.
   - When offering to commit, include the proposed commit message so one approval covers both.
   - Write the handoff for the engineer who will maintain the code: what now behaves differently for callers, operators, or stored data, and, for consequential changes, the mechanism and the invariant future edits must preserve.
   - State which success criteria passed and what the checks did not establish; a passing test covers only the behavior it exercised. Include assumptions, plan deviations, skipped tests or revised scaffold outcomes with reasons, intentional exclusions, and any real pending action.
   - Scale the handoff to the consequences: a rename gets one sentence, a changed transaction boundary a causal explanation; even one sentence names the behavior and what was checked.
