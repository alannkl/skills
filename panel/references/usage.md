# Runner usage

The skill has two modes. Panel mode runs `scripts/panel.py` with one of three presets; pair mode runs `scripts/consult.py` as described under [Consultant](#consultant). Choose between them with the skill's [mode-selection rules](../SKILL.md#prepare).

## Brief and roster

The brief defines the work, deliverable and acceptance criteria, and the runner reads it as written. The host may adapt the [brief examples](brief-examples.md).

For an existing skill in either mode, follow [skill collaboration](skill-collaboration.md). The host manages interactive stages, skill loading and questions. In panel mode it supplies the chosen preset to `panel.py`; the runner does not automate the skill's stages. In pair mode the host executes those stages under the consultation and review rules in [Pair mode](../SKILL.md#pair-mode).

### Default roster

In panel mode, when the user leaves the roster unspecified, use two participants. Pair mode uses one consultant; its model choice and fallback follow the same per-harness defaults:

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

Follow the [skill's roster-confirmation step](../SKILL.md#prepare) before launch. Direct CLI calls with explicit roster files remain noninteractive.

Every opening contribution is required. Critique or clarification may skip a failed participant after confirming inactivity and reconciling the failure; that participant remains required for final approval.

## Execution boundaries

In panel mode, `execution` controls access and checks independently of the brief's subject and output format:

| Setting | Meaning |
| --- | --- |
| `workspace: "read-only"` | Default. Read frozen evidence and return a deliverable through the runner. |
| `workspace: "inspect"` | Use isolated worktrees and run commands; source edits are rejected. Scratch scripts are permitted. |
| `workspace: "edit"` | Edit separate worktrees and integrate a result for verification. |
| `web: true` | Enable web retrieval. Default is false. |
| `checks` | Commands to verify the assembled result, with expected exit codes. |
| `verification_note` | Explain the review method when working-copy verification cannot use executable checks. |

Tool approval is automatic within these boundaries; final approval requires every configured reviewer.

All workspace settings permit reading supplied evidence, including bounded read-only shell inspection when needed. Permissions expose `file_reads` rather than a blanket `shell` switch; each adapter controls native tools and sandbox enforcement, and read-only mode permits neither source edits nor general side effects.

Use Python 3.10+ on Linux or macOS, authenticated roster CLIs, and Git for `inspect` or `edit`. No Python packages are required.

## Evidence and working copies

For read-only evidence, set optional `source` to a directory of selected files; relative paths resolve against the roster file. The runner creates a read-only snapshot, or an empty evidence directory when `source` is omitted for brief-only or web work.

For repository evidence or working copies, select `repository` and an explicit `base_revision` instead of `source`:

```json
{
  "repository": "/absolute/repository",
  "base_revision": "HEAD",
  "execution": {
    "workspace": "edit",
    "checks": [["python3", "-m", "unittest", "discover", "-s", "tests"]]
  },
  "drafter": "b",
  "participants": [
    {"id": "a", "role": "member", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "effort": "high", "max_turns": 12}},
    {"id": "b", "role": "member", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL", "effort": "high"}}
  ]
}
```

The runner resolves the revision once, creates a private local clone without hardlinks or remotes, and gives participants separate worktrees at that commit. Git metadata and changes stay in the run directory.

`HEAD` includes only committed work. To review dirty work, export the exact diff and supporting files as evidence, preserving the requested scope.

Participants retain working directories across resume. Contributions are captured as patches and read-only snapshots, which peers receive after reveal; later edits cannot alter that evidence. The integrator assembles the result in its worktree. A separate verification worktree reconstructs the final patch before checks run.

Choose a new run directory outside the source, caller repository and skill package. Regular files, executable modes and internal relative symlinks are supported. Escaping symlinks, special files and uninitialized submodule entries are rejected. Git-ignored files are not patch deliverables.

Processes share an operating-system account and may inherit instructions, hooks and extensions. The runner separates edits and withholds initial peer inputs but does not enforce filesystem isolation. Use a controlled account or container for stronger isolation.

## Checks and tool permissions

Working-copy runs require `checks` or an explicit `verification_note`. Checks run against the assembled result as argument arrays, never shell strings. Expected exit defaults to zero:

```json
{
  "workspace": "inspect",
  "checks": [{"argv": ["python3", "reproduce.py"], "expect_exit": 1}]
}
```

Checks record commands, expected and actual exit codes, stdout, stderr and hashes. They must preserve reviewed source files; generated outputs stay in the verification worktree. Failed checks block agreement despite unanimous approval. Rework receives failure evidence; unresolved verification at the cap returns incomplete.

For acceptance tests participants must not edit, run a script from the immutable source snapshot against the verification working directory.

Both bundled adapters accept `model`, `effort` and an optional trusted `executable`. Claude also accepts `max_turns` and `max_budget_usd`; Codex rejects unsupported bounds. Both retain existing authentication and billing settings.

Claude uses native `auto` without interactive permission prompts. Tools follow execution settings; native policy assesses shell operations without a runner command allowlist. Declare source and check directories with `--add-dir`; add peer snapshot access after reveal and retain it on resume. Put complex or Unicode-bearing shell programs in scratch script files to avoid parsing errors. Directory grants follow [Claude permission rules](https://code.claude.com/docs/en/permissions#working-directories).

Codex uses `approval_policy="never"` with a read-only or workspace-write sandbox. Web retrieval follows explicit `execution.web` through the [documented setting](https://learn.chatgpt.com/docs/config-file/config-reference). Neither adapter uses unrestricted bypass; native denials remain visible blockers.

Claude's `max_turns` caps the agentic loop (model responses with tool calls) within one invocation and is unset by default, so a participant takes as many steps as the task needs and the idle window and discussion allowance end runaway work; its budget flag applies where the account supports it. Codex has no equivalent generation bound here. Both retain reported usage and have wall-clock limits, without a guaranteed whole-run token or monetary ceiling.

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

The discussion allowance caps unattended work. Waiting for a host decision at a round boundary pauses it and the remainder resumes afterwards. A `continue` or `brief` decision never renews it, because the runner cannot tell a person's decision from the host agent's own; only a new discussion started by `--continue` or `--reopen` starts it afresh. Elapsed time between human interventions can therefore exceed the allowance by the time spent waiting, never by autonomous work. `--unbounded` is an explicit opt-in that removes the discussion deadline: the idle bound and round cap still end stalled or looping work, but a turn that keeps writing is never killed. It is saved across follow-ups until a later `--run-seconds` restores a ceiling.

The idle window bounds stalls. A turn is killed only after that long with nothing new written under its attempt directory, which both bundled harnesses stream to as they work. Silence is sampled once per window, so a stalled turn is killed between one and two windows after its last write. Claude streams partial-message deltas, including reasoning, so a long thinking call keeps the capture growing and captures are correspondingly larger. Codex emits an event per completed item, so a long reasoning phase writes nothing, which is why its window is longer. `--idle-seconds` overrides every harness with one value and is saved like other limits.

A turn that is killed for idling or exits without a valid envelope is resumed once in the same session, with a runner notice naming the reason and asking it to finish from the work already done; the second attempt has the same idle window. Both attempts are recorded under the same turn ID, and the dispatch event carries `retry_reason`. Native permission denials and indeterminate deliveries are not retried.

Stderr reports the run directory at startup; stdout contains the final JSON report. Exit codes: 0 agreed, 1 disagreement, 2 incomplete, 130 interrupted. Startup errors return 2 with null artifact paths if no report could be created.

Both bundled harnesses stream native events to the attempt's `stdout` file while the turn runs. `python3 scripts/progress.py RUN_DIR` prints each participant's reasoning and messages from those files in turn order, headed by participant, turn and attempt. It unwraps protocol envelopes to their text, or for a review to its decision with the revision and content hash it names, and skips tool activity. By default it covers the current discussion, the turns dispatched after the latest `discussion_start` event; `--all` prints every discussion. `--follow` polls until the manifest records a finished discussion, and exits at once when the run finished before it attached. A streamed block belongs to an attempt and is provisional until the runner's `terminal_result` accepts that attempt. Claude may redact reasoning to an empty block, which prints nothing; partial-message deltas count only as activity. Other adapters' dialects are ignored. `events.jsonl` is appended and fsynced as each turn completes: a `message` event carries the contribution's full text, a `review` event the review, and `phase_end` closes a round.

Artifacts include the saved manifest, `events.jsonl`, participant prompts and native outputs, and `revisions/REVISION/` with `result.md` and `result.json`. Working-copy results add frozen files, a patch and check evidence. `report.json` is the latest answer's report; `reports/discussion-N.json` preserves each answer's reviews, verification, failures, cancellations and usage. Link the returned `discussion_report` when presenting an answer so later follow-ups cannot change its approval record. `manifest.json` records whether the conversation is active or stopped, independently of the latest answer's outcome.

The protocol envelope carries contributions or deliverables in `text` and any brief-requested JSON object in `data`, without predefined keys. Reviews use revision/hash and approve/object/unable fields. The runner builds a JSON schema for each dispatch and each harness enforces it natively, through Claude's `--json-schema` and Codex's `--output-schema`, so the outer shape of an envelope is constrained and the review schema limits the revision and hash to the candidate under review. Codex validates strictly, so its copy carries `data` as a JSON-encoded string that the adapter decodes; that string can still be invalid JSON, which makes the turn a failed attempt that one retry can recover. A pinned revision proves which candidate the response is associated with, not that the reviewer examined it: the runner still validates identity and content, and reviewers assess substance against the brief.

In `flat-peers`, the responsibilities round also carries an `integrator` nomination with an `integrator_reason`. Participants are told the `declared_drafter`; a null nomination with an empty reason keeps it, and a nomination needs a nonempty reason. Only a unanimous nomination by the required peers moves integration to that peer for the discussion, announced to everyone as a runner message with every reason; otherwise, or when a working-copy run would leave no other approver, the roster's declared drafter integrates. The roster's `drafter` stays the saved fallback across follow-ups.

Result hashes bind text and data, plus files, patch and verification for working copies. Code or data changes require fresh approval even if prose is unchanged. Each round freezes its event cutoff; directed messages affect visibility without adding turns.

## Continuing the conversation

After delivering an answer, keep the panel available and apply the [routing rule](../SKILL.md#keep-the-panel-in-the-chat). For each routed follow-up, write a file with the user's message, new decisions or evidence, the current skill stage if applicable, and the requested deliverable and acceptance criteria. Include relevant host-only exchanges since the last discussion, separating user decisions from host recommendations. Put the host's opinion under the [host view](../SKILL.md#host-view) heading. Resume the same run directory:

```bash
python3 scripts/panel.py --continue /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Supply the same `--adapter NAME=FILE` registrations for external harnesses. Pass `--idle-seconds`, `--run-seconds`, `--unbounded`, `--max-cycles` or `--report-seconds` to change the saved limits for this and later discussions; the `discussion_start` event records the limits in force, with `idle_seconds` null while each adapter's own window applies. Each `--continue` or `--reopen` starts a fresh autonomous-work allowance. The runner retains the roster, preset, models, effort, required approvers, execution settings, source snapshot, participant sessions and workspaces. It supplies prior host briefs and previously undelivered shared discussion, clears the current candidate and approvals, and runs a fresh bounded discussion. Private opening rounds withhold current opening contributions only; participants still know the earlier conversation. Every new panel result requires fresh approval of its exact revision, even when its text is unchanged.

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

### Older runs

Completed version-3 panels can be continued explicitly with their saved sessions; the runner archives their original report and upgrades continuation state to version 4. Unfinished work must be recovered first. The experimental `task` roster configuration is rejected: put objectives and result requirements in the brief, and access and check requirements in `execution`. Completed older reports remain readable; unfinished older-format runs need a new run.

## Consultant

`scripts/consult.py` runs one read-only participant while the host does the work. Pair mode uses it under the [consultation and review rules](../SKILL.md#pair-mode), keeping the session available across follow-ups.

| Command | Behavior |
| --- | --- |
| `open DIR --harness H --model M [--effort E] [--web] --brief FILE [--read DIR ...]` | Start a session and answer the brief. A fresh consultation requires a new directory. |
| `ask DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Resume the saved session. Also the retry path for a failed opening turn once the consultation exists, since a second `open` rejects that directory. Rejects closed consultations. |
| `close DIR` | Close the consultation on stop or reset. |
| `reopen DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Reopen a closed consultation and answer the new question with the saved session, model, effort and permissions. Include decisions made while stopped. |

Attachments are inlined into the question. `--read` grants directory access through Claude's `--add-dir` or Codex's read-only sandbox. Neither harness grants the consultant write capability. Register external harnesses with `--adapter NAME=FILE`, as for the panel.

A one-field schema requires each reply as text. `--timeout` defaults to 600 seconds and cancels a turn that never returns, leaving the session open. Stdout carries one JSON object with `ok`, `text` and the turn number. Exit 2 means no reply; the `error` text distinguishes a timeout, failed turn or configuration error. An unconfirmed timeout cancellation warns that the process may still be running.

`DIR/consult.json` records the harness, model, session and readable directories. `DIR/log.jsonl` records every question and reply; `DIR/turns/tN/` holds native captures.

All consultation commands take a writer lock. Before dispatch, the runner records `pending_turn` and clears the marker only after recording a determinate outcome. Active writers, missing completion records, unfinished turns and uncertain termination block asking, closing and reopening. Reconcile the saved records and confirm termination before resuming; changing the closed/open flag does not resolve these conditions.

A terminal session-loading failure starts one fresh session within the same turn timeout. It retains prior questions, captured attachments and replies as context and records `replacement` in the reply and log, with the old session under `retired_sessions` in the manifest. The original attempt stays in `turns/tN/`; the fresh attempt uses `turns/tN/fresh/`. Normal follow-ups then use the replacement session. A missing saved session ID is an incomplete record, not proof of a terminal native failure.

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

Supply the same registrations with `--recover`; recovery does not import modules named in saved output or run state. Validate the adapter's authentication, permissions and capabilities in the current environment before claiming live support; registration alone is insufficient.

## Extending the runner

Tests live in `tests/panel/`, outside the installed skill.

An adapter may return `Terminal(outcome="session_unavailable", session_id=OLD_ID, exit_status=NONZERO)` only when it can establish that a resume failed terminally while loading the saved session, before task execution. This triggers one automatic fresh start. Generic failures, timeouts, permission errors and unexpected session IDs do not qualify. The bundled adapters recognize specific missing-session diagnostics for the requested ID from Claude and Codex stderr with no stdout activity; unrecognized diagnostics remain ordinary failures.

A harness adapter provides immediate `start`/`resume` handles, an asyncio completion task returning `Terminal`, bounded asynchronous cancellation and recovery from persisted evidence. Export it through `create_adapter()` for CLI registration or pass it in the `Panel` mapping, without changing the engine. Implement automatic, noninteractive tool permissions within execution boundaries or report the unsupported capability. Runtime settings include working, scratch and attempt directories, plus explicit capabilities.

An unfamiliar subject needs a brief, not a new adapter or task type. External tools still need support and authorization in the selected harness.
