# Runner usage

## Brief and roster

The brief defines the work, deliverable and acceptance criteria. The host may use [brief examples](brief-examples.md); the runner reads the brief, without a task selector, category registry or profile loader.

For an existing skill, follow [skill collaboration](skill-collaboration.md). The host supplies the chosen preset to the CLI and manages interactive stages, skill loading and questions; the runner does not automate those steps.

### Default roster

When the user leaves the roster unspecified, use two participants:

| Harness | Preferred model | Effort |
| --- | --- | --- |
| Claude Code | Claude Fable 5.1 | `high` |
| Codex | GPT-6 Astra | `high` |

1. Preserve explicit user choices and apply task-specific model restrictions only within their stated scope. Fill unspecified models on matching harnesses from the table; default unspecified effort to `high`.
2. Resolve exact model identifiers for the installed harness and current account using current model listings or account availability evidence. Consult current official vendor guidance when identifiers or capability are unclear. If a preferred model is unavailable, choose that harness's most capable available model for general reasoning and coding. Use the same rule for other requested harnesses. Base the ranking on current model descriptions, not names or speed/cost defaults. Report fallbacks and reasons, or unresolved availability/ranking before launch; never invent an identifier.
3. Set `high` explicitly where supported. If effort control exists but lacks `high`, disclose supported choices and resolve effort before launch. Report harnesses without effort control.
4. Assign roles and the integrator to fit the brief and preset, with both default participants required to approve. Write the resolved choices into the roster file; the runner does not discover or substitute models.

### Roster file

A roster specifies participants, coordination roles, optional evidence and execution settings. Replace the model placeholders with resolved identifiers:

```json
{
  "source": "evidence",
  "execution": {"web": true},
  "drafter": "a",
  "participants": [
    {"id": "a", "role": "Develop the approach and integrate", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "effort": "high"}},
    {"id": "b", "role": "Challenge assumptions and verify evidence", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL", "effort": "high"}}
  ]
}
```

Use supported effort values. IDs must be unique; `host`, `runner` and `all` are reserved. Each participant gets a separate session, even on the same harness. `required_approvers` defaults to everyone. Set `drafter`; `leader-members` also requires `leader`, who integrates instead. Working-copy runs require an approver other than the integrator.

Follow the [skill's roster-confirmation step](../SKILL.md#prepare) before launch. Presets determine coordination, not roster composition. Direct CLI calls with explicit roster files remain noninteractive.

Every opening contribution is required. Critique or clarification may skip a failed participant after confirming inactivity and reconciling the failure. That participant remains required for final approval.

## Execution boundaries

`execution` controls access and checks, independently of the brief's subject:

| Setting | Meaning |
| --- | --- |
| `workspace: "read-only"` | Default. Read frozen evidence and return a deliverable through the runner. |
| `workspace: "inspect"` | Use isolated worktrees and run commands; source edits are rejected. Scratch scripts are permitted. |
| `workspace: "edit"` | Edit separate worktrees and integrate a result for verification. |
| `web: true` | Enable web retrieval. Default is false. |
| `checks` | Commands to verify the assembled result, with expected exit codes. |
| `verification_note` | Explain the review method when working-copy verification cannot use executable checks. |

Access settings are independent of task instructions and output formats. Tool approval is automatic within these boundaries; final approval requires every configured reviewer.

All modes permit reading supplied evidence, including bounded read-only shell inspection when needed. Permissions expose `file_reads`, not a blanket `shell` switch. Each adapter controls native tools and sandbox enforcement; read-only mode permits neither source edits nor general side effects.

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
    {"id": "a", "role": "Implement and integrate", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "effort": "high", "max_turns": 12}},
    {"id": "b", "role": "Verify behavior and scope", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL", "effort": "high"}}
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

Defaults: three integration/review cycles, 180 seconds per invocation or check, and 1,800 seconds per run. Cancellation/reporting reserves ten seconds, with a five-second minimum. The round cap is the opening phase count plus three times the cycle cap, including restarts after brief changes. See `--help` for options.

Stderr reports the run directory at startup; stdout contains the final JSON report. Exit codes: 0 agreed, 1 disagreement, 2 incomplete, 130 interrupted. Startup errors return 2 with null artifact paths if no report could be created.

Artifacts include the frozen manifest, `events.jsonl`, participant prompts/native outputs, and `revisions/REVISION/` with `result.md` and `result.json`. Working-copy results add frozen files, a patch and check evidence. `report.json` links the result and records reviews, verification, failures, cancellations and usage.

The protocol envelope carries contributions or deliverables in `text` and any brief-requested JSON object in optional `data`, without predefined keys. Reviews use revision/hash and approve/object/unable fields. The runner validates the envelope and identity; reviewers assess substance against the brief.

Result hashes bind text and data, plus files, patch and verification for working copies. Code or data changes require fresh approval even if prose is unchanged. Each round freezes its event cutoff; directed messages affect visibility without adding turns.

## Human input and recovery

With `--pause-between-rounds`, stderr announces `awaiting_host_decision`. Write one JSON line to stdin: `{"action":"continue"}`, `{"action":"stop"}`, or `{"action":"brief","text":"The full revised brief and acceptance criteria."}`.

A revised brief invalidates approvals and restarts opening rounds within the original limits. Sessions retain history; working copies retain work. Start a new run for fresh independence or changed roster/execution boundaries. SIGINT/SIGTERM stops scheduling and cancels active agent and verification process groups. Reports distinguish confirmed exit from uncertain termination.

After a crash, use `python3 scripts/panel.py --recover /absolute/run-directory`. Recovery takes the writer lock, reconciles persisted output/exit evidence and applies valid results once. It returns incomplete without redispatch or re-verification. A torn final append is retained as `torn-event`. Saved PIDs are never signalled because they may have been reused.

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
