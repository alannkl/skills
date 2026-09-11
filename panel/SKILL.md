---
name: panel
description: Keep N agents in the current chat, continuing their discussion across follow-ups and verifying each combined result, or one read-only consultant for second opinions while the host does the work itself.
disable-model-invocation: true
---

# Panel

Choose between two modes:

- **Pair:** the host does the work with advice from one read-only consultant.
- **Panel:** participants do the work while the host coordinates. A panel uses one of three presets: `independent-discussion`, `leader-members` or `flat-peers`.

## Keep the panel in the chat

Invocation keeps the selected pair or panel active for the current chat until the user stops it, resets it or asks to answer solo. Route subsequent substantive questions, corrections, decisions and task changes through the same saved sessions, even when the user does not repeat the skill name. The host may give acknowledgments and status directly; distinguish host comments from panel conclusions or pair advice.

Use the resolved model's short name, such as `Fable` or `Astra`, to identify each member or consultant in user-facing progress, reply headings, relayed advice and final ledgers; use the model actually selected after any fallback. If names collide, append the participant ID or a stable session label, such as `Fable a` and `Fable b`, and show the mapping in the pre-launch report.

Retain the active panel or consultation directory, resolved roster or model settings, adapter registrations, authorization and shared decisions in the session's persistent working record and any continuation handoff. At the next message, restore that record and read the saved manifest before dispatch. After context compaction, reload this skill. The selected mode stays active after each answer while waiting for the user.

For follow-ups, read [continuing the conversation](references/usage.md#continuing-the-conversation) and resume the saved panel; in pair mode, `ask` the saved consultant. Stop and answer-solo requests close the panel, or the consultation, without further participant work. Reset closes the old panel and prepares a new one with fresh sessions, retaining the old artifacts. Honor an explicitly one-message solo exception, record any resulting user decisions, and return to panel routing afterward. Reuse existing authorization; resolve changes outside it before launch. Time and cycle limits may change on a follow-up without a reset.

## Prepare

1. Write a brief defining the goal, scope, evidence, deliverable and acceptance criteria. Consult [brief examples](references/brief-examples.md) when useful. For collaborative execution of an existing skill, first read that skill and [skill collaboration](references/skill-collaboration.md).
2. Read [runner usage](references/usage.md) for roster, evidence and execution settings. Select pair or panel mode. Invoking `panel` alone defaults to [Pair mode](#pair-mode). An explicit request for a panel, a group discussion or multiple participating agents selects panel mode. Honor an explicit mode or preset choice: "pair" selects pair mode, "independent" (or "independent discussion") selects `independent-discussion`, "leader" (or "leader and members") selects `leader-members`, and "peers" (or "flat peers") selects `flat-peers`. For panel mode without a named preset, choose by how the work should be shared and announce the reason. Apply these criteria to interactive skills too, preserving the selected skill's own mode-selection rules. If no preset clearly fits better, prefer `leader-members`:
   - `independent-discussion`: duplicated work. Every participant produces the whole deliverable privately; the panel then compares competing results. Choose it when the value is whether participants converge unprompted: judgments, forecasts, designs, reviews.
   - `leader-members`: split work, decided by the leader. The leader assigns complementary parts and integrates them. Choose it when one participant should own the decomposition.
   - `flat-peers`: split work, proposed by the peers. Peers with equal authority each propose the split, then each contributes its part and the contribute round resolves overlaps; the declared drafter assembles the result unless every required peer nominates the same other peer with a reason. Choose it when the work should be divided but nobody, host included, should decide the division in advance.

   For pair mode, skip steps 3 to 5 and follow [Pair mode](#pair-mode). The remaining preparation steps apply to panel mode.
3. Resolve the requested roster or the two-participant [default roster](references/usage.md#default-roster), including model availability and effort. Assign IDs, roles, adapters, the integrator and required approvers using the [roster file rules](references/usage.md#roster-file).
4. Set authorized web, command and source-edit access. Choose checks with expected exit codes, or explain how review will verify completion. Preserve authentication and billing settings.
5. Before launching, freeze the inputs and report the source revision, deliverable, participant count, each participant's harness/model/effort/role, required approvers, preset and run limits. Confirm the roster unless the user already supplied or approved it, including effort defaults or a fallback policy. Report choices within that approval without asking again; confirm changes outside it. Freeze the resolved roster for the run. Use `--unbounded` only when the user asks for it by name.

## Run

For panel mode, run from this skill's directory:

```bash
python3 scripts/panel.py leader-members /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory --max-cycles 3 --run-seconds 3600
```

Leave `--idle-seconds` out unless one window should override every harness's own.

The runner manages scheduling, sessions, working directories, input delivery, artifacts and final approval. Use each harness's automatic, noninteractive tool permissions within the execution boundaries; keep harness-specific flags in its adapter. Report missing participants or permissions as blockers and preserve the roster.

Run the runner in the background and retain the process handle. Beside it, run `python3 scripts/progress.py RUN_DIR --follow`, which prints each participant's reasoning and messages of the current discussion as its turn produces them, headed by participant, turn and attempt, and exits when the runner records the outcome. Relay it to the chat as progress, not as transcript: one status line per turn; the substance of each completed message in a few sentences; a review decision only with the revision and attempt it carries, since a streamed block belongs to an attempt that can still fail or be retried; blockers as soon as they appear. Omit reasoning unless the user asks for it. Name the run directory once so the full transcript (`progress.py RUN_DIR --all`) is one command away. Conclusions come from the report, and the host view waits for the reveal.

For round-by-round decisions, use `--pause-between-rounds` and send host decisions through stdin. Follow [human input and recovery](references/usage.md#human-input-and-recovery) for brief changes, cancellation and crashes. Wait for the report before claiming processes stopped.

## Host view

In panel mode, the host coordinates and is not a participant: the participant count excludes it, and it runs on the chat session's model regardless of the roster. Keep the opening brief to goal, scope, evidence and criteria so opening contributions stay independent. After the reveal, the host may add its own opinion under a `Host view (non-binding)` heading, sent as a brief revision at a round boundary or inside a follow-up file. Participants treat it as evidence to challenge; approval stays with the roster. At delivery, the host may add its own dissent as a host comment, separate from the panel outcome.

## Pair mode

In pair mode the host does the task itself and keeps one read-only consultant on another harness. Unless the user names a harness or model, the consultant runs on the other harness from the host's own: a Claude Code host pairs with Codex and a Codex host with Claude Code, each on that harness's preferred model from the [default roster](references/usage.md#default-roster) (GPT-6 Astra and Claude Fable 5.1 respectively), at `high` effort, with the roster's fallback rules when that model is unavailable. Before opening, report the consultant's harness, model and effort, the directories it may read, web access and the turn timeout, reusing existing authorization and confirming only what falls outside it. Open it once per chat with a brief that states the goal, scope and acceptance criteria. Keep the consultation directory in the session's working record and keep the consultant open across follow-ups, like a panel: `ask` is pair's continuation. See [consultant usage](references/usage.md#consultant).

```bash
python3 scripts/consult.py open /absolute/consult-dir --harness codex --model MODEL --effort high \
  --brief /absolute/brief.md --read /absolute/repo
python3 scripts/consult.py ask /absolute/consult-dir --question /absolute/question.md --attach /absolute/diff.patch
```

Only a stop or reset closes it: `python3 scripts/consult.py close /absolute/consult-dir`.

Two consultations are required per task, plus any the host wants in between:

1. **Approach.** Before the host commits to a direction, whether that is the first edit, the analysis method or the review plan, send the approach and ask for objections, risks and alternatives. Done when the reply is relayed and each objection has a recorded decision.
2. **Deliverable.** Send the deliverable the host intends to deliver, with the acceptance criteria, and ask for a review. Done when the reply is relayed and each finding is fixed, or rejected with a reason. Reconsult after a material change, and once on a disputed finding before its final disposition.

Delivery is a ledger, not a third consultation: the final message lists each consultation turn of the current task by turn number, with its verdict, what the host did with each point, and every disagreement, and links `log.jsonl` in the consultation directory. A delivery whose ledger does not match those turns in the log is incomplete.

Run each `consult.py` call as a background command whose exit notifies the host, and act on that notification; a poll loop is how a reply goes unread. The turn's own `--timeout` (default 600 seconds) applies regardless, so pass a longer one for a turn that may need it. If a required consultation's turn is recorded in an open consultation but returns no usable reply, and the prior invocation is confirmed stopped, retry once through `ask` with the same question and attachments; if termination is uncertain, report the checkpoint blocked without launching another invocation. A failure before the consultation exists, such as an unknown harness or an unreadable brief, is a configuration error to fix and reopen, not a turn to retry. After a second failure of the same turn, report a failed checkpoint and leave completion pending unless the user waives it.

Relay each reply under a `Second opinion from MODEL` heading, such as `Second opinion from Fable`, separate from the host's own view, as concise advice: the points that changed or challenged the host's plan and every explicit disagreement, with the full reply available in the log; quote it verbatim only when the user asks. The consultant's advice is evidence: the host weighs it, records disagreement explicitly, and stays accountable; nothing the consultant says is approval. The consultant reads the listed directories and attachments and never edits. The user may waive the checkpoints for a task by saying so; the host may not.

## Deliver the current answer

Check the deliverable against every acceptance criterion; for a panel run, read `report.json` first, and in pair mode deliver through the ledger instead of a report. For another skill, also verify its completion rules and deliver its required output once for the team. Agreement on an intermediate question or proposal completes only that assignment. Deliver the requested content, data or files; include frozen files, the patch and verification evidence for file changes.

For a panel, link this answer's `discussion_report`, retain the active panel record, and yield for the next user message. The runner exits between discussions; no background process is needed to keep participants' saved sessions. Report a failed continuation as a blocker instead of silently answering alone or starting replacement participants.

For a panel, report the outcome and artifact paths:

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval does not authorize applying changes, committing, publishing or external actions. The host may apply a patch under existing task authorization after inspecting the destination's current changes. The runner retains isolated results and leaves the caller's checkout untouched. Report that independence is procedural, without enforced filesystem isolation.
