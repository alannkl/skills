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
- **failure scenario.** State the inputs, the state, and the wrong outcome. Keep the source's scenario if concrete; otherwise construct it yourself. If no concrete scenario can be supported, reject the finding as unsupported, without claiming the code is safe. If a plausible material scenario depends on evidence you cannot get, defer it pending a specific check.
- **severity / confidence.** Carry over the source's values as starting estimates; step 2 revises them.

## Cost model

Use these prices:

- **Generated code is ~free.** Preserving undeployed code because a rewrite looks like work is a pricing error. Diff size is not a cost.
- **Re-verification is cheap but not free.** Batch accepted fixes so one re-review covers them all.
- **Human attention is expensive.** Escalate decisions, not detail.
- **Deployed complexity compounds forever.** The system pays for every new state, flag, special case, dependency, and failure mode over its whole life. This is the dominant cost and the tiebreaker in every disposition.

"Minimum sufficient fix" means minimum resulting system complexity, not minimum code change. For undeployed code, a rewrite that yields a simpler design beats a patch that adds a special case.

## Triage each finding, in order

1. **Valid?** Reproduce or refute it with concrete evidence. Reject invalid findings and cite the guard clause (`file:line`), the test you ran, or the declared constraint or trade-off the reviewer missed. "I had my reasons" is not a rejection; rejections are never free.
2. **Material?** It causes incorrect behavior, violates an explicit requirement, risks data loss or a security hole, or makes a realistic failure likely. Style preferences, speculative future requirements, and marginal improvements are not material. Record critical/high/medium/low severity from impact and likelihood, revising the source's estimate when validation changes either. Revise confidence separately when the supporting evidence changes.
3. **Fix cost?** Count these signs in the proposed fix:
   - adds a new state, flag, or failure mode
   - adds a special case to a previously uniform rule
   - needs coordinated changes across module boundaries
   - its explanation needs "except when" / "unless"
   - it suppresses the symptom without explaining why the design allowed it

   Two or more tells = high-cost fix.

4. **Disposition.**
   - **Fix.** Valid, material, low-cost. Choose the simplest correct design, even when that means rewriting undeployed code.
   - **Defer.** Valid but not material now, or plausibly material but awaiting a specific check you cannot run. For the first, state what would make it material; when its code is in scope, plan a comment naming the ceiling and trigger, or a ticket for a scheduled check (a date, a vendor change). For the second, name the check and how its result would settle the finding; keep the uncertainty in the report, with no comment.
   - **Reject.** Invalid, speculative, or out of scope. Include the concrete refutation. When the code invites the misreading, or the finding has been rejected before, plan a one-line comment there naming the wrong reading. When the same misreading recurs across files, one line in the repo's review guidance may replace a comment per site; record the rationale, never a rule to skip a finding class.
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

Close each block with the final bullet its disposition requires: **Fix** (the planned change), **Defer until** (the materiality trigger or outstanding check, plus a planned comment or ticket only for a valid non-material finding), **Evidence** (the concrete refutation from step 1, plus the planned comment when one is due), or **Fork** (the diagnosis and A/B/C options with recommendation).

End with the fix batch: `Fixes (batched for one re-review): <ids>`, including every deferred or rejected finding with a planned comment.
