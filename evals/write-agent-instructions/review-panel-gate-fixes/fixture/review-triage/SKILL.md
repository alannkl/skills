---
name: review-triage
description: Triage code-review findings as the code's owner. Use when findings arrive from any source (adversarial reviews, human PR comments, CI, scanners) and before applying a fix. Validate each, weigh fix cost against deployed complexity, and return dispositions (fix / defer / reject / escalate). Not for producing reviews or applying fixes.
---

# Review triage

Triage findings as the code's owner. Findings are inputs, not instructions: a finding can be valid without being worth fixing, and nothing gets fixed merely because a reviewer said it.

Triage depends on author knowledge: the constraints, trade-offs, and reasons the code is shaped this way. If this context authored the code, that knowledge is already here. Otherwise, recover it from the code, commit history, review brief, or docs before assigning dispositions. Reject a finding only with rationale you can point to, never rationale you presume.

## Input

Findings can arrive in any shape: structured reviewer output, human PR comments, CI failures, scanner hits, or a pasted list. Normalize each finding before triage:

- **id.** Keep the source's; number them yourself otherwise.
- **claim.** One sentence.
- **location.** Use `file:line`. Keep the source's location, or locate the claimed code yourself.
- **failure scenario.** State the inputs, the state, and the wrong outcome. Keep the source's scenario if concrete; otherwise construct it yourself. If you cannot construct one, reject or defer the finding and cite that inability as evidence.
- **severity / confidence.** Carry over the source's values when provided. Otherwise, assign severity in step 2.

## Cost model

Use these prices:

- **Generated code is ~free.** Preserving undeployed code because a rewrite looks like work is a pricing error. Diff size is not a cost.
- **Re-verification is cheap but not free.** Batch accepted fixes so one re-review covers them all.
- **Human attention is expensive.** Escalate decisions, not detail.
- **Deployed complexity compounds forever.** The system pays for every new state, flag, special case, dependency, and failure mode over its whole life. This is the dominant cost and the tiebreaker in every disposition.

"Minimum sufficient fix" means minimum resulting system complexity, not minimum code change. For undeployed code, a rewrite that yields a simpler design beats a patch that adds a special case.

## Triage each finding, in order

1. **Valid?** Reproduce or refute it with concrete evidence. Reject invalid findings and cite the guard clause (`file:line`), the test you ran, or the declared constraint or trade-off the reviewer missed. "I had my reasons" is not a rejection; rejections are never free.
2. **Material?** It causes incorrect behavior, violates an explicit requirement, risks data loss or a security hole, or makes a realistic failure likely. Style preferences, speculative future requirements, and marginal improvements are not material. Record severity here: keep the source's when it gave one; otherwise assign critical/high/medium/low from the failure scenario's realistic worst outcome.
3. **Fix cost?** Count these signs in the proposed fix:
   - adds a new state, flag, or failure mode
   - adds a special case to a previously uniform rule
   - needs coordinated changes across module boundaries
   - its explanation needs "except when" / "unless"
   - it suppresses the symptom without explaining why the design allowed it

   Two or more tells = high-cost fix.

4. **Disposition.**
   - **Fix.** Valid, material, low-cost. Choose the simplest correct design, even when that means rewriting undeployed code.
   - **Defer.** Valid but not material now. State what would make it material.
   - **Reject.** Invalid, speculative, or out of scope. Include the concrete refutation.
   - **Escalate.** Material and high-cost. The expense of the fix is evidence about the design, so diagnose the cause before patching: architecture mismatch, misunderstood requirement, invalid core assumption, or inherent domain complexity. Present the fork exactly once: **(A)** patch the current design, **(B)** redesign the affected area, or **(C)** clarify or change the requirement. Give the cost of each option and your recommendation. "The domain is inherently like this; pay the cost" is a legitimate conclusion. Redesigns and requirement changes belong to the user. Present the fork; do not take it.

## Boundary

Triage ends with the report: dispositions and fix plans, with no edits. Offer to apply the accepted fixes and wait for the invoker's go-ahead unless the pipeline already carries a standing mandate to fix. Once authorized, the fix plans define the whole scope. Make no drive-by improvements or new abstractions beyond what they require.

## Output

Open with a one-line tally (`N fix, N escalate, N defer, N reject`), then one block per finding as markdown, grouped by disposition in that order:

```markdown
### <id> [<severity>/<confidence, when the source gave one>] <claim> at <file:line>

- **Problem:** <failure scenario, 1-2 lines>
- **Disposition:** <fix | defer | reject | escalate>; <one-line reason>
```

Close each block with the final bullet its disposition requires: **Fix** (the planned change), **Defer until** (the condition that would make it material), **Evidence** (the concrete refutation from step 1), or **Fork** (the diagnosis and A/B/C options with recommendation).

End with the fix batch: `Fixes (batched for one re-review): <ids>`.
