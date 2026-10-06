---
name: delegate
description: Delegate bounded steps to subagents when that costs less than doing them inline. Use for broad retrieval, long references, verbose command output, independent parallel batches, or acceptance of a delegate's returned record. Not for delegates or reviewers prescribed by another workflow.
---

# Delegate

## Workflow

1. Identify candidates: broad searches, inventories, long references, verbose command output, and independent parallel batches.
   - Handle design, diagnosis, findings, trade-offs, acceptance, and user interaction yourself.
   - Delegate before reading bulky inputs yourself; an orientation read first is fine.
   - Read the instructions that govern your own work yourself, including any skill you load; delegate task material only.

2. If not already loaded, read [Model tiers and cost inputs](references/models.md) for model defaults, availability fallbacks and cost inputs, then weigh each candidate from what you already know. Spend no calls on the weighing and never check the estimate afterward.
   - Verification: can you check the result more cheaply than you can produce it? Use an exit status, diff, count, source-linked record, or quick comparison with the evidence. Would you catch a wrong result before it matters? If not, do the step yourself.
   - Authority: does the step require the user's answer? Get it yourself. Delegate only work within existing authority.
   - Cost: estimate both paths in weighted tokens from the same start to the same end, excluding calls common to both. Use the cost inputs in that reference. Count tokens only; wall-clock time counts only when the user set a deadline.
     - Inline: your model calls at your tier, including reasoning, and the tool calls, tool output, and intermediate reasoning left in your context.
     - Delegated: cold start-up, native or headless lean when the harness has no native subagent tool, and the delegate's calls at its tier; your dispatch, wait, collection, and verification calls; the work order and record left in your context; and the probability-weighted cost of a retry or takeover.
     - On both paths, include every later re-read of the retained context, during and after the step. Count reasoning only where you expect the harness to retain it.
     - Weight tokens by model and kind: reasoning and replies as output; cached context as cache read; new context, including cold start-up, as cache write where billed, otherwise as input. Assume no cache sharing between you and the delegate.

3. Delegate every candidate whose result is cheaper to check than to produce and whose delegated path costs less. Do the rest yourself. For each delegation, follow [Dispatch](references/dispatch.md) to pick the role, write the work order, dispatch, wait, and accept or escalate. Finish by accepting the record or taking over the step.

4. At delivery, report every delegation in one table: role, agent type, requested and runtime-confirmed model, effort, duration, and tokens. Write "not reported" where the harness gives no value, and "requested" where the runtime model is unconfirmed.
