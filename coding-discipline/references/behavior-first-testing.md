# Behavior-First Testing

## Define the Behavior Scaffold and Evidence Plan

- For every new or changed behavior, write a behavior scaffold before its implementation or executable test bodies: one concrete Given → When → Then scenario per case, with expected outcomes derived from intent, contracts, or worked examples, never from running the code.
- Pin each scenario's starting state or input, its action through an established public seam when one exists, and its complete observable outcome, including important boundary and failure conditions. If the technical seam is unknown, describe the domain-visible action and outcome and mark the seam unresolved rather than inventing an interface. Don't prescribe algorithms, internal collaborators, mocks, decomposition, or incidental calls, and don't scaffold diagnostic logs, metrics, or traces unless that signal is the contract.
- Record one non-running declaration (`test.todo`, a skipped test, or the framework equivalent) per scenario in the real test file, without test bodies yet. For a change with one or two scenarios, use a written list in the plan or notes instead; do the same, stating why, when the repository has no suitable test file or framework.
- Surface the scaffold for material or ambiguous behavior while correction is cheap; small, self-evident changes need no approval ceremony.
- Then choose evidence strength:
  - Routine forward development: implement once the scaffold is complete.
  - Reproducible regression: complete and run the relevant scaffolded test before the fix, and confirm it fails for the expected behavioral reason, not broken setup.
  - High-risk behavior — such as security boundaries, money movement, data loss, migrations, concurrency or retries, irreversible effects, or public compatibility: identify critical unsafe outcomes and a proportionate validation plan. Run selected behavior-level tests before completing the risky implementation when the outcome and public seam are stable, the test observes external behavior without choosing internals, and it can fail meaningfully; otherwise record why and use another proportionate independent check. Test timing alone is not enough: include real-infrastructure, failure-injection, concurrency or retry, migration, rollback or reconciliation, and observability checks as the risk requires.
- Default sequence: intent → behavior scaffold → evidence plan → implementation → remaining tests → validation.

## Test New or Changed Behavior at the Right Level, Not Implementation

- New or changed behavior requires automated tests. Skip only with a stated reason in the handoff: no test infrastructure, a behavior-preserving change existing tests already cover, explicitly throwaway work, or read-only operational scripts (smoke checks, ops CLIs, other one-off tooling), which you verify by review or a safe non-mutating run (help, dry-run, smoke). Test a script's mutating and rollback paths, such as a migration's, against disposable infrastructure; without it, state the gap and use proportionate independent checks. Never verify by executing an irreversible effect on real data. Never write vacuous tests to satisfy this rule: a skipped test with a reason beats a test that cannot fail.
- After implementation, translate every remaining scenario into an executable test from its pinned behavior and applicable contracts, not from the implementation's structure or observed output. Each body proves the complete outcome through the public seam.
- The scaffold is change-controlled, not immutable. Don't revise it merely because the implementation disagrees; when clarified intent, an applicable contract, established behavior, or proof of an impossible scenario shows it wrong, surface the conflict, revise it, and record why in the handoff.
- Add newly discovered scenarios with outcomes derived from intent, or flag them as assumptions when intent is silent. Never silently revise or remove a pinned outcome.
- Assert outcomes over internals: return values, persisted state, emitted events, HTTP responses, UI-visible behavior, thrown errors, or meaningful side effects (the saved record has `status: "active"`, not "`setStatus` was called once"). Assert stored state directly only when its format is a contract another system reads; otherwise prove persistence by reading back through the public seam.
- Cover the happy path and the important edge and failure paths the change touches.
- In unit and narrow integration tests, control true boundaries — network, database, filesystem, clock, queues, vendor clients — with mocks, fakes, local services, or realistic test dependencies as fits the repo; use the real internal collaborators you own, faking one only when it makes the test slow or nondeterministic.
- Keep fixtures minimal and deterministic: control randomness and external effects, and control time at every level, end-to-end included, by injecting a clock, aging timestamps, or setting short horizons through test configuration, never by lowering production values. Aged state does not test the timer or schedule that would have produced it; when that schedule is the behavior, run it on a short horizon.
- Run independent scenarios in parallel on isolated fixtures. Reuse expensive infrastructure across the suite where isolation permits; rebuild or reset it only for a scenario that needs a clean instance.
- Don't weaken implementation code to satisfy an incomplete test double.
- For consequential or implementation-shaped test translations, run a proportionate sensitivity check when practical: run against pre-change behavior, temporarily remove or invert the behavior, introduce a targeted mutant, or get independent review. Confirm failure for the expected behavioral reason and leave no deliberate fault behind. For high-risk behavior, the strongest form is a mutation-testing run over the changed code with the repo's tool, if it has one.
- Before finishing, confirm every scenario has an executable body proving its full pinned outcome, or document why it stays skipped.

## Gotchas

- Don't assert incidental counts, logs, ordering, timing, or payload shape unless they are the contract.
- When a no-op implementation would violate the contract, include a test it fails; keep valid negative assertions, such as no event emitted.
- Avoid tautological tests: never derive expected values from the implementation's output or recompute them with the same logic; use independent expected outcomes, such as known-good literals or worked examples from stated intent.
