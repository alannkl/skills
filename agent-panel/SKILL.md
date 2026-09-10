---
name: agent-panel
description: Keep N agents in the current chat, continuing their discussion across follow-ups and verifying each combined result.
disable-model-invocation: true
---

# Agent panel

## Keep the panel in the chat

Invocation activates the panel for the current chat until the user stops it, resets it or asks to answer solo. Route subsequent substantive questions, corrections, decisions and task changes through the same panel, even when the user does not repeat the skill name. The host may give acknowledgments and status directly; distinguish host comments from panel conclusions.

Retain the active run directory, resolved roster, adapter registrations, authorization and shared decisions in the session's persistent working record and any continuation handoff. At the next message, restore that record and read the saved manifest before dispatch. After context compaction, reload this skill. A final answer completes one discussion; the panel stays active while waiting for the user.

For follow-ups, read [continuing the conversation](references/usage.md#continuing-the-conversation) and resume the saved panel. Stop and answer-solo requests close it without further participant work. Reset closes the old panel and prepares a new one with fresh sessions, retaining the old artifacts. Honor an explicitly one-message solo exception, record any resulting user decisions, and return to panel routing afterward. Reuse existing authorization; resolve changes outside it before launch.

## Prepare

1. Write a brief defining the goal, scope, evidence, deliverable and acceptance criteria. Consult [brief examples](references/brief-examples.md) when useful. For collaborative execution of an existing skill, first read that skill and [skill collaboration](references/skill-collaboration.md).
2. Read [runner usage](references/usage.md) for roster, evidence and execution settings. Use the requested preset; otherwise choose one by how the work is shared and announce it. Default interactive skills to `leader-members` with one human-facing coordinator, preserving the selected skill's mode-selection rules:
   - `independent-discussion`: duplicated work. Every participant produces the whole deliverable privately; the panel then compares competing results. Choose it when the value is whether participants converge unprompted: judgments, forecasts, designs, reviews.
   - `leader-members`: split work, decided by the leader. The leader assigns complementary parts and integrates them. Choose it when one participant should own the decomposition.
   - `flat-peers`: split work, negotiated by the peers. Identical peers propose the split, then each contributes its part; a declared integrator assembles them. Choose it when the work should be divided but nobody, host included, should decide the division in advance.
3. Resolve the requested roster or the two-participant [default roster](references/usage.md#default-roster), including model availability and effort. Assign IDs, roles, adapters, the integrator and required approvers using the [roster file rules](references/usage.md#roster-file).
4. Set authorized web, command and source-edit access. Choose checks with expected exit codes, or explain how review will verify completion. Preserve authentication and billing settings.
5. Before launching, freeze the inputs and report the source revision, deliverable, participant count, each participant's harness/model/effort/role, required approvers, preset and run limits. Confirm the roster unless the user already supplied or approved it, including effort defaults or a fallback policy. Report choices within that approval without asking again; confirm changes outside it. Freeze the resolved roster for the run.

## Run

From this skill's directory:

```bash
python3 scripts/panel.py leader-members /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory --max-cycles 3 \
  --turn-seconds 180 --run-seconds 1800
```

The runner manages scheduling, sessions, working directories, input delivery, artifacts and final approval. Use each harness's automatic, noninteractive tool permissions within the execution boundaries; keep harness-specific flags in its adapter. Report missing participants or permissions as blockers and preserve the roster.

Run the runner in the background and retain the process handle. Beside it, run `python3 scripts/progress.py RUN_DIR --follow`, which prints each participant's reasoning and messages as its turn produces them and exits when the report is written. Post each block to the chat as it lands, so the user reads the discussion as it happens instead of after the report. Relayed blocks are progress; conclusions come from the report, and the host view waits for the reveal.

For round-by-round decisions, use `--pause-between-rounds` and send host decisions through stdin. Follow [human input and recovery](references/usage.md#human-input-and-recovery) for brief changes, cancellation and crashes. Wait for the report before claiming processes stopped.

## Host view

The host coordinates and is not a participant: the participant count excludes it, and it runs on the chat session's model regardless of the roster. Keep the opening brief to goal, scope, evidence and criteria so opening contributions stay independent. After the reveal, the host may add its own opinion under a `Host view (non-binding)` heading, sent as a brief revision at a round boundary or inside a follow-up file. Participants treat it as evidence to challenge; approval stays with the roster. At delivery, the host may add its own dissent as a host comment, separate from the panel outcome.

## Deliver the current answer

Read `report.json` and check the deliverable against every acceptance criterion. For another skill, also verify its completion rules and deliver its required output once for the team. Agreement on an intermediate question or proposal completes only that assignment. Deliver the requested content, data or files; include frozen files, the patch and verification evidence for file changes.

Link this answer's `discussion_report`, retain the active panel record, and yield for the next user message. The runner exits between discussions; no background process is needed to keep participants' saved sessions. Report a failed continuation as a blocker instead of silently answering alone or starting replacement participants.

Report the outcome and artifact paths:

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval does not authorize applying changes, committing, publishing or external actions. The host may apply a patch under existing task authorization after inspecting the destination's current changes. The runner retains isolated results and leaves the caller's checkout untouched. Report that independence is procedural, without enforced filesystem isolation.
