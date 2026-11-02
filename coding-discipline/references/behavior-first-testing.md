# Behavior-First Testing

## Scaffold and evidence plan

- Derive every expected outcome, in scaffolds and tests, from intent, contracts, or known-good examples, never from the code's output or logic.
- Before implementing new or changed behavior or writing test bodies, write a behavior scaffold: one concrete Given → When → Then scenario per case, pinning the starting state, the action through an established public seam, and the complete observable outcome, including boundary and failure cases. If the seam is unknown, describe the domain-visible action and mark the seam unresolved. Prescribe no internals; scaffold logs, metrics, or traces only when that signal is the contract.
- Record each scenario as a non-running declaration (`test.todo`, a skipped test) in the real test file. For one or two scenarios, or with no suitable test file (state why), list them in the plan instead.
- Surface the scaffold for material or ambiguous behavior while correction is cheap.
- Then choose evidence strength:
  - Routine: implement once the scaffold is complete.
  - Reproducible regression: write and run its test before the fix; confirm it fails for the expected behavioral reason, not broken setup.
  - High-risk (security, money, data loss, migrations, concurrency or retries, irreversible effects, public compatibility): identify the critical unsafe outcomes. Run behavior-level tests before finishing the implementation when the seam is stable and the test can fail meaningfully without choosing internals; otherwise record why and use an independent check. Add real-infrastructure, failure-injection, and rollback checks as the risk requires.

## Test behavior, not implementation

- New or changed behavior needs automated tests. Skip only with a reason in the handoff: no test infrastructure, existing coverage of a behavior-preserving change, explicitly throwaway work, or read-only operational scripts verified by a safe non-mutating run. Test mutating and rollback paths on disposable infrastructure, or state the gap; never verify by executing an irreversible effect on real data. A skipped test with a reason beats one that cannot fail.
- After implementation, turn every remaining scenario into an executable test proving its complete outcome through the public seam, or document why it stays skipped.
- Never revise the scaffold because the implementation disagrees. When intent, a contract, established behavior, or proof of impossibility shows it wrong, surface the conflict, revise it, and record why in the handoff. Add discovered scenarios with outcomes from intent, flagged as assumptions when intent is silent.
- Assert observable outcomes, not internals. Read stored state directly only when its format is a contract; otherwise read back through the public seam. Assert counts, logs, ordering, or timing only when they are the contract.
- When a no-op implementation would violate the contract, include a test it fails.
- Cover the happy path and the important edge and failure paths the change touches.
- In unit and narrow integration tests, control true boundaries (network, database, filesystem, clock, vendors) with mocks, fakes, or local services as fits the repo; use real owned collaborators unless they make the test slow or nondeterministic.
- Keep fixtures minimal and deterministic. Control time at every level through test configuration, never by lowering production values; when a schedule is the behavior, run it on a short horizon instead of aging state.
- Run independent scenarios in parallel on isolated fixtures, sharing expensive infrastructure where isolation permits.
- Don't weaken implementation code to satisfy an incomplete test double.
- For consequential or implementation-shaped tests, run a sensitivity check when practical, such as running against pre-change behavior or injecting a mutant; confirm the expected failure and leave no fault behind. For high-risk behavior, prefer the repo's mutation-testing tool on the changed code.
