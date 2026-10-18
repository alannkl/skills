---
name: delegate
description: Delegates bounded steps to subagents when that costs less than doing them inline, or saves the user time at bounded extra cost. Use before searching broadly, reading a long reference, running a verbose command, implementing a design you have fixed, or starting independent parallel batches, and when accepting a delegate's returned record. When another workflow requires an agent or reviewer, follow its delegation rules.
---

# Delegate

## Workflow

1. Identify candidates: broad searches, inventories, long references, verbose command output, code changes that carry out a design you have fixed, and independent parallel batches.
   - Handle design, diagnosis, findings, trade-offs, acceptance, and user interaction yourself.
   - Delegate before reading bulky inputs yourself; an orientation read first is fine.
   - Read the instructions that govern your own work yourself, including any skill you load; delegate task material only.

2. If not already loaded, read `references/models.md` for model defaults, availability fallbacks and cost inputs, then weigh each candidate from what you already know. Spend no calls on the weighing and never check the estimate afterward.
   - Verification: can you check the result more cheaply than you can produce it? Use an exit status, diff, count, source-linked record, or quick comparison with the evidence. Would you catch a wrong result before it matters? If not, do the step yourself.
   - Authority: does the step require the user's answer? Get it yourself. Delegate only work within existing authority.
   - Cost: estimate both paths in weighted tokens from the same start to the same end, excluding calls common to both.
     - Inline: your model calls at your tier, including reasoning, and the tool calls, tool output, and intermediate reasoning left in your context.
     - Delegated: cold start-up (native subagent, or headless lean when the harness has none) and the delegate's calls at its tier; your dispatch, wait, collection, and verification calls; the work order and record left in your context; and the probability-weighted cost of a retry or takeover.
     - On both paths, include every later re-read of the retained context, during and after the step. Count reasoning only where you expect the harness to retain it.
     - Weight tokens by model and kind: reasoning and replies as output; cached context as cache read; new context, including cold start-up, as cache write where billed, otherwise as input. Assume no cache sharing between you and the delegate.
   - Time: estimate it, attended or unattended, unless the user has named a token budget or cost sensitivity. On each path, estimate wall-clock from the step's start until the step and whatever independent work you would do during the delegated wait are both accepted, counting the delay to any later step whose start would move; never the whole run.
     - Inline: your own calls, with independent tool calls batched.
     - Delegated: start-up, the work order, any pilot, the wait, collection, verification of every record, and the probability-weighted retry or takeover.
     - Credit overlap only for independent delegates running together within the harness's concurrency and rate limits, or for your own independent work during the wait, counting each overlap once. A single delegate you only wait on is never faster.
     - Take the slow end of the delegated estimate and the fast end of the inline one.

3. Delegate every candidate whose result is cheaper to check than to produce and whose delegated path either costs less and, when Time applies, finishes no later, or, when Time applies, finishes at least twice as fast and at least one minute sooner within the run's time budget. Judge a fan-out as one step covering its whole batch. Do the rest yourself. For each delegation, follow `references/dispatch.md` to pick the role, write the work order, dispatch, wait, and accept or escalate. Finish by accepting the record or taking over the step.
   - Time budget: a run is the user's current request, from its start to delivery. Its budget is your estimated inline cost of the whole run, re-estimated when the authorized scope changes. Before each time-based dispatch, charge its estimated extra cost, delegated minus inline, reserving a whole batch at once. A cheaper path that meets step 3 qualifies on tokens and is neither charged nor credited. Dispatch only while the charges fit the budget, summing decision-time estimates, never reported tokens.

4. At delivery, report every delegation in one table: role, agent type, requested and runtime-confirmed model, effort, decision basis (tokens or time), duration, and tokens. Write "not reported" where the harness gives no value, and "requested" where the runtime model is unconfirmed. Below the table, state the time budget charged against the run's inline estimate.
