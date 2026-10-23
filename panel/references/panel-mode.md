# Panel mode

Participants do the work through `scripts/panel.py` while the host coordinates.

## Presets

Without a named preset, choose by how the work should be shared, announce the reason, and prefer `leader-members` when none clearly fits better.

- `independent-discussion`: duplicated work. Each participant privately produces the whole deliverable, then the panel compares the results. Choose it when the value is whether participants converge unprompted: judgments, forecasts, designs, reviews.
- `leader-members`: split work, decided by the leader, who assigns complementary parts and integrates them. Choose it when one participant should own the decomposition.
- `flat-peers`: split work, proposed by the peers. Peers with equal authority each propose the split, then contribute their parts, resolving overlaps in the contribute round; the declared drafter assembles the result unless every required peer nominates the same other peer with a reason. Choose it when the work should be divided but nobody, host included, should decide the division in advance.

## Prepare

The runner reads the brief as written.

1. Resolve the requested or default roster under Default roster in `SKILL.md`. Assign neutral roles and the integrator to fit the preset, with both default participants required to approve; choose an unspecified drafter under Default drafter; and assign IDs, adapters and required approvers under Roster file. Write the resolved choices into the roster file; the runner does not discover or substitute models. Spend model capability on required approvers first.
2. Set authorized web, command and source-edit access under Execution boundaries. Choose checks with expected exit codes, or explain how review will verify completion. Preserve authentication and billing settings.
3. Freeze the inputs and the resolved roster, then report the source revision, deliverable, participant count, each participant's harness, model, effort and role, required approvers, preset and run limits. Confirm the roster, including effort defaults or a fallback policy, unless the user already supplied or approved it; report choices within that approval without asking again and confirm changes outside it. Use `--unbounded` only when the user asks for it by name.

### Default drafter

Unless the user specifies a drafter, write into `drafter` the ID of the first Codex participant in roster order, or else the first Claude Code participant. If neither is present, choose a participant suited to the deliverable and report the choice. This preference selects among existing participants; it does not add or replace models.

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

IDs must be unique; `host`, `runner` and `all` are reserved. Each participant gets a separate session, even on the same harness. `required_approvers` defaults to everyone. Set `drafter`; `leader-members` also requires `leader`, who integrates instead, and `flat-peers` treats `drafter` as the fallback when peers do not unanimously nominate an integrator. Working-copy runs require an approver other than the integrator.

Roles are neutral labels: `member` for every participant, and `leader` for the `leader-members` leader. The preset's opening round divides the work or keeps it whole; a role that names a viewpoint or a slice of the task prejudices that round, since the runner sends each participant its own role and the full roster in every phase, including the opening. The `drafter` designation is an editing duty.

Direct CLI calls with explicit roster files are noninteractive.

Every opening contribution is required. Critique or clarification may skip a failed participant after confirming inactivity and reconciling the failure; that participant remains required for final approval.

## Run

Run from this skill's directory:

```bash
python3 scripts/panel.py leader-members /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory --max-cycles 3 --run-seconds 3600
```

Leave `--idle-seconds` out unless one window should override every harness's own. See Limits and artifacts for defaults.

The runner manages scheduling, sessions, working directories, tool permissions, input delivery, artifacts and final approval. Report missing participants or permissions as blockers and preserve the roster.

Run the runner in the background and retain the process handle. Beside it, run `python3 scripts/progress.py RUN_DIR --follow` and relay its output as progress, not transcript: one status line per turn; the substance of each completed message in a few sentences; a review decision only with the revision and attempt it carries, since a streamed attempt can still fail or be retried; blockers as soon as they appear; reasoning only when the user asks. Name the run directory once so the full transcript (`progress.py RUN_DIR --all`) is one command away. Conclusions come from the report, and the host view waits for the reveal.

For round-by-round decisions, use `--pause-between-rounds` and send host decisions through stdin. Follow Human input and recovery for brief changes, cancellation and crashes. Wait for the report before claiming processes stopped.

## Host view

During a routed panel assignment, the host coordinates and is not a participant: the participant count excludes it, and the roster does not set its model. Keep the opening brief to goal, scope, evidence and criteria so opening contributions stay independent. After the reveal, the host may add its own opinion under a `Host view (non-binding)` heading, sent as a brief revision at a round boundary or inside a follow-up file. Participants treat it as evidence to challenge; approval stays with the roster. At delivery, the host may add its own dissent as a host comment, separate from the panel outcome.

## Deliver

Read `report.json` first. Report the outcome and artifact paths, link this answer's `discussion_report`, retain the active panel record and yield for the next user message. Report unresolved continuation failures as blockers instead of silently answering alone.

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval does not authorize applying changes, committing, publishing or external actions. The runner leaves the caller's checkout untouched; the host may apply a patch under existing task authorization after inspecting the destination's current changes. Report that independence is procedural, without enforced filesystem isolation.

## Execution boundaries

`execution` declares what participants may change and how results are checked, independently of the brief's subject and output format:

| Setting | Meaning |
| --- | --- |
| `workspace: "read-only"` | Default. Read frozen evidence and return a deliverable through the runner. |
| `workspace: "inspect"` | Use isolated worktrees and run commands; source edits are rejected. Scratch scripts are permitted. |
| `workspace: "edit"` | Edit separate worktrees and integrate a result for verification. |
| `web: false` | Disable web retrieval, which is on by default. |
| `checks` | Commands to verify the assembled result, with expected exit codes. |
| `verification_note` | Explain the review method when working-copy verification cannot use executable checks. |

Participants get their harness's full tool set in every mode, including shell, file writes, skills and subagents, with automatic approval; final approval requires every configured reviewer. Their prompt directs them to apply the `delegate` skill when it is installed, and otherwise to delegate a bounded step when its result is cheaper to check than to produce, while making their contribution and any review decision themselves. The workspace setting is declared intent the participant follows, not a tool restriction. The runner enforces what it can check: the frozen source snapshot is read-only on disk and a changed snapshot ends the run incomplete, and an `inspect` round that leaves a source patch ends incomplete. In read-only runs, participants write scratch files in their artifact directory.

`inspect` and `edit` need Git.

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

Participants retain working directories across resume. Contributions are captured as patches and read-only snapshots, which peers receive after reveal; later edits cannot alter that evidence. The integrator assembles the result in its worktree, and a separate verification worktree reconstructs the final patch before checks run.

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

Both bundled adapters accept `model`, `effort` and an optional trusted `executable`. Claude also accepts `max_turns`, `max_budget_usd` and `prompt_cache_ttl` (`5m` or `1h`), which sets `CLAUDE_CODE_PROMPT_CACHE_TTL` for that participant's process only. `FORCE_PROMPT_CACHING_5M` in the runner's environment overrides it, and the adapter then prints a warning to stderr; a one-hour cache costs more to write and pays off when a participant's turns are more than five minutes apart. Codex rejects unsupported bounds. Both retain existing authentication and billing settings.

Claude uses native `auto` without interactive permission prompts and no `--tools` restriction; `web: false` disallows the web tools. Subagents inherit the participant's tool set. Native policy assesses shell operations without a runner command allowlist. Consultants keep a read-only set: file reads, skills, subagents and web when enabled. Declare source and check directories with `--add-dir`; add peer snapshot access after reveal and retain it on resume. The adapter also grants `~/.claude/skills` and `~/.agents/skills` where they exist, so participants, consultants and their subagents can read installed skills, such as `delegate` and `constitution`, and their reference files. Put complex or Unicode-bearing shell programs in scratch script files to avoid parsing errors. Directory grants follow [Claude permission rules](https://code.claude.com/docs/en/permissions#working-directories).

Codex uses `approval_policy="never"` with a workspace-write sandbox whose writable roots add the participant's scratch directory; consultants run read-only. Codex discovers user-level skills in `~/.agents/skills` and `~/.codex/skills` itself, and both sandboxes read files outside the working directory, so installed skills and their reference files need no extra grant. Web retrieval follows `execution.web` through the [documented setting](https://learn.chatgpt.com/docs/config-file/config-reference). Neither adapter uses unrestricted bypass; native denials remain visible blockers.

Claude's `max_turns` caps the agentic loop (model responses with tool calls) within one invocation. It is unset by default, so a participant takes as many steps as the task needs, and the idle window and discussion allowance end runaway work. Its budget flag applies where the account supports it. Codex has no equivalent generation bound here. Both retain reported usage and have wall-clock limits, without a guaranteed whole-run token or monetary ceiling.

## Limits and artifacts

See `--help` for options. Defaults:

| Limit | Default | Flag |
| --- | --- | --- |
| Integration/review cycles per discussion | 3 | `--max-cycles` |
| Autonomous work per discussion | 3,600 seconds | `--run-seconds`, or `--unbounded` to remove it |
| Idle window per invocation | each harness's own: Claude 300 seconds, Codex 600, external adapters 300 unless they declare `idle_seconds` | `--idle-seconds` |
| Wall-clock cap per check | 300 seconds, or the explicit `--idle-seconds` value | `--idle-seconds` |
| Cancellation and reporting reserve | 10 seconds, 5 minimum | `--report-seconds` |

The round cap is the opening phase count plus three times the cycle cap, including restarts after brief changes. There is no whole-chat spending cap and no cap on a turn's total time.

The discussion allowance caps unattended work. Waiting for a host decision at a round boundary pauses it, and the remainder resumes afterwards. A `continue` or `brief` decision never renews it, because the runner cannot tell a person's decision from the host agent's own; only a new discussion started by `--continue` or `--reopen` starts it afresh. Time between human interventions can therefore exceed the allowance only by the time spent waiting, never by autonomous work. `--unbounded` is an explicit opt-in that removes the discussion deadline: the idle bound and round cap still end stalled or looping work, but a turn that keeps writing is never killed. It is saved across follow-ups until a later `--run-seconds` restores a ceiling.

The idle window bounds stalls: a turn is killed only after that long with nothing new written under its attempt directory, which both bundled harnesses stream to as they work. Silence is sampled once per window, so a stalled turn is killed one to two windows after its last write. Claude streams partial-message deltas, including reasoning, so a long thinking call keeps the capture growing and captures are larger. Codex emits an event per completed item, so a long reasoning phase writes nothing; its window is longer for that reason. A subagent streams only its finished messages, so its parent can fall silent during one long subagent response; while a Claude participant has a subagent call without a result, silence may last four windows before the turn is killed. `--idle-seconds` overrides every harness with one value and is saved like other limits.

A turn that is killed for idling or exits without a valid envelope is resumed once in the same session, with a runner notice naming the reason and asking it to finish from the work already done; the second attempt has the same idle window. Both attempts are recorded under the same turn ID, and the dispatch event carries `retry_reason`. Native permission denials and indeterminate deliveries are not retried.

Stderr reports the run directory at startup; stdout contains the final JSON report. Exit codes: 0 agreed, 1 disagreement, 2 incomplete, 130 interrupted. Startup errors return 2 with null artifact paths if no report could be created.

Both bundled harnesses stream native events to the attempt's `stdout` file while the turn runs. `python3 scripts/progress.py RUN_DIR` prints each participant's reasoning and messages from those files in turn order, headed by participant, turn and attempt. It unwraps protocol envelopes to their text, or for a review to its decision with the revision and content hash it names, and skips tool activity. By default it covers the current discussion, the turns dispatched after the latest `discussion_start` event; `--all` prints every discussion. `--follow` polls until the manifest records a finished discussion, and exits at once when the run finished before it attached. A streamed block belongs to an attempt and is provisional until the runner's `terminal_result` accepts that attempt. Claude may redact reasoning to an empty block, which prints nothing; partial-message deltas count only as activity. Other adapters' dialects are ignored. `events.jsonl` is appended and fsynced as each turn completes: a `message` event carries the contribution's full text, a `review` event the review, and `phase_end` closes a round.

Artifacts include the saved manifest, `events.jsonl`, participant prompts and native outputs, and `revisions/REVISION/` with `result.md` and `result.json`. Working-copy results add frozen files, a patch and check evidence. `report.json` is the latest answer's report; `reports/discussion-N.json` preserves each answer's reviews, verification, failures, cancellations and usage. Link the returned `discussion_report` when presenting an answer so later follow-ups cannot change its approval record. `manifest.json` records whether the conversation is active or stopped, independently of the latest answer's outcome.

The protocol envelope carries contributions or deliverables in `text` and any brief-requested JSON object in `data`, without predefined keys. Reviews use revision/hash and approve/object/unable fields. The runner builds a JSON schema for each dispatch, which each harness enforces natively through Claude's `--json-schema` and Codex's `--output-schema`; it constrains the envelope's outer shape, and the review schema limits the revision and hash to the candidate under review. Codex validates strictly, so its copy carries `data` as a JSON-encoded string that the adapter decodes; invalid JSON there fails the attempt, which one retry can recover. A pinned revision proves which candidate the response is associated with, not that the reviewer examined it: the runner still validates identity and content, and reviewers assess substance against the brief.

In `flat-peers`, the responsibilities round also carries an `integrator` nomination with an `integrator_reason`. Participants are told the `declared_drafter`; a null nomination with an empty reason keeps it, and a nomination needs a nonempty reason. Only a unanimous nomination by the required peers moves integration to that peer for the discussion, announced to everyone as a runner message with every reason; otherwise, or when a working-copy run would leave no other approver, the roster's declared drafter integrates. The roster's `drafter` stays the saved fallback across follow-ups.

Result hashes bind text and data, plus files, patch and verification for working copies. Code or data changes require fresh approval even if prose is unchanged. Each round freezes its event cutoff; directed messages affect visibility without adding turns.

## Continuing the conversation

For each routed follow-up, write a file with the user's message, new decisions or evidence, the current skill stage if applicable, and the requested deliverable and acceptance criteria. Include relevant host-only exchanges since the last discussion, separating user decisions from host recommendations. Put the host's opinion under a `Host view (non-binding)` heading, per Host view. Resume the same run directory:

```bash
python3 scripts/panel.py --continue /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Add `--fresh-sessions` to start new native sessions instead of resuming. Each participant then receives the new brief and a history file in its own scratch directory holding the earlier briefs and the earlier discussion visible to it, which it reads as the task needs; nothing earlier is inlined. Sessions stay retired, the report lists them under `session_replacements`, and later follow-ups resume the new sessions. Put every decision the next answer depends on in the follow-up file, since fresh sessions keep no unrecorded context.

Supply the same `--adapter NAME=FILE` registrations for external harnesses. Pass `--idle-seconds`, `--run-seconds`, `--unbounded`, `--max-cycles` or `--report-seconds` to change the saved limits for this and later discussions; the `discussion_start` event records the limits in force, with `idle_seconds` null while each adapter's own window applies. The runner retains the roster, preset, models, effort, required approvers, execution settings, source snapshot, workspaces and, unless `--fresh-sessions` is passed, participant sessions. It supplies prior host briefs and previously undelivered shared discussion, clears the current candidate and approvals, and runs a fresh bounded discussion. Private opening rounds withhold current opening contributions only; participants still know the earlier conversation. Every new panel result requires fresh approval of its exact revision, even when its text is unchanged.

Continue within the saved execution boundaries. The source snapshot stays pinned; include new read-only evidence in the follow-up text. A new message does not authorize broader tools or source edits. Changes to the roster, preset, source or execution boundaries require an explicit reset; explain this and resolve authorization before starting the replacement. Changed limits need no reset.

The runner first resumes saved sessions in their original harness accounts and directories. A definitive terminal session-loading failure starts one fresh session automatically with the same role, settings, permissions and workspace. The replacement receives recorded briefs and the history visible to that participant, but not unrecorded native-session context. Relay any `session_replacements` listed in the report.

For stop or answer-solo requests while idle:

```bash
python3 scripts/panel.py --stop /absolute/panel-directory
```

This closes the conversation without invoking participants or modifying previous answers. Clear the host's active-panel routing. On an explicit reopen request:

```bash
python3 scripts/panel.py --reopen /absolute/panel-directory \
  --follow-up /absolute/follow-up.md
```

Reopening runs the same checks as continuation and preserves prior reports. Use `--continue` while active and `--reopen` after stopping; neither changes the roster or execution permissions, and both accept the same limit overrides and adapter registrations. For a reset, close the old panel and use the normal new-panel command with a new run directory; record it as active. Carry context into a reset only as requested, and disclose that participants start fresh.

The process exits after each answer, releasing its writer lock; native sessions and panel records persist on disk. Missing saved session IDs, changed frozen evidence, unreconciled dispatches or indeterminate delivery block continuation and reopening; preserve the roster and report the gap. Resolve uncertain effects before a reset that could repeat work.

### Older runs

Completed version-3 panels can be continued explicitly with their saved sessions; the runner archives their original report and upgrades continuation state to version 4. Unfinished work must be recovered first. The `task` roster configuration is rejected: put objectives and result requirements in the brief, and access and check requirements in `execution`. Completed older reports remain readable; unfinished older-format runs need a new run.

## Human input and recovery

With `--pause-between-rounds`, stderr announces `awaiting_host_decision`. Write one JSON line to stdin: `{"action":"continue"}`, `{"action":"stop"}`, or `{"action":"brief","text":"The full revised brief and acceptance criteria."}`.

A revised brief invalidates approvals and restarts opening rounds within the current discussion's round cap and remaining allowance. Sessions retain history; working copies retain work. SIGINT/SIGTERM stops scheduling, cancels active agent and verification process groups, and closes panel routing. Reports distinguish confirmed exit from uncertain termination. Stop an active process through its retained handle; `--stop` acquires the writer lock and closes only an idle conversation.

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
