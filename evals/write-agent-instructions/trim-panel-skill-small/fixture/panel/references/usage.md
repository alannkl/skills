# Runner usage

Panel mode runs `scripts/panel.py` with one of three presets; pair mode runs `scripts/consult.py`, described under Consultant. Choose the mode under Prepare in `SKILL.md`.

## Brief and roster

The brief defines the work, deliverable and acceptance criteria; the runner reads it as written.

For an existing skill in either mode, follow `references/skill-collaboration.md`; the host manages the skill's stages, loading and questions, and the runner does not automate them.

### Default roster

An unspecified panel roster has two participants. Pair mode has one consultant by default; Pair mode in `SKILL.md` assigns harnesses to further ones. Participants and consultants follow these per-harness defaults:

| Harness | Preferred model | Effort |
| --- | --- | --- |
| Claude Code | Claude Fable 5.1 | `high` |
| Codex | GPT-6 Astra | `high` |

1. Preserve explicit user choices and apply task-specific model restrictions only within their stated scope. Fill unspecified models on matching harnesses from the table; default unspecified effort to `high`.
2. Resolve exact model identifiers for the installed harness and current account from current model listings or account availability evidence, consulting current official vendor guidance when identifiers or capability are unclear. If a preferred model is unavailable, choose that harness's most capable available model for general reasoning and coding, ranked by current model descriptions rather than names or speed/cost defaults; apply the same rule to other requested harnesses. Report fallbacks and reasons, or unresolved availability or ranking, before launch; never invent an identifier.
3. Set `high` explicitly where supported. If effort control exists but lacks `high`, disclose the supported choices and resolve effort before launch. Report harnesses without effort control.
4. For panel mode, assign neutral roles and the integrator to fit the preset, with both default participants required to approve. Write the resolved choices into the roster file; the runner does not discover or substitute models. Spend model capability on required approvers first; the host's session model is independent of the roster.

### Default drafter

Unless the user specifies a drafter, choose from the resolved roster in this order: **Codex > Claude Code**, breaking ties within a harness by roster order. If neither is present, choose a participant suited to the deliverable and report the choice. This preference selects among existing participants; it does not add or replace models.

Write the selected participant ID into `drafter`. The preset rules still apply: `leader-members` uses its assigned leader to integrate, and `flat-peers` may unanimously nominate another integrator.

### Roster file

A panel roster specifies participants, coordination roles, optional evidence and execution settings. Replace the model placeholders with resolved identifiers:

```json
{
  "source": "evidence",
  "execution": {"web": true},
  "drafter": "b",
  "participants": [
    {"id": "a", "role": "member", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "effort": "high"}},
    {"id": "b", "role": "member", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL", "effort": "high"}}
  ]
}
```

Use supported effort values. IDs must be unique; `host`, `runner` and `all` are reserved. Each participant gets a separate session, even on the same harness. `required_approvers` defaults to everyone. Set `drafter`; `leader-members` also requires `leader`, who integrates instead, and `flat-peers` treats `drafter` as the fallback when peers do not unanimously nominate an integrator. Working-copy runs require an approver other than the integrator.

Roles are neutral labels: `member` for every participant, and `leader` for the `leader-members` leader. The brief defines the work; the preset's opening round divides it, or keeps it whole. A role that names a viewpoint or a slice of the task prejudices that round, since the runner sends each participant its own role and the full roster in every phase, including the opening. The `drafter` designation is an editing duty.

Direct CLI calls with explicit roster files are noninteractive.

Every opening contribution is required. Critique or clarification may skip a failed participant after confirming inactivity and reconciling the failure; that participant remains required for final approval.

## Execution boundaries

In panel mode, `execution` declares what participants may change and how results are checked, independently of the brief's subject and output format:

| Setting | Meaning |
| --- | --- |
| `workspace: "read-only"` | Default. Read frozen evidence and return a deliverable through the runner. |
| `workspace: "inspect"` | Use isolated worktrees and run commands; source edits are rejected. Scratch scripts are permitted. |
| `workspace: "edit"` | Edit separate worktrees and integrate a result for verification. |
| `web: false` | Disable web retrieval, which is on by default. |
| `checks` | Commands to verify the assembled result, with expected exit codes. |
| `verification_note` | Explain the review method when working-copy verification cannot use executable checks. |

Use Python 3.10+ on Linux or macOS, authenticated roster CLIs, and Git for `inspect` or `edit`. No Python packages are required.

## Evidence and working copies

For read-only evidence, set optional `source` to a directory of selected files; relative paths resolve against the roster file. The runner creates a read-only snapshot, or an empty evidence directory when `source` is omitted for brief-only or web work.

For repository evidence or working copies, select `repository` and an explicit `base_revision` instead of `source`.

Choose a new run directory outside the source, caller repository and skill package. Regular files, executable modes and internal relative symlinks are supported. Escaping symlinks, special files and uninitialized submodule entries are rejected. Git-ignored files are not patch deliverables.

Processes share an operating-system account and may inherit instructions, hooks and extensions. The runner separates edits and withholds initial peer inputs but does not enforce filesystem isolation. Use a controlled account or container for stronger isolation.

## Run and inspect

```bash
python3 scripts/panel.py independent-discussion /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory
```

See `--help` for options. Defaults:

| Limit | Default | Flag |
| --- | --- | --- |
| Integration/review cycles per discussion | 3 | `--max-cycles` |
| Autonomous work per discussion | 3,600 seconds | `--run-seconds`, or `--unbounded` to remove it |
| Idle window per invocation | each harness's own: Claude 300 seconds, Codex 600, external adapters 300 unless they declare `idle_seconds` | `--idle-seconds` |
| Wall-clock cap per check | 300 seconds, or the explicit `--idle-seconds` value | `--idle-seconds` |
| Cancellation and reporting reserve | 10 seconds, 5 minimum | `--report-seconds` |

The round cap is the opening phase count plus three times the cycle cap, including restarts after brief changes. There is no whole-chat spending cap and no cap on a turn's total time.

Stderr reports the run directory at startup; stdout contains the final JSON report. Exit codes: 0 agreed, 1 disagreement, 2 incomplete, 130 interrupted. Startup errors return 2 with null artifact paths if no report could be created.

Artifacts include the saved manifest, `events.jsonl`, participant prompts and native outputs, and `revisions/REVISION/` with `result.md` and `result.json`. Working-copy results add frozen files, a patch and check evidence. `report.json` is the latest answer's report; `reports/discussion-N.json` preserves each answer's reviews, verification, failures, cancellations and usage. Link the returned `discussion_report` when presenting an answer so later follow-ups cannot change its approval record. `manifest.json` records whether the conversation is active or stopped, independently of the latest answer's outcome.

## Continuing the conversation

After delivering an answer, keep the panel available and apply the routing rule under Keep the panel in the chat in `SKILL.md`. For each routed follow-up, write a file with the user's message, new decisions or evidence, the current skill stage if applicable, and the requested deliverable and acceptance criteria. Include relevant host-only exchanges since the last discussion, separating user decisions from host recommendations. Resume the same run directory:

```bash
python3 scripts/panel.py --continue /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Add `--fresh-sessions` to start new native sessions instead of resuming. Each participant then receives the new brief and a history file in its own scratch directory holding the earlier briefs and the earlier discussion visible to it, which it reads as the task needs; nothing earlier is inlined. Sessions stay retired, the report lists them under `session_replacements`, and later follow-ups resume the new sessions. Put every decision the next answer depends on in the follow-up file, since fresh sessions keep no unrecorded context.

Supply the same `--adapter NAME=FILE` registrations for external harnesses. Pass `--idle-seconds`, `--run-seconds`, `--unbounded`, `--max-cycles` or `--report-seconds` to change the saved limits for this and later discussions; the `discussion_start` event records the limits in force, with `idle_seconds` null while each adapter's own window applies. Each `--continue` or `--reopen` starts a fresh autonomous-work allowance. The runner retains the roster, preset, models, effort, required approvers, execution settings, source snapshot, workspaces and, unless `--fresh-sessions` is passed, participant sessions. It supplies prior host briefs and previously undelivered shared discussion, clears the current candidate and approvals, and runs a fresh bounded discussion. Private opening rounds withhold current opening contributions only; participants still know the earlier conversation. Every new panel result requires fresh approval of its exact revision, even when its text is unchanged.

Continue within the saved execution boundaries. The source snapshot stays pinned; include new read-only evidence in the follow-up text. A new message does not authorize broader tools or source edits. Changes to the roster, preset, source or execution boundaries require an explicit reset; explain this and resolve authorization before starting the replacement. Changed limits need no reset.

The runner first resumes saved sessions in their original harness accounts and directories. A definitive terminal session-loading failure starts one fresh session automatically with the same role, settings, permissions and workspace. The replacement receives recorded briefs and the history visible to that participant, but not unrecorded native-session context. Other failures, including transient errors, permission denials and uncertain termination, do not trigger replacement. Relay any `session_replacements` listed in the report.

For stop or answer-solo requests while idle:

```bash
python3 scripts/panel.py --stop /absolute/panel-directory
```

This closes the conversation without invoking participants or modifying previous answers. Clear the host's active-panel routing but retain its directory and saved settings for an explicit reopen request:

```bash
python3 scripts/panel.py --reopen /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Reopening runs the same checks as continuation, preserves prior reports and requires fresh approval of the new result. Use `--continue` while active and `--reopen` after stopping; neither changes the roster or execution permissions, and both accept the same limit overrides and adapter registrations. For a reset, close the old panel and use the normal new-panel command with a new run directory; record it as active. Carry context into a reset only as requested, and disclose that participants start fresh. For an explicit one-message solo exception, keep the panel saved and include any new decisions when next continuing it.

The process exits after each answer, releasing its writer lock; native sessions and panel records persist on disk. Missing saved session IDs, changed frozen evidence, unreconciled dispatches or indeterminate delivery block continuation and reopening; preserve the roster and report the gap. Resolve uncertain effects before a reset that could repeat work.

## Consultant

`scripts/consult.py` runs one read-only participant per directory while the host does the work. Pair mode opens one directory per consultant under the Pair mode consultation and review rules in `SKILL.md`, keeping each session available across follow-ups.

| Command | Behavior |
| --- | --- |
| `open DIR --harness H --model M [--effort E] [--web \| --no-web] --brief FILE [--read DIR ...]` | Start a session and answer the brief. Web retrieval defaults to enabled; `--no-web` disables it. A fresh consultation requires a new directory. |
| `ask DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Resume the saved session. Also the retry path for a failed opening turn once the consultation exists, since a second `open` rejects that directory. Rejects closed consultations. |
| `close DIR` | Close the consultation on stop or reset. |
| `reopen DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Reopen a closed consultation and answer the new question with the saved session, model, effort and permissions. Include decisions made while stopped. |

Attachments are inlined into the question. `--read` grants directory access through Claude's `--add-dir` or Codex's read-only sandbox. Neither harness grants the consultant write capability. Register external harnesses with `--adapter NAME=FILE`, as for the panel.

A one-field schema requires each reply as text. `--timeout` defaults to 600 seconds and cancels a turn that never returns, leaving the session open. Stdout carries one JSON object with `ok`, `text` and the turn number. Exit 2 means no reply; the `error` text distinguishes a timeout, failed turn or configuration error. An unconfirmed timeout cancellation warns that the process may still be running.

`DIR/consult.json` records the harness, model, session and readable directories. `DIR/log.jsonl` records every question and reply; `DIR/turns/tN/` holds native captures.

## Human input and recovery

With `--pause-between-rounds`, stderr announces `awaiting_host_decision`. Write one JSON line to stdin: `{"action":"continue"}`, `{"action":"stop"}`, or `{"action":"brief","text":"The full revised brief and acceptance criteria."}`.

A revised brief invalidates approvals and restarts opening rounds within the current discussion's round cap and remaining allowance; a boundary decision pauses the clock while the host is deciding and never renews it. Sessions retain history; working copies retain work. After an answer, use `--continue` for the next discussion, or `--reopen` if the conversation was stopped. SIGINT/SIGTERM stops scheduling, cancels active agent and verification process groups, and closes panel routing. Reports distinguish confirmed exit from uncertain termination. Stop an active process through its retained handle; `--stop` acquires the writer lock and closes only an idle conversation.

After a crash, use `python3 scripts/panel.py --recover /absolute/run-directory`. Recovery takes the writer lock, reconciles the current discussion's persisted output and exit evidence, and applies valid results once. It retains earlier reports and returns incomplete without redispatch or re-verification. An already completed discussion returns its saved report. If delivery is certain and all sessions exist, the host may continue, or explicitly reopen a stopped conversation, with a follow-up that accounts for the recovered effects. A torn final append is retained as `torn-event`. Saved PIDs are never signalled because they may have been reused.

## Additional harnesses

The engine uses adapter instances. Claude Code and Codex are bundled; other CLIs need adapters translating their launch, resume, permission and output conventions.

Register a trusted local adapter module without editing the runner:

```bash
python3 scripts/panel.py flat-peers /absolute/brief.md /absolute/roster.json \
  --adapter other=/absolute/other_adapter.py
```

Use `"harness": "other"` for one or more participants alongside other adapters. Repeat `--adapter NAME=FILE` to add harnesses. Names must be unique and cannot replace bundled adapters. Each module exports `create_adapter()`, returning an instance with the contract below. Modules are executable code selected by the host; participant output cannot register adapters.
