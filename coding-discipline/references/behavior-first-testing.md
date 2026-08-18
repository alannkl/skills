# Behavior-First Testing

## Define the Behavior Scaffold and Evidence Plan

- For every new or changed behavior, create a behavior scaffold before writing its implementation or executable test bodies: one concrete Given → When → Then scenario per case, with expected outcomes derived from intent, contracts, or worked examples — never by running the code.
- Pin each scenario's starting state or input, action through an established public seam when one exists, and complete observable outcome, including important boundary and failure conditions. If the technical seam is genuinely unknown, describe the domain-visible action and outcome and mark the seam unresolved rather than inventing an interface. Do not prescribe algorithms, internal collaborators, mocks, decomposition, or incidental calls. Do not scaffold diagnostic logs, metrics, or traces unless that signal is itself the contract.
- Record one non-running declaration (`test.todo`, a skipped test, or the framework equivalent) per scenario in the real test file; do not write the test bodies yet. Use a written list in the plan or notes only when the repository has no suitable test file or framework, and state why.
- For material or ambiguous behavior, surface the scaffold while correction is cheap. Small, self-evident changes need no approval ceremony.
- Choose evidence strength after establishing the scaffold:
  - For routine forward development, implement after the scaffold is complete.
  - For a reproducible regression, complete and run the relevant scaffolded test before the fix; confirm it fails for the expected behavioral reason, not because of broken setup.
  - For high-risk behavior — such as security boundaries, money movement, data loss, migrations, concurrency or retries, irreversible effects, or public compatibility — identify critical unsafe outcomes and a proportionate validation plan. Run selected behavior-level tests before completing the risky implementation when the outcome and public seam are stable, the test observes external behavior without choosing internals, and it can fail meaningfully. Otherwise record why and use another proportionate independent check. Do not treat test timing as sufficient; include real-infrastructure, failure-injection, concurrency or retry, migration, rollback or reconciliation, and observability checks as the risk requires.
- Default sequence: intent → behavior scaffold → evidence plan → implementation → remaining tests → validation.

## Test New or Changed Behavior at the Right Level, Not Implementation

- New or changed behavior requires automated tests. Skip only with a stated reason in the handoff: no test infrastructure, a behavior-preserving change already covered by existing tests, explicitly throwaway work, or operational scripts (smoke checks, ops CLIs, and other one-off tooling). Operational scripts get no automated tests; verify them by review or a safe non-mutating run (help, dry-run, smoke), not by executing a migration or other irreversible effect. Never write vacuous tests to satisfy this rule — a skipped test with a reason beats a test that cannot fail.
- After implementation, translate every remaining scaffolded scenario into an executable test from its pinned behavior and applicable contracts — not from the implementation's structure or observed output. Each body must prove the complete outcome through the public seam.
- Treat the scaffold as change-controlled, not immutable. Do not revise it merely because the implementation disagrees. If clarified intent, an applicable contract, established behavior, or proof of an impossible scenario shows it is wrong, surface the conflict, revise it, and record the reason in the handoff.
- Add newly discovered scenarios with outcomes derived from intent, or flag them as assumptions when intent is silent. Never silently revise or remove a pinned outcome.
- Prefer outcomes over internals: return values, persisted state, emitted events, HTTP responses, UI-visible behavior, thrown errors, or meaningful side effects. (Assert that the saved record has `status: "active"`, not that `setStatus` was called once.)
- Cover the happy path, important edge cases, and failure paths touched by the change.
- For unit and narrow integration tests, control true boundaries such as network, database, filesystem, clock, queues, and vendor clients with mocks, fakes, local services, or realistic test dependencies as appropriate to the repo; do not mock internal collaborators you own.
- Keep fixtures minimal and deterministic; control time, randomness, and external effects.
- Do not weaken implementation code to satisfy an incomplete test double.
- For consequential or implementation-shaped test translations, perform a proportionate sensitivity check when practical: run against pre-change behavior, temporarily remove or invert the relevant behavior, introduce a targeted mutant, or obtain independent review. Confirm failure for the expected behavioral reason and leave no deliberate fault behind.
- Before finishing, confirm every scaffolded scenario has an executable body that proves its full pinned outcome, or document why it remains skipped.

## Gotchas

- Do not make tests assert incidental counts, logs, ordering, timing, or payload shape unless those details are the contract.
- Do not let the implementation grade itself: never derive expected test values by running the code and asserting whatever it produces, or by recomputing them in the test with the same logic. Expected outcomes are independent — known-good literals or worked examples from stated intent.
