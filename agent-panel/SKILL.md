---
name: agent-panel
description: Coordinate N agents to complete a shared task, combine their work, and verify the final result against the brief.
disable-model-invocation: true
---

# Agent panel

## Prepare

1. Write a brief defining the goal, scope, evidence, requested deliverable and acceptance criteria. The brief determines the work and the form of the result. Use [brief examples](references/brief-examples.md) when examples would help frame the request.
2. Read [runner usage](references/usage.md) to prepare the roster, evidence and execution settings. Select how the participants coordinate:
   - `independent-discussion`: independent work, reveal, critique, integration, review.
   - `leader-members`: a leader assigns complementary work and integrates contributions.
   - `flat-peers`: peers propose responsibilities, contribute, and a declared integrator assembles the result.
3. Select the requested harnesses and their adapters using [runner usage](references/usage.md). Give each participant a unique ID, role, harness and explicit model. Multiple participants may share a harness; each gets a separate session. Set the integrator through `drafter` and the required approvers, which default to everyone. Working-copy runs need a required reviewer other than the integrator.
4. Set access and checks from the authorized scope: whether agents may use the web, run commands, or change source files. Choose executable checks with expected exit codes, or explain how review will verify completion. Freeze the inputs and report the roster, source revision, deliverable and execution bounds before launching. Keep existing authentication and billing settings.

## Run

From this skill's directory:

```bash
python3 scripts/panel.py leader-members /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory --max-cycles 3 \
  --turn-seconds 180 --run-seconds 1800
```

The runner owns scheduling, separate sessions and working directories, input delivery, artifact capture and the final approval gate. Use each harness's automatic, noninteractive tool-permission mechanism within the execution boundaries. Harness-specific flags belong in its adapter. Keep the process handle available and relay progress from `events.jsonl`. Missing participants or permissions remain blockers; preserve the roster and report them.

Use `--pause-between-rounds` when the human wants to inspect each round. Send host decisions through stdin as described in [runner usage](references/usage.md). A revised brief invalidates previous approvals. SIGINT or SIGTERM cancels active agent and verification processes; wait for the report before claiming they stopped.

## Finish

Read `report.json` and inspect the actual deliverable against every acceptance criterion in the brief. Deliver the requested content, structured data or files. For file changes, include the frozen files, patch and verification evidence.

Report the outcome and artifact paths:

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval is separate from authorization to apply changes, commit, publish or perform external actions. Applying a patch to another checkout is a host operation under the existing task authorization; inspect its current changes first. The runner retains isolated results and leaves the caller's checkout untouched.

After a crash, follow the reconciliation procedure in [runner usage](references/usage.md). Report procedural independence and the absence of enforced filesystem isolation.
