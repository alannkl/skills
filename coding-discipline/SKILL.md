---
name: coding-discipline
description: Core engineering discipline for code work — keeps changes simple, scoped, maintainable, well-structured, and verified. Use before any task to write, implement, add, build, create, change, fix, debug, refactor, optimize, review, test, or organize code, scripts, configs, APIs, modules, boundaries, or file layout in any language. Load this skill first, then do the task. Skip only for trivial formatting, pure prose edits, or explicitly throwaway prototypes.
---

# Coding Discipline

## Core authority

These are strong defaults. User instructions, repo rules, security or compliance requirements, and local conventions override them, with user instructions outranking conventions; call out the tradeoff.

- Think before coding: surface assumptions, ambiguity, and tradeoffs.
- Simplicity: the smallest correct solution for present requirements.
- Surgical changes: touch only what the request requires; match existing style; clean up only issues your change caused.
- Contribute judgment: propose materially better approaches with a recommendation; withholding one fails as badly as overbuilding. Gate acting, never proposing.
- Goal-driven: define independently verifiable success criteria and loop until they pass.

Correctness and contract safety beat simplicity and minimal diff. Prefer a clean design over a shortcut that leaves the wrong shape; state its cost and the added scope.

Scale process to the change's cost and reversibility: on small low-risk changes, assumptions, criteria, and handoff take a sentence each, or nothing when self-evident.

## Workflow

Follow these steps when changing code. For reviews, use them as criteria, weight findings by risk, and flag divergence from the repo's norms, not from your taste.

1. Read before coding.
   - Read the relevant code, tests, docs, and build config. Manifests, lockfiles, and CI config outrank docs; flag contradictions.
   - Identify the behavioral surface: inputs, outputs, side effects, and contracts.
   - When a request prescribes a mechanism, contradicts the code, or names only a symptom, restate the goal. Present materially different interpretations or designs with the tradeoff and a recommendation; build an alternative only if the user takes it.
   - Offer safeguards against costly failures present requirements don't cover as declinable options, quantifying their downside where evidence allows.
   - For a bug, trace the callers and fix the shared cause once. If the cause isn't evident, apply `references/diagnosing-bugs.md` first.

2. Plan the smallest verifiable change.
   - Write success criteria as observable checks.
   - For new or changed behavior, reproducible regressions, test work, or test-adequacy reviews, apply `references/behavior-first-testing.md` before implementing or writing test bodies.
   - For a refactor, pin behavior with passing tests, adding any needed; restructure; then rerun them unchanged except wiring.
   - Ask when ambiguity would materially change the solution, add risk, or leave criteria unverifiable. With no one to answer, take the most reversible interpretation and state it in the handoff.
   - When discovery contradicts the plan, take the most reversible option that honors its intent, record the deviation in a notes file, and surface it in the handoff. If it breaks the plan's premise, re-plan.
   - State each step's verification check and run it before the next; in a sweep, verify each edit as it lands. Edits that only work together are one step. When a slow run surfaces several issues, let it finish, verify each fix with the fastest covering check, then rerun once.

3. Preserve system shape.
   - Match existing structure and conventions as evidence of taste, not proof, following any newer direction the user or recent work set. Propose an improvement when the structure blocks the change or conflicts with these principles.
   - Organize by domain over technical role unless the repo dictates otherwise.
   - In layered systems, boundaries validate and translate, core logic decides, and adapters do I/O, unless the code already mixes them and the change is tiny. Add no layers to small scripts.
   - Point dependencies toward the stable core; prefer explicit collaborators over hidden globals; avoid cycles.
   - Protect public contracts and persisted data across old data, mixed versions, rollout, and rollback.

4. Write clean code.
   - Before adding code, stop at the first rung that holds: not needed; the repo has it; the standard library; an installed dependency; the minimum that works. Between equally small options, take the edge-case-correct one.
   - Name by intent, with side effects visible. Give functions and modules one purpose; prefer guard clauses to nesting.
   - Give each decision one home; derive the rest from it.
   - Treat extension points a library's published contract promises as requirements.
   - Prefer small, honest interfaces to pass-through wrappers.
   - Zoom out on friction: a third special case, a second synced boolean, a fix needing its own fix, a solution larger than the problem. Restate the problem one level up and look for a simpler structure; continuing is then a stated decision.
   - In typed languages, make illegal states unrepresentable where partiality appears, then stop; never lie to the type checker with casts or silencing escapes.
   - Reuse canonical domain types and APIs instead of local aliases.
   - Suggest or add dependencies that reduce complexity or risk, after weighing security, licensing, and fit.

5. Handle data, errors, and concurrency deliberately.
   - Validate untrusted input at boundaries into a canonical model; past that, trust the types, asserting only high-stakes invariants.
   - Design for authorization, injection, secrets, personal data, and least privilege from the start.
   - Make errors actionable, with diagnostic context.
   - Never log or commit secrets or full sensitive payloads. Never commit personal data; log it only when a stated requirement needs it, and only the fields it needs.
   - Make hard-to-diagnose production behavior observable.
   - No hidden concurrency or fire-and-forget work unless intentional, documented, and observable.
   - In hot paths, weigh data volume, complexity, indexing, N+1 queries, batching, and caching; measure before broad optimization.

6. Organize files conservatively.
   - Put code where a newcomer expects it, near what changes with it.
   - Split by reason to change, not line count, and only into units with a real interface; no forwarding layers or re-export folders.
   - Extract shared code only after real reuse, grouped by subject; no catch-all utils.
   - Document or enforce only load-bearing structural rules.

7. Document only useful intent.
   - Prefer clearer names and simpler code to comments. Document public interfaces per repo convention; otherwise comment only the non-obvious why.
   - For a deliberately simple implementation with a known ceiling, comment the ceiling and what would justify upgrading.

8. Validate and finish.
   - Run the relevant checks; if they are expensive or unavailable, run the narrowest meaningful one and state the gap.
   - In every check, including manual and real-model ones, fast-forward time you control and wait only the minimum. When elapsed time is the evidence or outside your control, bound the wait and state what went unproved. Aim for seconds per test, minutes per suite.
   - For a risky change, verify each fact its safety hinges on by running code, not by argument. Check impact past symbol search, into serialized data, wire formats, feature flags, and readers in other languages; record searches that find nothing.
   - Review the diff: every line traces to the request or to cleanup your change caused. Remove unused code your edit introduced; mention unrelated issues when useful instead of fixing them.
   - Before deleting code, files, branches, or worktrees, confirm they are unneeded; keep pre-existing uncommitted work and unmerged commits unless removal is authorized.
   - When offering to commit, include the proposed message.
   - Write the handoff for the maintaining engineer, scaled to consequence: what changed for callers, operators, or stored data and, for consequential changes, the invariant future edits must preserve; non-obvious tradeoffs; which criteria passed and what the checks didn't establish; assumptions, deviations, exclusions, and skipped tests or revised scaffolds with reasons; pending actions.
