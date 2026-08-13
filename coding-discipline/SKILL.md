---
name: coding-discipline
description: Core engineering discipline for code work — keeps changes simple, scoped, maintainable, well-structured, and verified. Use before any task to write, implement, add, build, create, change, fix, debug, refactor, optimize, review, test, or organize code, scripts, configs, APIs, modules, boundaries, or file layout in any language. Load this skill first, then do the task. Skip only for trivial formatting, pure prose edits, or explicitly throwaway prototypes.
---

# Coding Discipline

## Core Authority

Use these as strong defaults. When they conflict with explicit user instructions, repo rules, security/compliance requirements, production incident constraints, or established local conventions, follow the higher-authority requirement and call out the tradeoff:

- Think before coding: surface assumptions, ambiguity, and tradeoffs before changing code.
- Simplicity first: build the smallest correct solution for present requirements — real data volume, failure cost, and contract safety — not anticipated future ones. Avoid unrequested features, abstractions, flexibility, or speculative safeguards unless risk or system contracts justify them. Minimality constrains what you ship, not what you consider — explore the wider design space freely.
- Surgical changes: touch only what the request requires; match existing style; clean up only issues caused by your change.
- Contribute your judgment: propose materially better approaches, framings, or designs with a clear recommendation — withholding a better idea is as much a failure as overbuilding. The gate is on acting unilaterally, never on proposing.
- Goal-driven execution: define success criteria, make them strong enough to verify independently, and loop until verified.

When these principles conflict with each other, correctness and contract safety win over simplicity and minimal diff. Call out the added scope rather than expanding silently.

Scale process to risk. On small, low-risk changes, assumptions, success criteria, and handoff notes can each be a sentence, or be skipped when self-evident. Reserve full rigor for contract-touching, multi-step, or hard-to-reverse work.

The goal is clean, efficient, elegant, industry-grade software: clear contracts, explicit boundaries, reliable behavior, testability, and maintainable code without unnecessary machinery — where elegance is economy, not cleverness for its own sake.

## Calibrate the Approach

Apply the same principles and repo conventions across applicable tasks; scale the bar to the change's actual cost and reversibility, not its category. The same edit can be expensive in a large, contract-heavy system and cheap in a small, young, or well-tested one, so a mid-implementation refactor can still be worthwhile.

As cost and irreversibility rise, stay surgical, match convention by default, and propose deviations with their reasons. As they fall, surface worthwhile fixes rather than silently passing them. Act only within scope: make and explain in-scope fixes; report the rest separately.

Scale ambition with openness. For open-ended or greenfield work, present the ambitious option alongside the minimal one. For well-specified execution, default to the minimal option and mention the ambitious one only briefly. A precisely worded request may still be open-ended when it prescribes a mechanism instead of a goal, contradicts the code, or describes only a symptom; treat it accordingly and surface the option the requester may not know to ask for.

When surfacing findings, weigh substance over taste. A divergence from the repo's own norms is a strong finding; a mere difference from your preferred style is not. Do not bury real findings in noise.

## Workflow

Follow these steps when changing artifacts. For reviews, use the same principles as evaluation criteria and weight findings by their risk.

1. Read before coding.
   - Inspect the relevant files, tests, docs, and existing conventions.
   - For structural decisions, inspect the tree, import/dependency rules, build files, tests, and representative files in the area before choosing where code belongs.
   - Identify the behavioral surface: inputs, outputs, side effects, persistence, external calls, and user-visible contracts.
   - State assumptions when they affect implementation or risk; do not hide confusion.
   - When the request prescribes a mechanism ("add a retry loop here"), restate the goal it appears to serve before planning; if the mechanism serves that goal poorly, recommend what would serve it better.
   - If multiple materially different interpretations exist, present them with a clear recommendation instead of picking silently.
   - Recommend a simpler approach when one exists and push back when warranted.
   - If a more complex design is plausibly better for likely future needs, present its tradeoff and let the user make that bet; do not build for the future unprompted.
   - For a bug fix, treat the report as a symptom, not the cause: trace the callers of the code you touch and fix the shared cause once, rather than patching only the path the report names and leaving sibling callers broken.

2. Define the smallest verifiable plan.
   - Convert the request into concrete success criteria, each written as an observable check: a command to run, an expected output, or an assertion — not a vague goal. ("`GET /users/:id` returns 404 for unknown ids" beats "handle missing users".)
   - For new or changed behavior, reproducible regressions, test work, or reviews of test adequacy, read [Behavior-First Testing](references/behavior-first-testing.md) before implementation or executable test bodies and follow its workflow.
   - Prefer the narrowest change that satisfies those criteria without worsening system shape.
   - Ask when ambiguity would materially change the solution, create risk, or leave success criteria too weak to verify.
   - If no one is available to answer, choose the most reversible interpretation, state the assumption prominently in the handoff, and proceed.
   - When mid-implementation discovery contradicts the agreed plan, take the most reversible option that honors the plan's intent, record the deviation in a notes file (preferred over commit messages or PR descriptions; the handoff summary is not a record), and surface it in the handoff.
   - If the discovery invalidates the plan's premise, stop and re-plan instead of pushing through.
   - For multi-step work, state each step with its verification check.

3. Preserve system shape.
   - Treat the codebase's existing structure — its system shape — and conventions as evidence and match them by default; when the current structure blocks the change or conflicts with these principles, propose the improvement with its reason.
   - Prefer domain or capability ownership over scattered technical-role buckets unless the repo already dictates otherwise.
   - Where the system is layered, keep responsibilities separate: boundary adapters validate and translate, core logic decides, and persistence or integration code performs I/O.
   - Do not mix business rules, transport details, storage concerns, and formatting unless the existing system already does so and the change is tiny.
   - In small scripts or single-file programs, do not introduce layers or indirection.
   - Point dependencies toward stable core behavior and away from volatile edges; prefer explicit collaborators over hidden globals, ambient state, or hard-to-control side effects.
   - Avoid dependency cycles; they make separate parts change as one unit.
   - Protect public contracts: APIs, schemas, migrations, events, config, CLI flags, serialized formats, and persisted data need compatibility, rollout, and rollback care.

4. Write clear code.
   - The best code is the code never written. Before adding code, stop at the first rung that holds: does it need to exist (YAGNI); does the repo already provide it; does the standard library or platform cover it; does an already-installed dependency cover it. Only then write the minimum that works. Smaller never means flimsier: between two equally small options, take the edge-case-correct one.
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
   - Never log secrets, credentials, tokens, private keys, personal data, or full sensitive payloads.
   - Make production behavior observable with appropriate logs, metrics, traces, or audit events when the system would otherwise be hard to diagnose.
   - Avoid hidden concurrency and fire-and-forget work unless intentional, documented, and observable.
   - In hot paths, consider data volume, algorithmic complexity, indexing, batching, caching, and N+1 risks; measure before broad optimization.

6. Organize files conservatively.
   - Put new code where a newcomer would expect it, near the code and tests that are read and changed with it. Tree distance should track conceptual distance.
   - Split by reason-to-change, not line count. Treat unusual size as a prompt to look for hidden seams, not a reason to split by itself; a long cohesive file is better than fragments that must be understood together.
   - Split only when the new unit has a real interface with leverage; avoid forwarding layers and navigation-only abstractions.
   - A new unit can be a directory of cohesive modules. Promoting `routes.ts` to `routes/` with one module per domain (`users`, `admin`) is sound when each module is a real boundary, but not when the pieces are arbitrary slices or the folder only exists to re-export them.
   - Keep types, constants, helpers, and docs near their primary consumers unless shared use justifies extraction.
   - Extract shared code only after real reuse, group it by cohesive subject and ownership, and avoid catch-all helper or utility dumping grounds.
   - Document or enforce only load-bearing naming, ownership, dependency, and boundary rules.

7. Document only useful intent.
   - Make code clear through names and structure first; add comments only for non-obvious why: invariants, tradeoffs, ordering, retries, idempotency, fallbacks, security constraints, or business rules.
   - When you deliberately choose a simpler implementation with a known ceiling (a coarse lock, an O(n²) scan, a naive heuristic), comment the ceiling and the condition that would justify upgrading it — so the shortcut reads as a decision, not an oversight.
   - Do not comment obvious syntax, trivial control flow, or unclear code that should instead be simplified.

8. Validate and finish cleanly.
   - Run the most relevant formatter, linter, typecheck, test, build, or targeted smoke check available.
   - If a full check is expensive or unavailable, run the narrowest meaningful check and state the gap.
   - Review the diff: every changed line should trace to the request or to cleanup caused by your change.
   - Keep changes reviewable: avoid unrelated churn, explain non-obvious tradeoffs, and make contract or migration effects explicit.
   - Remove unused imports, variables, functions, and branches introduced by your edit.
   - Leave unrelated pre-existing issues untouched and mention them separately when useful.
   - Confirm every scaffolded scenario has an executable test body or a documented reason for remaining skipped (see [Behavior-First Testing](references/behavior-first-testing.md)).
   - Summarize the handoff: passed success criteria; what changed and why; assumptions and plan deviations; skipped tests or revised scaffold outcomes with reasons; intentional exclusions; and remaining gaps or risks.

## Gotchas

- Do not equate "more robust" with more code. Unrequested fallbacks, retries, abstractions, and options often make systems worse.
- Do not use minimality to omit what present requirements demand: validation, error handling, and rollback care are part of correct, not extras.
- Do not treat a smaller diff as automatically better: the smallest change in the wrong place isn't simpler, it's a second bug. Earn the small diff by understanding the flow first.
- Do not delete pre-existing dead code unless the user asked for that cleanup.
