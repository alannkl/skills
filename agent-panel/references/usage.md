# Runner usage

The skill has two modes. Panel mode uses `scripts/panel.py` with one of three presets; pair mode uses `scripts/consult.py` as described under [Consultant](#consultant). Follow the skill's [mode-selection rules](../SKILL.md#prepare) before choosing either path.

## Brief and roster

The brief defines the work, deliverable and acceptance criteria. The host may use [brief examples](brief-examples.md); the runner reads the brief, without a task selector, category registry or profile loader.

For an existing skill in either mode, follow [skill collaboration](skill-collaboration.md). The host manages interactive stages, skill loading and questions. In panel mode, it supplies the chosen preset to `panel.py`; the runner does not automate the skill's stages. In pair mode, the host executes those stages with the checkpoints in [Pair mode](../SKILL.md#pair-mode).

### Default roster

In panel mode, when the user leaves the roster unspecified, use two participants. Pair mode uses one consultant; its model choice and fallback follow the same per-harness defaults below:

| Harness | Preferred model | Effort |
| --- | --- | --- |
| Claude Code | Claude Fable 5.1 | `high` |
| Codex | GPT-6 Astra | `high` |

1. Preserve explicit user choices and apply task-specific model restrictions only within their stated scope. Fill unspecified models on matching harnesses from the table; default unspecified effort to `high`.
2. Resolve exact model identifiers for the installed harness and current account using current model listings or account availability evidence. Consult current official vendor guidance when identifiers or capability are unclear. If a preferred model is unavailable, choose that harness's most capable available model for general reasoning and coding. Use the same rule for other requested harnesses. Base the ranking on current model descriptions, not names or speed/cost defaults. Report fallbacks and reasons, or unresolved availability/ranking before launch; never invent an identifier.
3. Set `high` explicitly where supported. If effort control exists but lacks `high`, disclose supported choices and resolve effort before launch. Report harnesses without effort control.
4. For panel mode, assign neutral roles and the integrator to fit the preset, with both default participants required to approve. Write the resolved choices into the roster file; the runner does not discover or substitute models. Spend model capability on required approvers first; the host's session model is independent of the roster.

### Roster file

A panel roster specifies participants, coordination roles, optional evidence and execution settings. Replace the model placeholders with resolved identifiers:

```json
{
  "source": "evidence",
  "execution": {"web": true},
  "drafter": "a",
  "participants": [
    {"id": "a", "role": "member", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "effort": "high"}},
    {"id": "b", "role": "member", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL", "effort": "high"}}
  ]
}
```

Use supported effort values. IDs must be unique; `host`, `runner` and `all` are reserved. Each participant gets a separate session, even on the same harness. `required_approvers` defaults to everyone. Set `drafter`; `leader-members` also requires `leader`, who integrates instead; `flat-peers` treats `drafter` as the fallback when peers do not unanimously nominate an integrator. Working-copy runs require an approver other than the integrator.

Roles are neutral labels: `member` for every participant, and `leader` for the `leader-members` leader. The brief defines the work; the preset's opening round divides it, or keeps it whole. A role that names a viewpoint or a slice of the task prejudices that round, since the runner sends each participant its own role and the full roster in every phase, including the opening. The `drafter` designation is an editing duty.

Follow the [skill's roster-confirmation step](../SKILL.md#prepare) before launch. Direct CLI calls with explicit roster files remain noninteractive.

Every opening contribution is required. Critique or clarification may skip a failed participant after confirming inactivity and reconciling the failure. That participant remains required for final approval.

## Execution boundaries

In panel mode, `execution` controls access and checks, independently of the brief's subject:

| Setting | Meaning |
| --- | --- |
| `workspace: "read-only"` | Default. Read frozen evidence and return a deliverable through the runner. |
| `workspace: "inspect"` | Use isolated worktrees and run commands; source edits are rejected. Scratch scripts are permitted. |
| `workspace: "edit"` | Edit separate worktrees and integrate a result for verification. |
| `web: true` | Enable web retrieval. Default is false. |
| `checks` | Commands to verify the assembled result, with expected exit codes. |
| `verification_note` | Explain the review method when working-copy verification cannot use executable checks. |

Access settings are independent of task instructions and output formats. Tool approval is automatic within these boundaries; final approval requires every configured reviewer.

All workspace settings permit reading supplied evidence, including bounded read-only shell inspection when needed. Permissions expose `file_reads`, not a blanket `shell` switch. Each adapter controls native tools and sandbox enforcement; read-only mode permits neither source edits nor general side effects.

Use Python 3.10+ on Linux or macOS, authenticated roster CLIs, and Git for `inspect` or `edit`. No Python packages are required.

## Evidence and working copies

For read-only evidence, set optional `source` to a directory of selected files. Relative paths resolve against the roster file. The runner creates a read-only snapshot, or an empty evidence directory when source is omitted for brief-only or web work.

For repository evidence or working copies, select `repository` and an explicit `base_revision` instead of `source`:

```json
{
  "repository": "/absolute/repository",
  "base_revision": "HEAD",
  "execution": {
    "workspace": "edit",
    "checks": [["python3", "-m", "unittest", "discover", "-s", "tests"]]
  },
  "drafter": "a",
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

Checks record commands, expected/actual exit codes, stdout, stderr and hashes. They must preserve reviewed source files; generated outputs stay in the verification worktree. Failed checks block agreement despite unanimous approval. Rework receives failure evidence; unresolved verification at the cap returns incomplete.

For acceptance tests participants must not edit, run a script from the immutable source snapshot against the verification working directory.

Both bundled adapters accept `model`, `effort` and optional trusted `executable`. Claude also accepts `max_turns` and `max_budget_usd`; Codex rejects unsupported bounds. Both retain existing authentication and billing settings.

Claude uses native `auto` without interactive permission prompts. Tools follow execution settings; native policy assesses shell operations without a runner command allowlist. Declare source/check directories with `--add-dir`; add peer snapshot access after reveal and retain it on resume. Put complex or Unicode-bearing shell programs in scratch script files to avoid parsing errors. Directory grants follow [Claude permission rules](https://code.claude.com/docs/en/permissions#working-directories).

Codex uses `approval_policy="never"` with a read-only or workspace-write sandbox. Web retrieval follows explicit `execution.web` through the [documented setting](https://learn.chatgpt.com/docs/config-file/config-reference). Neither adapter uses unrestricted bypass; native denials remain visible blockers.

Claude defaults to eight internal turns per invocation; its budget flag applies where the account supports it. Codex has no equivalent generation bound here. Both retain reported usage and have wall-clock limits, without a guaranteed whole-run token or monetary ceiling.

## Run and inspect

```bash
python3 scripts/panel.py independent-discussion /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory
```

Defaults: three integration/review cycles, each harness's own idle window per invocation (Claude 300 seconds, Codex 600, external adapters 300 unless they declare `idle_seconds`), 300 seconds per check, and 3,600 seconds of autonomous work per discussion. Cancellation/reporting reserves ten seconds, with a five-second minimum. The round cap is the opening phase count plus three times the cycle cap, including restarts after brief changes. The discussion allowance is a ceiling on unattended work: waiting for a host decision at a round boundary pauses it and the remainder resumes afterwards, a `continue` or `brief` decision never renews it because the runner cannot tell a person's decision from the host agent's own, and only a new discussion started by `--continue` starts it afresh. Elapsed time between human interventions can therefore exceed the allowance by the time spent waiting, never by autonomous work. There is no whole-chat spending cap. `--unbounded` is an explicit opt-in that removes the discussion deadline; the idle bound and round cap still end stalled or looping work, but a turn that keeps writing is never killed, and the setting is saved across follow-ups until a later `--run-seconds` restores a ceiling. See `--help` for options. There is no cap on a turn's total time. The idle window bounds stalls: a turn is killed only after that long with nothing new written under its attempt directory, which both bundled harnesses stream to as they work. Silence is suspected inactivity, not proof of a stall, and it is sampled once per window, so a stalled turn is killed between one and two windows after its last write. Claude streams partial-message deltas, including reasoning, so a long thinking call keeps the capture growing; captures are correspondingly larger. Codex emits an event per completed item, so a long reasoning phase writes nothing, which is why its window is longer; 600 is a provisional policy, not a measured bound. `--idle-seconds` overrides every harness with one value and is saved like other limits. Checks use the explicit value, or 300, as a plain wall-clock cap.

A turn that is killed for idling or exits without a valid envelope is resumed once in the same session, with a runner notice naming the reason and asking it to finish from the work already done; the second attempt has the same idle window. Both attempts are recorded under the same turn ID, and the dispatch event carries `retry_reason`. Native permission denials and indeterminate deliveries are not retried.

Stderr reports the run directory at startup; stdout contains the final JSON report. Exit codes: 0 agreed, 1 disagreement, 2 incomplete, 130 interrupted. Startup errors return 2 with null artifact paths if no report could be created.

Both bundled harnesses stream native events to the attempt's `stdout` file while the turn runs. `python3 scripts/progress.py RUN_DIR` prints each participant's reasoning and messages from those files in turn order, headed by participant, turn and attempt, unwrapping protocol envelopes to their text or, for a review, its decision with the revision and content hash it names, and skipping tool activity. By default it covers the current discussion, the turns dispatched after the latest `discussion_start` event; `--all` prints every discussion. `--follow` polls until the manifest records a finished discussion, and exits at once when the run finished before it attached. A streamed block belongs to an attempt: it is provisional until the runner's `terminal_result` accepts that attempt. Claude may redact reasoning to an empty block, which prints nothing; partial-message deltas are ignored by the progress script and count only as activity. Other adapters' dialects are ignored. `events.jsonl` is appended and fsynced as each turn completes: a `message` event carries the contribution's full text, a `review` event the review, and `phase_end` closes a round.

Artifacts include the saved manifest, `events.jsonl`, participant prompts/native outputs, and `revisions/REVISION/` with `result.md` and `result.json`. Working-copy results add frozen files, a patch and check evidence. `report.json` is the latest answer's report; `reports/discussion-N.json` preserves each answer's reviews, verification, failures, cancellations and usage. Link the returned `discussion_report` when presenting an answer so later follow-ups cannot change its approval record. `manifest.json` records whether the conversation is active or stopped independently of the latest answer's outcome.

The protocol envelope carries contributions or deliverables in `text` and any brief-requested JSON object in `data`, without predefined keys. Reviews use revision/hash and approve/object/unable fields. The runner builds a JSON schema for each dispatch and each harness enforces it natively, through Claude's `--json-schema` and Codex's `--output-schema`, so the outer shape of an envelope is constrained and the review schema limits the revision and hash to the candidate under review. Codex validates strictly, so its copy carries `data` as a JSON-encoded string that the adapter decodes; that string can still be invalid JSON, which makes the turn a failed attempt that one retry can recover. A pinned revision proves which candidate the response is associated with, not that the reviewer examined it: the runner still validates identity and content, and reviewers assess substance against the brief.

In `flat-peers`, the responsibilities round also carries an `integrator` nomination with an `integrator_reason`. Participants are told the `declared_drafter`; a null nomination with an empty reason keeps it, and a nomination needs a nonempty reason. Only a unanimous nomination by the required peers moves integration to that peer for the discussion, announced to everyone as a runner message with every reason; otherwise, or when a working-copy run would leave no other approver, the roster's declared drafter integrates. The roster's `drafter` stays the saved fallback across follow-ups.

Result hashes bind text and data, plus files, patch and verification for working copies. Code or data changes require fresh approval even if prose is unchanged. Each round freezes its event cutoff; directed messages affect visibility without adding turns.

## Continuing the conversation

The host keeps this panel active in the current chat after delivering an answer. For each substantive follow-up, write a file containing the user's message, new decisions or evidence, the current skill stage when applicable, and the requested deliverable and acceptance criteria. Include relevant host-only exchanges since the last discussion, identifying user decisions separately from host recommendations. Put the host's own opinion under the [host view](../SKILL.md#host-view) heading. Then resume the same run directory:

```bash
python3 scripts/panel.py --continue /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Supply the same `--adapter NAME=FILE` registrations for external harnesses. Pass `--idle-seconds`, `--run-seconds`, `--unbounded`, `--max-cycles` or `--report-seconds` to change the saved limits for this and later discussions; the `discussion_start` event records the limits in force, with `idle_seconds` null while each adapter's own window applies. Each `--continue` starts a fresh autonomous-work allowance. The runner retains the roster, preset, models, effort, required approvers, execution settings, source snapshot, participant sessions and workspaces. It supplies prior host briefs and previously undelivered shared discussion, clears the current candidate and approvals, and runs a fresh bounded discussion. Private opening rounds withhold current opening contributions only; participants still know the earlier conversation. Every new answer requires fresh approval of its exact revision, even when its text is unchanged.

Use continuation for new questions, corrections and subsequent skill stages within the saved execution boundaries. The source snapshot stays pinned; include new read-only evidence in the follow-up text. A new message does not authorize broader tools or source edits. If the work requires a changed roster, preset, source or execution boundaries, explain that it needs an explicit reset and resolve authorization before starting the replacement; changed limits need no reset. Saved sessions must remain available in their original harness accounts and directories. A failed resume returns incomplete; it never silently substitutes a fresh session.

For stop or answer-solo requests while idle:

```bash
python3 scripts/panel.py --stop /absolute/panel-directory
```

This closes the conversation without invoking participants or modifying previous answers. Clear the host's active-panel record. For reset, close the old panel and use the normal new-panel command with a new run directory; record it as active. Carry context into a reset only as requested, and disclose that participants start fresh. For an explicit one-message solo exception, keep the panel saved and include any new decisions when next continuing it.

The process exits after each answer, releasing its writer lock; native sessions and panel records persist on disk. Keep the active directory and authorized settings in the host's session checkpoint so context compaction does not drop panel routing. The runner handles continuation when invoked; the host must route later chat messages to it.

Completed version-3 panels can be explicitly continued using their saved sessions. The runner archives their original report and upgrades continuation state to version 4. Unfinished work must be recovered first. Missing sessions, changed frozen evidence, unreconciled dispatches or indeterminate delivery block continuation; preserve the roster and report the gap. Resolve uncertain effects before a reset that could repeat work.

## Consultant

`scripts/consult.py` runs one read-only participant outside any panel, for a host that does the work itself; the skill's pair mode requires it at fixed checkpoints and keeps it open across chat follow-ups. `open DIR --harness H --model M [--effort E] [--web] --brief FILE [--read DIR ...]` starts the session and answers the brief; `ask DIR --question FILE [--attach FILE ...] [--read DIR ...]` resumes the same session, and is also the retry path after an `open` whose turn failed once the consultation existed, since a second `open` rejects the existing directory; `close DIR` ends it on stop or reset. Attached files are inlined into the question; `--read` directories are granted to the harness's file tools, through `--add-dir` for Claude and the read-only sandbox for Codex. The consultant has no write capability in either harness. Each turn's reply is enforced by a one-field schema, so the answer arrives as text, and `--timeout` (default 600 seconds) cancels a turn that never returns while leaving the session open. Stdout carries one JSON object with `ok`, `text` and the turn number; exit 2 means no reply, from a timeout, a failed turn or a configuration error alike, and the `error` text says which; a timeout whose cancellation is unconfirmed says the process may still be running. `DIR/consult.json` records harness, model, session and readable directories; `DIR/log.jsonl` records every question and reply; `DIR/turns/tN/` holds the native captures. `--adapter NAME=FILE` registers external harnesses as for the panel.

## Human input and recovery

With `--pause-between-rounds`, stderr announces `awaiting_host_decision`. Write one JSON line to stdin: `{"action":"continue"}`, `{"action":"stop"}`, or `{"action":"brief","text":"The full revised brief and acceptance criteria."}`.

A revised brief invalidates approvals and restarts opening rounds within the current discussion's round cap and remaining allowance; a boundary decision pauses the clock while the host is deciding and never renews it. Sessions retain history; working copies retain work. After an answer, use `--continue` for the next discussion. SIGINT/SIGTERM stops scheduling, cancels active agent and verification process groups, and closes panel routing. Reports distinguish confirmed exit from uncertain termination. Stop an active process through its retained handle; `--stop` acquires the writer lock and closes only an idle conversation.

After a crash, use `python3 scripts/panel.py --recover /absolute/run-directory`. Recovery takes the writer lock, reconciles the current discussion's persisted output/exit evidence and applies valid results once. It retains earlier reports and returns incomplete without redispatch or re-verification. An already completed discussion returns its saved report. If delivery is certain and all sessions exist, the host may explicitly continue with a follow-up that accounts for the recovered effects. A torn final append is retained as `torn-event`. Saved PIDs are never signalled because they may have been reused.

The experimental `task` configuration is no longer accepted. Put objectives and result requirements in the brief, access/check requirements in `execution`. Completed older reports remain readable; unfinished older-format runs need a new run.

## Additional harnesses

The engine uses adapter instances. Claude Code and Codex are bundled; other CLIs need adapters translating their launch, resume, permission and output conventions.

Register a trusted local adapter module without editing the runner:

```bash
python3 scripts/panel.py flat-peers /absolute/brief.md /absolute/roster.json \
  --adapter other=/absolute/other_adapter.py
```

Use `"harness": "other"` for one or more participants alongside other adapters. Repeat `--adapter NAME=FILE` to add harnesses. Names must be unique and cannot replace bundled adapters. Each module exports `create_adapter()`, returning an instance with the contract below. Modules are executable code selected by the host; participant output cannot register adapters.

Supply the same registrations with `--recover`; recovery does not import modules named in saved output or run state. Validate the adapter's authentication, permissions and capabilities in the current environment before claiming live support; registration alone is insufficient.

## Verification and extension

Tests and validation records live in `tests/agent-panel/`, outside the installed skill. Coverage includes unrelated briefs, arbitrary data, external adapters, all presets with N participants, execution boundaries, exact approval, worktree integration, recovery and cancellation.

A harness adapter provides immediate `start`/`resume` handles, an asyncio completion task returning `Terminal`, bounded asynchronous cancellation and recovery from persisted evidence. Export it through `create_adapter()` for CLI registration or pass it in the `Panel` mapping, without changing the engine. Implement automatic, noninteractive tool permissions within execution boundaries or report the unsupported capability. Runtime settings include working, scratch and attempt directories, plus explicit capabilities.

An unfamiliar subject requires a brief, not a new adapter or task type. External tools still need support and authorization in the selected harness. Comparative quality experiments remain separate from operational acceptance.
