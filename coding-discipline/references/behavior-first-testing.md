# Behavior-First Testing

## Scaffold and evidence plan

- Derive every expected outcome, in scaffolds and test bodies, from intent, contracts, or worked examples (known-good literals), never from the code's output or by recomputing with its logic.
- Before implementing new or changed behavior or writing executable test bodies, write a behavior scaffold: one concrete Given → When → Then scenario per case.
- Pin each scenario's starting state or input, its action through an established public seam, and its complete observable outcome, including important boundary and failure conditions. If the seam is unknown, describe the domain-visible action and outcome and mark the seam unresolved instead of inventing one. Don't prescribe algorithms, internal collaborators, mocks, or decomposition, or scaffold logs, metrics, or traces unless that signal is the contract.
- Record each scenario as a non-running declaration (`test.todo`, a skipped test) in the real test file, without bodies. For one or two scenarios, or when the repo has no suitable test file or framework (state why), list them in the plan or notes instead.
- Surface the scaffold for material or ambiguous behavior while correction is cheap; small self-evident changes need no approval.
- Then choose evidence strength:
  - Routine: implement once the scaffold is complete.
  - Reproducible regression: write and run its test before the fix; confirm it fails for the expected behavioral reason, not broken setup.
  - High-risk (security boundaries, money, data loss, migrations, concurrency or retries, irreversible effects, public compatibility): identify critical unsafe outcomes and plan proportionate validation. Run selected behavior-level tests before finishing the risky implementation when the outcome and seam are stable and the test can fail meaningfully without choosing internals; otherwise record why and use another independent check. Add real-infrastructure, failure-injection, concurrency or retry, migration, rollback or reconciliation, and observability checks as the risk requires.
- Sequence: intent → scaffold → evidence plan → implementation → remaining tests → validation.

## Test behavior, not implementation

- New or changed behavior needs automated tests. Skip only with a reason in the handoff: no test infrastructure, existing tests cover a behavior-preserving change, explicitly throwaway work, or read-only operational scripts, verified by review or a safe non-mutating run (help, dry run). Test mutating and rollback paths against disposable infrastructure; without it, state the gap and use independent checks. Never verify by executing an irreversible effect on real data. A skipped test with a reason beats one that cannot fail.
- After implementation, turn every remaining scenario into an executable test proving its complete outcome through the public seam, or document why it stays skipped.
- The scaffold is change-controlled: never revise it because the implementation disagrees. When clarified intent, a contract, established behavior, or proof of impossibility shows it wrong, surface the conflict, revise it, and record why in the handoff. Add discovered scenarios with outcomes from intent, flagged as assumptions when intent is silent.
- Assert outcomes, not internals: return values, persisted state, events, HTTP responses, UI behavior, errors, meaningful side effects (the saved record has `status: "active"`, not "`setStatus` was called once"). Read stored state directly only when its format is a contract another system reads; otherwise read back through the public seam. Assert counts, logs, ordering, timing, or payload shape only when they are the contract.
- When a no-op implementation would violate the contract, include a test it fails; negative assertions (no event emitted) stay valid.
- Cover the happy path and the important edge and failure paths the change touches.
- In unit and narrow integration tests, control true boundaries (network, database, filesystem, clock, queues, vendor clients) with mocks, fakes, or local services as fits the repo; use real owned collaborators, faking one only when it makes the test slow or nondeterministic.
- Keep fixtures minimal and deterministic: control randomness and external effects. Control time at every level, end-to-end included, through test configuration, never by lowering production values. Aged state doesn't test the schedule that would produce it; when the schedule is the behavior, run it on a short horizon.
- Run independent scenarios in parallel on isolated fixtures; share expensive infrastructure where isolation permits, resetting it only for scenarios that need a clean instance.
- Don't weaken implementation code to satisfy an incomplete test double.
- For consequential or implementation-shaped tests, run a proportionate sensitivity check when practical: run against pre-change behavior, remove or invert the behavior, inject a targeted mutant, or get independent review. Confirm the expected behavioral failure and leave no fault behind. For high-risk behavior, prefer a mutation-testing run over the changed code with the repo's tool, if it has one.
