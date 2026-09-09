# Runner usage

## Brief and roster

The brief defines what participants must do, what to deliver, and how to judge success. There is no task selector, category registry or profile loader. Optional [brief examples](brief-examples.md) help the host write a brief; the runner does not consume them.

For collaborative execution of an existing skill, follow [skill collaboration](skill-collaboration.md). The host selects a preset when the user leaves it unspecified and supplies it to the CLI. The host also manages interactive skill stages; there is no automatic skill loader, stage scheduler or question-forwarding mechanism in this runner.

A roster contains participants, coordination roles, optional evidence and explicit execution settings:

```json
{
  "source": "evidence",
  "execution": {"web": true},
  "drafter": "a",
  "participants": [
    {"id": "a", "role": "Develop the approach and integrate", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL"}},
    {"id": "b", "role": "Challenge assumptions and verify evidence", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL"}},
    {"id": "c", "role": "Check the complete deliverable against the brief", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL"}}
  ]
}
```

Replace model placeholders with available models. IDs are unique; `host`, `runner` and `all` are reserved. Every participant gets a separate session, including repeated use of one harness. `required_approvers` defaults to everyone. `leader-members` also requires `leader`; that participant integrates. Other presets use `drafter`.

Every opening contribution is required. Critique or clarification can skip a confirmed inactive, reconciled failure, while retaining that participant for required final approval. A failed participant never silently changes the approval policy.

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

These settings do not select instructions or output formats. The same access settings can serve unrelated briefs. Tool approval is automatic within these boundaries; final result approval still requires every configured reviewer.

Use Python 3.10+ on Linux or macOS and the authenticated CLIs selected in the roster. No Python packages are required. Git is required for `inspect` and `edit`.

## Evidence and working copies

For read-only evidence, optionally set `source` to a directory of selected files. Relative paths resolve against the roster file. The runner copies it to a read-only snapshot. Omitting source creates an empty evidence directory for work that only needs the brief or web retrieval.

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
    {"id": "a", "role": "Implement and integrate", "harness": "claude", "settings": {"model": "YOUR_CLAUDE_MODEL", "max_turns": 12}},
    {"id": "b", "role": "Verify behavior and scope", "harness": "codex", "settings": {"model": "YOUR_CODEX_MODEL"}}
  ]
}
```

The runner resolves the revision once and creates a private local clone without hardlinks or remotes. Participants get separate worktrees at that commit. Their Git metadata and changes stay in the run directory. Working-copy runs require a final approver other than the integrator.

`HEAD` means the committed revision. Dirty changes are not included. For a review of dirty work, export the exact diff and supporting files as evidence; preserve the requested scope rather than replacing it with HEAD.

Each participant keeps its working directory across resume. Contributions are captured as patches and read-only file snapshots. After reveal, peer references point to those snapshots so later working-copy edits cannot alter the round's evidence. The integrator assembles the result in its own worktree. A separate verification worktree reconstructs the final patch before checks run.

Choose a new run directory outside the source, caller repository and skill package. Regular files, executable modes and internal relative symlinks are supported. Escaping symlinks, special files and uninitialized submodule entries are rejected. Git-ignored files are not patch deliverables.

Processes share an operating-system account and may inherit local instructions, hooks and extensions. The runner separates edits and withholds initial peer inputs; filesystem access controls do not enforce independence. Use a controlled account or container when stronger isolation is needed.

## Checks and tool permissions

Working-copy runs require `checks` or an explicit `verification_note`. Checks are argument arrays, never shell strings, and run against the assembled result. Exit zero is expected unless specified otherwise:

```json
{
  "workspace": "inspect",
  "checks": [{"argv": ["python3", "reproduce.py"], "expect_exit": 1}]
}
```

Checks record their command, expected and actual exit code, stdout, stderr and hashes. They must leave reviewed source files unchanged. Generated check outputs stay in the verification worktree. A failing check prevents agreement even if every participant approves. Bounded rework receives that failure evidence; unresolved verification at the cap returns incomplete.

For acceptance tests participants must not edit, point the command at a script in the immutable source snapshot and make it test the verification working directory.

The two bundled adapters are the initial integrations. Both accept `model`, `effort` and optional trusted `executable`. Claude also accepts `max_turns` and `max_budget_usd`; Codex rejects unsupported bounds. Existing authentication and billing settings are retained.

Claude uses native `auto` with interactive permission prompts disabled. Available tools follow execution settings; its native policy assesses shell operations without a runner-maintained command allowlist. Source/check directories are declared with `--add-dir`, and peer snapshot access is added after reveal and retained on resume. Complex or Unicode-bearing shell programs belong in scratch script files to avoid fragile command parsing. The directory grants follow the [Claude permission rules](https://code.claude.com/docs/en/permissions#working-directories).

Codex uses `approval_policy="never"` with a read-only or workspace-write sandbox. Web retrieval follows explicit `execution.web`, using the [documented configuration setting](https://learn.chatgpt.com/docs/config-file/config-reference). Neither adapter uses an unrestricted bypass. Native denials remain visible blockers.

Claude defaults to eight internal turns per invocation. Its native budget flag applies where supported by the account. Codex has no equivalent generation bound here. Both have wall-clock limits, and reported usage is retained; a hard whole-run token or monetary ceiling is not promised.

## Run and inspect

```bash
python3 scripts/panel.py independent-discussion /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory
```

Defaults are three integration/review cycles, 180 seconds per invocation or check, and 1,800 seconds for the run. Ten seconds are reserved for cancellation/reporting, with a minimum reserve of five seconds. Participant rounds are capped at the opening phase count plus three times the cycle cap, including restarts after brief changes. See `--help` for options.

Stderr reports the run directory at startup. Stdout contains the final JSON report. Exit codes are 0 for agreed, 1 for disagreement, 2 for incomplete, and 130 for interrupted. Startup errors return 2 with null artifact paths when no report could be created.

Artifacts include the frozen manifest, `events.jsonl`, participant prompts/native outputs, and `revisions/REVISION/` containing `result.md` and `result.json`. Working-copy results also include frozen files, a patch and check evidence. `report.json` points to the result and records reviews, verification, failures, cancellations and usage.

The participant protocol is a transport envelope. `text` holds the contribution or final deliverable; optional `data` is any JSON object requested by the brief. Its keys are not predefined. Reviews use the common revision/hash and approve/object/unable fields. The runner validates the envelope and identity; reviewers assess substance against the brief.

Result hashes bind text and structured data, plus files, patch and verification for working copies. Changing code or structured output requires fresh approval even when the prose is unchanged. Each round freezes its event cutoff; directed messages affect visibility without scheduling extra turns.

## Human input and recovery

With `--pause-between-rounds`, stderr announces `awaiting_host_decision`. Write one JSON line to stdin: `{"action":"continue"}`, `{"action":"stop"}`, or `{"action":"brief","text":"The full revised brief and acceptance criteria."}`.

A revised brief restarts opening rounds within the original limits and invalidates approvals. Sessions and working copies retain history and work. Start a new run for fresh independence, a changed roster, or changed execution boundaries. SIGINT/SIGTERM stops scheduling and cancels active agent and verification process groups. Reports distinguish confirmed exit from uncertain termination.

Use `python3 scripts/panel.py --recover /absolute/run-directory` after a crash. Recovery acquires the writer lock, reconciles persisted output/exit evidence, and applies valid results once. It returns incomplete without redispatch or rerunning verification. A torn final append is retained as `torn-event`. Saved PIDs are never signalled because they may have been reused.

The previous experimental `task` configuration is no longer accepted. Put its objective and result requirements in the brief and its access/check requirements in `execution`. Completed older reports remain readable; unfinished older-format runs require a new run.

## Additional harnesses

The collaboration engine works with adapter instances, not fixed harness names. Claude Code and Codex are bundled initially; another CLI needs an adapter that translates its launch, resume, permission and output conventions.

Register a trusted local adapter module without editing the runner:

```bash
python3 scripts/panel.py flat-peers /absolute/brief.md /absolute/roster.json \
  --adapter other=/absolute/other_adapter.py
```

The roster can then use `"harness": "other"` for one or several participants, alongside any other registered adapters. Repeat `--adapter NAME=FILE` for more harnesses. Names must be unique and cannot replace a bundled adapter. Each module exports `create_adapter()`, returning an instance implementing the contract below. The module is executable code selected by the host; participant output cannot register adapters.

Supply the same registrations when using `--recover`. Recovery does not import modules named in saved participant output or run state. Registration makes a harness available; it does not establish that its authentication, permissions or capabilities work in the current environment. Validate the adapter before claiming live support.

## Verification and extension

Repository tests and validation records live in `tests/agent-panel/`, outside the installed skill. They cover unrelated briefs, arbitrary structured output, external adapters, all presets with N participants, execution boundaries, exact approval, worktree integration, recovery and cancellation.

A harness adapter implements immediate `start`/`resume` handles, an asyncio completion task returning `Terminal`, bounded asynchronous cancellation, and recovery from persisted evidence. Export it through `create_adapter()` for CLI registration, or pass it directly in the mapping to `Panel`; the collaboration engine does not change. The adapter must implement automatic, noninteractive tool permissions within the declared execution boundaries, or report the unsupported capability. Runtime settings include the working directory, scratch directory, attempt directory and explicit capabilities.

An unfamiliar subject requires a brief, not a new adapter or task type. External tools still need support and authorization in the selected harness. Comparative quality experiments remain separate from operational acceptance.
