---
name: coding-discipline
description: Core engineering discipline for code work — keeps changes simple, scoped, maintainable, well-structured, and verified. Use before any task to write, implement, add, build, create, change, fix, debug, refactor, optimize, review, test, or organize code, scripts, configs, APIs, modules, boundaries, or file layout in any language. Load this skill first, then do the task. Skip only for trivial formatting, pure prose edits, or explicitly throwaway prototypes.
---

# Coding Discipline

## Core Authority

Use these as strong defaults. When they conflict with explicit user instructions, repo rules, security/compliance requirements, production incident constraints, or established local conventions, follow the higher-authority requirement and call out the tradeoff:

- Think before coding: surface assumptions, ambiguity, and tradeoffs before changing code.
- Simplicity first: build the smallest correct solution for present requirements — real data volume, failure cost, and contract safety — not anticipated future ones. Avoid unrequested features, abstractions, flexibility, or speculative safeguards unless risk or system contracts justify them.
- Surgical changes: touch only what the request requires; match existing style; clean up only issues caused by your change.
- Goal-driven execution: define success criteria, make them strong enough to verify independently, and loop until verified.

When these principles conflict with each other, correctness and contract safety win over simplicity and minimal diff. Call out the added scope rather than expanding silently.

Scale process to risk. On small, low-risk changes, assumptions, success criteria, and handoff notes can each be a sentence, or be skipped when self-evident. Reserve full rigor for contract-touching, multi-step, or hard-to-reverse work.

The goal is industry-grade software: clear contracts, explicit boundaries, reliable behavior, testability, and maintainable code without unnecessary machinery.

## When To Use

Applies to implementation, bug fixes, refactors, reviews, tests, code-adjacent docs, and architecture-sensitive changes. Skip it only for trivial formatting, pure prose edits, or work the user explicitly wants as a quick throwaway prototype.

Across those tasks, the same principles and repo conventions apply. What changes is the cost of acting, which sets the bar — judge the actual cost and reversibility of the specific change, not the category of task. Cost is not fixed by the activity: the same edit is expensive in a large, contract-heavy system and cheap in a small, young, or well-tested one, so a refactor toward these principles can be worth doing even mid-implementation.

The more a change costs and the harder it is to undo, the higher the bar: stay surgical, match convention by default, and propose deviations with their reason rather than imposing them. The cheaper and more reversible it is, the lower the bar: rather than silently passing code worth fixing, surface it. A lower bar to act never lowers the duty to stay in scope — make the fix only when it is in scope and explain it; otherwise surface, don't fold in.

When surfacing findings, weigh substance over taste. A divergence from the repo's own norms is a strong finding; a mere difference from your preferred style is not. Do not bury real findings in noise.

## Workflow

Use these steps whenever you are changing artifacts. When you are only reviewing, apply the same principles as evaluation criteria: assess the change against them and raise divergences as findings, weighting severity by the risk each one carries.

1. Read before coding.
   - Inspect the relevant files, tests, docs, and existing conventions.
   - For structural decisions, inspect the tree, import/dependency rules, build files, tests, and representative files in the area before choosing where code belongs.
   - Identify the behavioral surface: inputs, outputs, side effects, persistence, external calls, and user-visible contracts.
   - State assumptions when they affect implementation or risk; do not hide confusion.
   - If multiple materially different interpretations exist, present them with a clear recommendation instead of picking silently.
   - If a simpler approach exists, say so and push back when warranted.
   - If a more complex design is plausibly better for likely future needs, propose it with the tradeoff and let the user make that bet; do not build for the future unprompted.

2. Define the smallest verifiable plan.
   - Convert the request into concrete success criteria, each written as an observable check: a command to run, an expected output, or an assertion — not a vague goal. ("`GET /users/:id` returns 404 for unknown ids" beats "handle missing users".)
   - Prefer the narrowest change that satisfies those criteria without worsening system shape.
   - Ask when ambiguity would materially change the solution, create risk, or leave success criteria too weak to verify.
   - If no one is available to answer, choose the most reversible interpretation, state the assumption prominently in the handoff, and proceed.
   - For multi-step work, state each step with its verification check.

3. Preserve system shape.
   - System shape means the structure the codebase already has: follow it rather than imposing architecture.
   - Treat existing conventions as evidence and match them by default — but they are not law; when the current structure blocks the change or conflicts with these principles, propose the improvement with its reason.
   - Prefer domain or capability ownership over scattered technical-role buckets unless the repo already dictates otherwise.
   - Where the system is layered, keep responsibilities separate — boundary adapters validate and translate, core logic decides, persistence/integration code performs I/O. In small scripts or single-file programs, do not introduce layers or indirection.
   - Do not mix business rules, transport details, storage concerns, and formatting in one place unless the existing system already does so and the change is tiny.
   - Point dependencies toward stable core behavior and away from volatile edges; prefer explicit collaborators over hidden globals, ambient state, or hard-to-control side effects.
   - Avoid dependency cycles; they make separate parts change as one unit.
   - Protect public contracts: APIs, schemas, migrations, events, config, CLI flags, serialized formats, and persisted data need compatibility, rollout, and rollback care.

4. Write clear code.
   - Name by intent; make side effects visible in names.
   - Keep functions and modules focused on one purpose, using guard clauses to reduce nesting.
   - Avoid premature abstractions, wrapper layers, generic helpers, speculative safeguards, or configuration knobs until duplication, risk, contracts, or complexity prove they are needed. A request to "send one email" needs a function call, not a pluggable `NotificationProvider` interface with retry config.
   - In library or public-API code, extension points promised by the published contract are requirements, not speculation.
   - Prefer meaningful modules with small, honest interfaces over shallow pass-through wrappers.
   - Ask: "Would this look overcomplicated during review?" If yes — or if the solution is growing much larger than the problem suggests — stop and simplify.
   - Reuse official or canonical domain types and APIs when available; do not invent local aliases that drift from the source of truth.
   - Suggest or add high-quality dependencies when they reduce complexity, risk, or maintenance burden; account for security, licensing, bundle size, compatibility, and repo fit before adopting them.

5. Handle data, errors, and concurrency deliberately.
   - Validate untrusted input at boundaries and map external shapes to a canonical model kept within each context.
   - Treat authorization, injection risks, secrets, personal data, and least-privilege access as part of the design, not as afterthoughts.
   - When changing stored data, configs, queues, or external contracts, account for old data, mixed versions, migrations, defaults, and rollback behavior.
   - Make errors actionable with enough context to diagnose, without leaking secrets or sensitive data.
   - Make production behavior observable with appropriate logs, metrics, traces, or audit events when the system would otherwise be hard to diagnose.
   - Avoid hidden concurrency and fire-and-forget work unless intentional, documented, and observable.
   - In hot paths, consider data volume, algorithmic complexity, indexing, batching, caching, and N+1 risks; measure before broad optimization.

6. Organize files conservatively.
   - Put new code where a newcomer would expect it, near the files it is read, changed, and tested with. Distance in the tree should track conceptual distance.
   - Split by reason-to-change, not line count. A long cohesive file is better than many fragments that must be held open together.
   - Treat unusual size as a prompt to look for hidden seams, not as a reason in itself. Large files often hide several reasons-to-change, so investigate before concluding one is cohesive.
   - Split only when the new unit has a real interface with leverage; avoid forwarding layers and navigation-only abstractions.
   - A new unit can be a directory of cohesive modules. Promoting `routes.ts` to `routes/` with one module per domain (`users`, `admin`) is sound when each module is a real boundary, but not when the pieces are arbitrary slices or the folder only exists to re-export them.
   - Keep types, constants, helpers, and docs near their primary consumers unless shared use justifies extraction.
   - Extract shared code only after real reuse, group it by cohesive subject and ownership, and avoid catch-all helper or utility dumping grounds.
   - Add structure only for current complexity and current variation; one implementation rarely justifies a new boundary.
   - Document or enforce only load-bearing naming, ownership, dependency, and boundary rules.

7. Test behavior at the right level, not implementation.
   - Prefer outcomes over internals: return values, persisted state, emitted events, HTTP responses, UI-visible behavior, thrown errors, or meaningful side effects. (Assert that the saved record has `status: "active"`, not that `setStatus` was called once.)
   - Cover the happy path, important edge cases, and failure paths touched by the change.
   - For unit and narrow integration tests, control true boundaries such as network, database, filesystem, clock, queues, and vendor clients with mocks, fakes, local services, or realistic test dependencies as appropriate to the repo.
   - Keep fixtures minimal and deterministic; control time, randomness, and external effects.
   - Do not weaken implementation code to satisfy an incomplete test double.

8. Document only useful intent.
   - Make code clear through names and structure first; add comments only for non-obvious why: invariants, tradeoffs, ordering, retries, idempotency, fallbacks, security constraints, or business rules.
   - Do not comment obvious syntax, trivial control flow, or unclear code that should instead be simplified.

9. Validate and finish cleanly.
   - Run the most relevant formatter, linter, typecheck, test, build, or targeted smoke check available.
   - If a full check is expensive or unavailable, run the narrowest meaningful check and state the gap.
   - Review the diff: every changed line should trace to the request or to cleanup caused by your change.
   - Keep changes reviewable: avoid unrelated churn, explain non-obvious tradeoffs, and make contract or migration effects explicit.
   - Remove unused imports, variables, functions, and branches introduced by your edit.
   - Leave unrelated pre-existing issues untouched and mention them separately when useful.
   - Summarize the handoff for the user: which success criteria passed, what changed and why, assumptions made, what was intentionally left out, and what remains unverified or risky.

## Gotchas

- Do not equate "more robust" with more code. Unrequested fallbacks, retries, abstractions, and options often make systems worse.
- Do not use minimality to omit what present requirements demand: validation, error handling, and rollback care are part of correct, not extras.
- Do not refactor or restyle adjacent code just because you noticed it.
- Do not hide uncertain requirements inside implementation choices.
- Do not delete pre-existing dead code unless the user asked for that cleanup.
- Do not split a file just because it is long, create catch-all helper modules, invert dependency direction, or add layers/interfaces/seams for a single implementation.
- Do not make tests assert incidental counts, logs, ordering, timing, or payload shape unless those details are the contract.
- Do not log secrets, credentials, tokens, private keys, personal data, or full sensitive payloads.
