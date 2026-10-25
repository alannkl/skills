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

2. Weigh each candidate from what you already know. Spend no calls on the weighing and never check the estimate afterward.
   - Verification: can you check the result more cheaply than you can produce it? Use an exit status, diff, count, source-linked record, or quick comparison with the evidence. Would you catch a wrong result before it matters? If not, do the step yourself.
   - Authority: does the step require the user's answer? Get it yourself. Delegate only work within existing authority.
   - Cost: estimate both paths in weighted tokens from the same start to the same end, excluding calls common to both. Use the cost inputs below. Count tokens only; wall-clock time counts only when the user set a deadline.
     - Inline: your model calls at your tier, including reasoning, and the tool calls, tool output, and intermediate reasoning left in your context.
     - Delegated: cold start-up, native or headless lean when the harness has no native subagent tool, and the delegate's calls at its tier; your dispatch, wait, collection, and verification calls; the work order and record left in your context; and the probability-weighted cost of a retry or takeover.
     - On both paths, include every later re-read of the retained context, during and after the step. Count reasoning only where you expect the harness to retain it.
     - Weight tokens by model and kind: reasoning and replies as output; cached context as cache read; new context, including cold start-up, as cache write where billed, otherwise as input. Assume no cache sharing between you and the delegate.

3. Delegate every candidate whose result is cheaper to check than to produce and whose delegated path costs less. Do the rest yourself. For each delegation, follow [Dispatch](references/dispatch.md) to pick the role, write the work order, dispatch, wait, and accept or escalate. Finish by accepting the record or taking over the step.

4. At delivery, report every delegation in one table: role, agent type, requested and runtime-confirmed model, effort, duration, and tokens. Write "not reported" where the harness gives no value, and "requested" where the runtime model is unconfirmed.

## Cost inputs

Cold start-up per spawn. For an unlisted harness, use the corresponding Codex CLI figure: native subagent or headless lean.

| Harness and agent type       | Cold start-up per spawn |
| ---------------------------- | ----------------------- |
| Claude Code, general-purpose | about 72,000 tokens     |
| Claude Code, Explore         | about 56,000 tokens     |
| Codex CLI, native subagent   | about 19,000 tokens     |
| Claude Code, headless lean   | about 10,000 tokens     |
| Codex CLI, headless lean     | about 13,000 tokens     |

Token weights, in units of one Claude Sonnet 5.5 input token. For an unlisted or unavailable model, use the listed model of the nearest tier from the same provider; if none fits, do the step inline.

| Model             | Input | Cache write | Cache read | Output |
| ----------------- | ----- | ----------- | ---------- | ------ |
| Claude Fable 5.1  | 5     | 6.25        | 0.125      | 25     |
| Claude Opus 5.5   | 2     | 2.5         | 0.1        | 10     |
| Claude Sonnet 5.5 | 1     | 1.25        | 0.1        | 5      |
| GPT-6 Astra       | 5     | 6.25        | 0.5        | 25     |
| GPT-6.1 Sol       | 1     | 1.25        | 0.05       | 5      |

## Example

Extract the configuration keys from a 30,000-token reference on Claude Code, with 20 session turns to follow. The delegate is an Explore collector on Sonnet 5.5 that reads the reference and returns a 1,500-token record; the main agent writes a 400-token work order, spot-checks 2,000 tokens of cited locations, and carries a 10% retry risk.

| Path                                                                                                                  | Main on Fable 5.1                                                            | Main on Sonnet 5.5                                                         |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Inline: read 30,000 tokens as cache write, then re-read them as cache read on 20 turns                                | 187,500 + 75,000 = 262,500                                                   | 37,500 + 60,000 = 97,500                                                   |
| Delegated: start-up, delegate read, delegate reply, then the work order, record, re-reads, spot check, and retry risk | 70,000 + 37,500 + 7,500 + 10,000 + 9,400 + 4,800 + 12,500 + 12,000 = 163,700 | 70,000 + 37,500 + 7,500 + 2,000 + 1,900 + 3,800 + 2,500 + 12,000 = 137,200 |
| Decision                                                                                                              | delegate                                                                     | inline                                                                     |

The main agent's tier decides: the same step pays on Fable and does not on Sonnet.
