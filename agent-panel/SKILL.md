---
name: agent-panel
description: Coordinate N agents on a shared task or existing skill, with one combined result verified against its requirements.
disable-model-invocation: true
---

# Agent panel

## Prepare

1. Write a brief defining the goal, scope, evidence, deliverable and acceptance criteria. Consult [brief examples](references/brief-examples.md) when useful. For collaborative execution of an existing skill, first read that skill and [skill collaboration](references/skill-collaboration.md).
2. Read [runner usage](references/usage.md) for roster, evidence and execution settings. Use the requested preset; otherwise choose and announce one. Default interactive skills to `leader-members` with one human-facing coordinator, preserving the selected skill's mode-selection rules:
   - `independent-discussion`: independent work, reveal, critique, integration, review.
   - `leader-members`: a leader assigns complementary work and integrates contributions.
   - `flat-peers`: peers propose responsibilities and contribute; a declared integrator assembles the result.
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

The runner manages scheduling, sessions, working directories, input delivery, artifacts and final approval. Use each harness's automatic, noninteractive tool permissions within the execution boundaries; keep harness-specific flags in its adapter. Retain the process handle and relay progress from `events.jsonl`. Report missing participants or permissions as blockers and preserve the roster.

For round-by-round inspection, use `--pause-between-rounds` and send host decisions through stdin. Follow [human input and recovery](references/usage.md#human-input-and-recovery) for brief changes, cancellation and crashes. Wait for the report before claiming processes stopped.

## Finish

Read `report.json` and check the deliverable against every acceptance criterion. For another skill, also verify its completion rules and deliver its required output once for the team. Agreement on an intermediate question or proposal completes only that assignment. Deliver the requested content, data or files; include frozen files, the patch and verification evidence for file changes.

Report the outcome and artifact paths:

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval does not authorize applying changes, committing, publishing or external actions. The host may apply a patch under existing task authorization after inspecting the destination's current changes. The runner retains isolated results and leaves the caller's checkout untouched. Report that independence is procedural, without enforced filesystem isolation.
