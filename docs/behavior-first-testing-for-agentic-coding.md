# Behavior-First Testing for Agentic Coding

Behavior-First Testing for Agentic Coding is a workflow that establishes observable behavior before code for a change or its executable test bodies are written. The behavior scaffold becomes the source of truth for both, independent of those later artifacts.

The workflow is inspired by Behavior-Driven Development and specification by example, but is adapted to an agentic-coding problem: implementation and executable tests are often produced within the same shared development context.

## The Problem

Agent identity alone does not create independence. One agent may specify, implement, and test a change in one continuous context; multiple agents or subagents may still share repository state, conversation history, diffs, summaries, or generated artifacts. Once the new implementation or executable test mechanics exist, they can bias each other and later attempts to define the intended behavior.

Existing code may already be present, especially for changes and regressions. The separation concerns the new implementation decisions for the change and its executable test mechanics, not the absence of an existing codebase.

In mechanically applied or overly low-level test-driven development, the agent turns behavior directly into executable tests before implementation. Those tests can encode premature API choices, internal seams, mocks, fixtures, or incomplete examples. The implementation may then overfit the agent's test design instead of the user's actual goal. TDD does not require this: well-practiced outside-in TDD can begin with observable behavior and avoid prescribing internals.

A TDD red test provides evidence that its executable setup and assertions detect a system in which the behavior is missing. It also necessarily chooses enough interface and test mechanics to run. Calling a not-yet-created `transfer()` function, for example, already chooses a name, signature, calling style, and boundary for the future implementation. That design pressure can be useful when the public seam is understood and premature when it is not. A red result caused only by a missing import, unimplemented interface, or broken fixture is not yet meaningful behavioral evidence.

In test-last development, the agent sees its implementation before writing tests. The tests may rationalize what the code already does, omit awkward cases, or assert implementation details and observed outputs rather than intended behavior.

Behavior-first testing inserts a small, independently reviewable specification between intent, code, and test mechanics:

```text
User intent
    ↓
Behavior scaffold
   ↙             ↘
Implementation   Executable tests
   └────── validation ──────┘
```

The scaffold is established before new implementation decisions or executable test bodies are authored. This temporal separation—not the number or identity of the agents—is the primary independence mechanism.

The implementation and tests are sibling translations of the behavior scaffold. Neither implementation details nor test mechanics may redefine the scaffold without independent evidence.

The goal is not to prevent required behavior from shaping implementation—that is desirable. It is to prevent incidental test mechanics from shaping implementation and implementation details from shaping tests.

## The Behavior Scaffold

A behavior scaffold is a concrete list of observable scenarios established before implementing the change. Each scenario pins:

- **Given:** the relevant starting state or concrete input;
- **When:** the observable action, through an established public seam when one exists;
- **Then:** the exact observable output, error, state change, or side effect;
- important boundary and failure conditions.

For example:

```ts
test.todo(
  "POST /transfers: $80 from a $50 balance → returns 409, preserves both balances, and writes no ledger entry",
);
```

The scaffold should not prescribe:

- algorithms or control flow;
- function decomposition;
- internal collaborators;
- mocks of code the repository owns;
- incidental calls, logs, ordering, or timing;
- test harness mechanics beyond what is needed to keep the scenario visible.

Store the scaffold as non-running declarations in the real test file—`test.todo`, skipped tests, or the framework equivalent—so it remains visible in the diff and naturally becomes the executable suite. Use a written list only when the repository has no suitable test file or framework.

The scaffold and a TDD red test can describe the same intended behavior, but they provide different evidence. The scaffold is **specification evidence**: it fixes what must be observed without yet choosing how the test reaches or measures it. A red test is **executable detection evidence**: when it fails for the expected behavioral reason, it shows that the chosen setup and assertions can detect the behavior's absence. Keeping the scaffold non-running is deliberate when writing the body would prematurely settle an unstable interface or harness.

Pin an existing or required public contract, such as an HTTP route or CLI command, when intent or repository evidence already establishes it. Do not invent an exported function, signature, collaborator, or other technical seam solely to make the scaffold executable. When the public seam is genuinely unknown, state the domain-visible action and outcome, mark the technical seam as unresolved, and settle it during implementation before translating the scenario into an executable test.

## Workflow

The workflow branches after the scaffold according to the evidence required:

```text
intent → behavior scaffold → evidence plan
                              ↓
            ┌─────────────────┬──────────────────┬─────────────────┐
            ↓                 ↓                  ↓
 regression test → fix   high-risk work       routine work
                         ↕ selected early tests
            └─────────────────┴──────────────────┴─────────────────┘
                              ↓
                  remaining tests → validation
```

### 1. Derive behavior from intent

The agent reads the request, relevant contracts, repository conventions, and existing behavior. It converts them into concrete Given → When → Then scenarios with expected values determined independently of the future implementation.

For material or ambiguous behavior, the agent surfaces the scaffold while correction is still cheap when the user is available, but does not pause solely to obtain approval.

Establish expected behavior from user intent, applicable contracts, repository evidence, or an explicitly documented assumption. Ask only when an unresolved ambiguity would materially change the observable behavior and the available evidence does not support a safe choice; otherwise proceed with the safest reversible interpretation and disclose the assumption. Small, self-evident changes need no approval ceremony.

### 2. Create the scaffold

The agent records one non-running declaration per scenario before implementing new or changed behavior. The scaffold must pin the complete observable outcome and identify the public seam when it is already established. A genuinely unknown technical seam remains explicitly unresolved rather than being invented for the test.

### 3. Choose the required evidence strength

For routine forward development, implementation may begin once the scaffold is established under the rule above.

A **reproducible regression** is existing intended behavior that is currently broken and can be demonstrated reliably. Complete the relevant scaffolded test and run it before fixing the regression. Confirm that the test fails for the expected behavioral reason—not because of a syntax error, missing fixture, or broken setup. This proves that the test detects the known failure and will guard against its return.

**High-risk behavior** is behavior whose failure could cause material harm, escape ordinary review, or be difficult to reverse or diagnose. Examples include authorization and security boundaries, money movement, data loss or corruption, migrations, concurrency and retry behavior, irreversible external side effects, and public compatibility contracts. Before implementation, identify the critical unsafe outcomes and record a validation plan proportionate to the risk.

For selected high-risk scenarios, run a behavior-level test before completing the risky implementation when all of these conditions hold:

- the behavior scaffold already fixes the expected outcome;
- the public seam is stable;
- the test observes externally meaningful results;
- the test does not require choosing internal architecture; and
- a pre-completion run can fail for a meaningful behavioral reason.

That failing run demonstrates that the test detects a system that still permits the critical unsafe outcome. It does not make the test the source of truth: the test remains a translation of the previously established scaffold.

If those conditions do not yet hold, preserve the scaffold, establish the smallest necessary interface or test environment, and execute the selected test before completing the risky logic when practical. If that remains impractical, document why and use another independent check proportionate to the risk.

Test timing alone is not sufficient assurance for high-risk behavior. The validation plan should cover the important failure modes with the appropriate combination of public-seam tests, real-infrastructure integration checks, failure injection, concurrency or retry tests, migration dry runs, rollback or reconciliation checks, and operational observability.

### 4. Implement from the scaffold

The agent implements from the scaffold and applicable repository constraints. Executable tests enforce the scaffold's observable behavior, but their incidental mechanics must not dictate the architecture, decomposition, or internal seams.

### 5. Translate the remaining scaffold into executable tests

After implementation, the agent fills in any remaining test bodies from the scaffold's inputs, outcomes, and applicable contracts—not from the implementation's structure or observed output. Each body must prove the full pinned outcome through the public seam.

### 6. Validate and close the loop

Before finishing, every scaffolded scenario must have an executable test body, or a documented reason for remaining skipped. The agent runs the relevant checks and reports the evidence and any remaining gaps.

Passing after implementation shows that code and test agree; it does not by itself show that the test would detect a relevant defect. For scenarios where translation error would be consequential or the test body was especially shaped by implementation details, add a proportionate sensitivity check when practical: run the test against the pre-change behavior, temporarily remove or invert the relevant behavior, introduce a targeted mutant, or obtain an independent review of the test translation. The check should demonstrate a failure for the expected behavioral reason and must not leave the deliberate fault in the final code.

## Change Control

The scaffold is change-controlled, not immutable. Implementation can reveal a mistaken assumption, an impossible scenario, or a previously unknown contract. It cannot, by itself, prove that the scaffold is wrong.

Use this decision rule:

- **The code disagrees with the scaffold:** fix the code.
- **Independent evidence disproves the scaffold:** revise the scaffold and record why.
- **A new behavior or edge case is discovered:** add a scenario with an outcome derived from intent, or mark the outcome as an assumption when intent is silent.

Independent evidence includes clarified user intent, an applicable public contract, repository documentation, established compatible behavior, or proof that the original scenario was impossible. “The implementation currently does something else” is not independent evidence.

For a material change to a pinned scenario, surface the conflict before revising it when that does not block progress. Do not pause solely for approval: apply the ambiguity rule above, record the independent evidence, and always disclose revised or removed scenarios in the handoff.

## Behavior-Preserving Work

A refactor or other change that does not alter behavior does not need new scenarios when existing tests already cover the relevant behavior. The agent should state that basis in the handoff.

## Relationship to TDD, BDD, and Test-Last Development

Behavior-first specification and executable test timing are separate dimensions:

| Workflow | Behavior established independently | Executable detection evidence | Main agentic trade-off |
| --- | --- | --- | --- |
| TDD without a prior behavior scaffold | In the executable test | Before each implementation increment | Early feedback, but the test can prematurely fix an interface, harness, or internal seam |
| Behavior-scaffolded TDD | In the scaffold | Before each implementation increment once a meaningful seam exists | Combines independent behavior with early feedback, but still commits to test mechanics before implementation |
| Test-last without a prior behavior scaffold | After or through the implementation | After implementation | Highest risk that tests rationalize completed code |
| Behavior-first with later test translation | In the scaffold | After implementation, except for regressions and selected high-risk behavior | Avoids fixing unstable test mechanics early, but later translations require drift and sensitivity checks |

Behavior-first testing is closest to BDD because it starts from observable scenarios and shared understanding. Its distinguishing constraint for agentic coding is the independence rule: behavior shapes both implementation and tests, while neither implementation details nor test mechanics may redefine behavior without independent evidence.

Behavior-first is therefore a specification discipline that can be combined with TDD or with later executable-test translation, not a categorical replacement for TDD. Good outside-in TDD may already begin from an independently established behavior list and express observable behavior through a stable public seam; in that case, the approaches substantially overlap. Behavior-first changes the default when executable test mechanics would themselves make premature design decisions: it pins behavior first, requires a reproducing test before fixing a regression, selectively executes behavior-level tests before completing high-risk behavior once the seam is stable, and otherwise permits test bodies to wait until after implementation.

Compared with unscaffolded test-last development, behavior-first provides a stronger independent oracle. Compared with behavior-scaffolded TDD, it trades early executable feedback for less premature interface and harness commitment. Which is preferable depends on whether the public seam is stable and whether early detection evidence is worth that commitment.

## Limits

Temporal separation prevents the scaffold from being derived from the new implementation or executable test mechanics, but it does not eliminate interpretation or translation errors. The scaffold author can misread intent or applicable contracts, and later implementation or test work can drift from—or improperly revise—the established scaffold. Concrete scenarios, explicit assumptions, change control, and final review make that drift visible. Independent, context-isolated review provides stronger assurance when the stakes justify it.

The scaffold also cannot repair an incorrect requirement. It preserves an established interpretation so that mistakes can be found and revised explicitly instead of being hidden inside code or tests.

## Completion Checklist

- Every new or changed behavior traces to a scaffolded scenario.
- The scaffold predates code for the change and executable test bodies.
- Every scenario identifies its concrete observable outcome and either an established public seam or an explicitly unresolved technical seam.
- No scenario specifies unnecessary implementation or test mechanics.
- Implementation decisions trace to behavior or repository constraints, not imagined assertions.
- Every reproducible regression has a valid failing test before the fix.
- Every high-risk behavior has identified unsafe outcomes and a proportionate validation plan; selected behavior-level tests run before the risky implementation is complete when the public seam permits it.
- Test bodies prove the scaffold rather than mirror the implementation.
- Consequential or implementation-shaped test translations receive a proportionate sensitivity check when practical.
- Expected values come from intent, contracts, or worked examples—not execution output or duplicated implementation logic.
- Scaffold revisions cite independent evidence and appear in the handoff.
- Every scenario is executable before completion or has a documented reason for remaining skipped.
