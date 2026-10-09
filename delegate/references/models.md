# Model tiers and cost inputs

Opinionated working preferences as of 2026-10-07, not benchmark results. When the supported models change, review the tier placements against observed results on each role's tasks, update the defaults, fallback order and the cost weights under Cost inputs, then refresh the date. A model's name alone does not establish its tier.

## Capability tiers

| Harness | Frontier | Strong | Routine |
| --- | --- | --- | --- |
| Claude Code | Claude Fable 5.1 | Claude Opus 5.5 | Claude Sonnet 5.5 |
| Codex | GPT-6 Astra | GPT-6.1 Sol | No separate default |
| Cursor | No default | Grok 4.7 High; Grok 4.7 Medium | Composer 2.5 |

Routine covers bounded retrieval and specified procedures. Strong covers general work and synthesis that preserves qualifications and relationships between supplied facts. Frontier covers demanding work that stays within the role's scope and cheap to verify. A stronger model does not expand a role's authority or replace the host's acceptance check.

Rank choices within the active harness; a shared tier does not make two harnesses' models interchangeable. Codex has no cheaper model, so GPT-6.1 Sol also takes routine work.

## Role defaults

| Role | Claude Code selector and expected model | Codex model and effort | Cursor model selector |
| --- | --- | --- | --- |
| `collector` | `sonnet`, expect `claude-sonnet-5-5` | `gpt-6.1-sol`, `low` | `composer-2.5` |
| `runner` | `sonnet`, expect `claude-sonnet-5-5` | `gpt-6.1-sol`, `low` | `grok-4.7-medium` |
| `digester` | `opus`, expect `claude-opus-5-5` | `gpt-6.1-sol`, `medium` | `grok-4.7-high` |

Pass the effort where supported. Claude Code's native Agent tool inherits the session's effort unless a custom agent definition sets one; estimate and record that inherited effort. For headless Claude Code, use `low` for collectors and runners and `medium` for digesters.

Cursor encodes Grok's effort in the model ID; pass the listed selector to its CLI's `--model`. Composer 2.5 has no separate effort setting. When availability changes, refresh Cursor selectors with `agent --list-models`, outside the per-candidate cost estimate.

Start with the role default: a suitable starting choice, not a minimum. For harder synthesis within the same scope, a stronger listed model or higher supported effort is fine while the result stays cheap to check and the revised estimate still favors delegation. A demonstrated reasoning failure follows Escalate by cause in `references/dispatch.md`, which returns the step to the host.

## Availability fallbacks

Honor the user's explicit model and effort choices; fall back only within the flexibility they allow. A model is available when the active tool exposes it or the installed CLI is known to support it. A native tool with fixed selectors offers only those selectors, whatever its CLI supports. Stay on the active harness: unavailability alone never justifies moving to another.

When the role default is unavailable:

1. From the same harness's roster, choose the available model you already judge sufficient for the task with the lowest expected total cost, verification and retry risk included. A lower tier qualifies when known task requirements support it; record that reason. Judge from existing context, without exploratory calls.
2. If suitability is uncertain, try the higher populated capability tiers, nearest first. On Cursor the order is Composer 2.5, Grok 4.7 Medium, then Grok 4.7 High, continuing after the unavailable model.
3. If the chain reaches the host's own model, stop and do the step inline, reporting it as inline because the fallback reached the host model. Match model identity, not tier: aliases, context-window suffixes and effort variants count as the same model, so Grok 4.7 Medium and High match. Use the host's runtime-confirmed model, or its requested model if unconfirmed. This stop applies only to fallbacks; the initial role-default dispatch uses the ordinary cost comparison.
4. Before dispatch, rerun the cost comparison with the fallback's weights. If no selectable choice still pays, do the step inline.

The fallback keeps the role's capability limits and, where separately selectable, its effort; on Cursor, the fallback's selector sets the effort. For frontier fallbacks, expect `claude-fable-5-1` or `gpt-6-astra`; pass that exact ID where the tool accepts it, otherwise an exposed selector for that model.

## Cost inputs

Cold start-up per spawn. For an unlisted harness, use the corresponding Codex CLI figure: native subagent or headless lean.

| Harness and agent type       | Cold start-up per spawn |
| ---------------------------- | ----------------------- |
| Claude Code, general-purpose | about 72,000 tokens     |
| Claude Code, Explore         | about 56,000 tokens     |
| Codex CLI, native subagent   | about 19,000 tokens     |
| Claude Code, headless lean   | about 10,000 tokens     |
| Codex CLI, headless lean     | about 13,000 tokens     |

Token weights, in units of one Claude Sonnet 5.5 input token. Use the selected model's known rates, including after a fallback.

| Model             | Input | Cache write | Cache read | Output |
| ----------------- | ----- | ----------- | ---------- | ------ |
| Claude Fable 5.1  | 5     | 6.25        | 0.125      | 25     |
| Claude Opus 5.5   | 2     | 2.5         | 0.1        | 10     |
| Claude Sonnet 5.5 | 1     | 1.25        | 0.1        | 5      |
| GPT-6 Astra       | 5     | 6.25        | 0.5        | 25     |
| GPT-6.1 Sol       | 1     | 1.25        | 0.05       | 5      |
| Composer 2.5      | 0.25  | —           | 0.1        | 1.25   |
| Grok 4.7          | 1     | —           | 0.25       | 3      |

A dash in cache write means bill new context at the input weight. The Grok 4.7 row covers `grok-4.7-low`, `grok-4.7-medium`, `grok-4.7-high`, and `grok-4.7-xhigh`; double it when input exceeds 256k tokens, up to 500k.

Estimate each unknown rate from the model's capability tier with the table below, rather than doing the step inline only because a rate is unknown. Mark estimated rates in the dispatch record. Each row is the Sonnet 5.5 weights times the tier's multiplier. These are estimation weights, not provider prices; effort changes the expected token count, not the multiplier.

| Tier     | Multiplier | Input | Cache write | Cache read | Output |
| -------- | ---------- | ----- | ----------- | ---------- | ------ |
| Frontier | 4          | 4     | 5           | 0.4        | 20     |
| Strong   | 2          | 2     | 2.5         | 0.2        | 10     |
| Routine  | 1          | 1     | 1.25        | 0.1        | 5      |

## Example

Extract the configuration keys from a 30,000-token reference on Claude Code, with 20 session turns to follow. The delegate is an Explore collector on Sonnet 5.5 that reads the reference and returns a 1,500-token record; the main agent writes a 400-token work order, spot-checks 2,000 tokens of cited locations, and carries a 10% retry risk.

| Path                                                                                                                  | Main on Fable 5.1                                                            | Main on Sonnet 5.5                                                         |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Inline: read 30,000 tokens as cache write, then re-read them as cache read on 20 turns                                | 187,500 + 75,000 = 262,500                                                   | 37,500 + 60,000 = 97,500                                                   |
| Delegated: start-up, delegate read, delegate reply, then the work order, record, re-reads, spot check, and retry risk | 70,000 + 37,500 + 7,500 + 10,000 + 9,400 + 4,800 + 12,500 + 12,000 = 163,700 | 70,000 + 37,500 + 7,500 + 2,000 + 1,900 + 3,800 + 2,500 + 12,000 = 137,200 |
| Decision                                                                                                              | delegate                                                                     | inline                                                                     |

The main agent's tier decides: the same step pays on Fable and does not on Sonnet.
