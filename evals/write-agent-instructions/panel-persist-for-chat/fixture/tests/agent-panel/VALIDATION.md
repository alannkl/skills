# Implementation and validation record

Current interface: the brief defines the work and result; `execution` defines access and checks. Runtime task profiles have been removed. Earlier entries below record the implementation history, not current configuration.

Target: design v5, SHA-256 `437778778421b895f4fcfe334114c71b1e17fb3826362d2b448806e764fb92a7`.

## Plan and evidence

- Use Python 3.10+ and its standard library. Keep the scheduler independent of adapters; use asyncio tasks as completion handles and process groups for cancellation.
- Implement independent + discussion first, then leader + members and flat peers as data presets. Use three simulated participants, including shared adapters, before live runs.
- Pin behavior scenarios in `tests/test_panel.py` before executable bodies. Exercise durable delivery, revision approval, deadlines and cancellation through public runner/adapter seams with failure injection. The new API has no pre-change implementation to run against; use persistence assertions and real subprocess checks for the consequential cases.
- Preserve design documents. Store runtime artifacts outside the package. Independence is procedural; filesystem isolation and a comparative quality experiment are not claimed.

## Progress

- Read handoff, design v5, review status, repository instructions and harness references. Verified design hash. Created `feat/agent-panel`. The handoff's editor swap file was absent at initial inspection.
- Recorded 19 behavior scenarios before implementation.
- Independent + discussion passed its three-participant session, visibility, cutoff and exact-approval check before the other preset files were added.
- All 27 tests passed, with no skips, including all three presets through the actual CLI and executable harness fixtures. Real subprocess cancellation confirmed both parent and child exit. Command: `python3 -m unittest discover -s agent-panel/tests -v`.
- Sandbox limitation reproduced independently: Python asyncio's wake-up socket receives `PermissionError: [Errno 1] Operation not permitted`, delaying child-exit delivery. The subprocess suite passed outside that sandbox in 12.2 seconds. No product polling workaround was added.
- Installed Claude CLI help lists `dontAsk`; the initial design run selected that explicit mode. The `default` alias was not exercised. The initial design adapter used `dontAsk` with Read/Grep/Glob only. Existing spawn-agent files remained untouched; the final permission policy is recorded below.
- Final offline suite: 36 tests passed with no skips in 17.8 seconds. This includes bounded cancellation when an adapter stalls, corrupt recovery output, native permission denials, candidate tampering, and stopping while the host channel is paused. Python compilation and CLI help checks passed.
- Approval sensitivity check: a disposable copy changed the final gate to accept only the first two reviewers. `test_revision_invalidates_approval` failed as expected. The working implementation retained the full required-approver gate. Evidence: `/tmp/agent-panel-mutation-1ppzt1x1/result.txt`.

## Bounded live evidence

Run directory: `/tmp/agent-panel-live-kbq_s9vb/run`.

The exercise designed a short operator workflow from the v5 source document. It did not revise v5 or repeat its approval process. The configured models were Claude `fable` and Codex `gpt-6-astra`, both at high effort, using existing authentication. Limits were two draft/review cycles, 180 seconds per turn and 900 seconds for the run. No credentials or account settings were changed.

- Twelve native dispatches completed across separate persistent sessions, with independent designs, reciprocal critique, a first draft/review, clarification, and a second draft/review.
- Claude session: `f4d77646-e445-4779-89d4-68fda7aca397`.
- Codex session: `01a086db-68bc-7dd2-85a2-9171a5ea01b3`.
- Codex objected to the first candidate's word count and recovery wording. The runner withheld agreement, retained the objection, and collected fresh reviews after revision.
- Both participants approved `b1-r2`, SHA-256 `6ae7e6f7c83c413a79a93841aa56826814fe53814c0a5099301d6048391840e9`. The final candidate contains 435 whitespace-delimited words. Persisted session IDs, dispatch count, both review cycles, and candidate bytes were checked directly.
- Final live report: `/tmp/agent-panel-live-kbq_s9vb/run/report.json`.
- Both sessions were then resumed for a disposable cancellation check. Each native process was active before cancellation; both completion handles resolved and process exit was confirmed. Claude returned 143; Codex returned 0 after cancellation. The exit-zero result was not treated as a valid design contribution.
- Cancellation evidence: `/tmp/agent-panel-live-kbq_s9vb/cancellation/report.json`.

The live exercise covered independent + discussion with two agents. Leader + members and flat peers were exercised with three offline participants through both the adapter contract and executable CLI fixtures. No comparative quality experiment or enforced filesystem-isolation claim is made.

## Packaging checks and limits

- The bundled system `quick_validate.py` rejects `compatibility` and `disable-model-invocation`; it does not recognize those authoring-guide fields. Validation passed for the core frontmatter in a disposable copy, and the two fields were separately checked for their expected types and values. Local documentation links and preset JSON also passed.
- Run state stays outside the skill. Recovery reconciles an unfinished run and returns incomplete without automatic redispatch. Native usage is recorded when available; hard whole-run token or dollar ceilings are not claimed.
- The design v5 hash remains unchanged. Scope is the new `agent-panel/` package and the README inventory entry. No staging, commit, push, or installed-skill update was performed. The handoff's swap file was absent at both initial and final inspection.

## User-directed extension after design v5

The user clarified that agent-panel must coordinate research, reviews, implementation, debugging, writing and other tasks. Design discussion is the first test case, not the product boundary. Preserve the hashed v5 document; this instruction supersedes its design-only execution scope.

The extension keeps the N-participant scheduler, presets, delivery records and exact-approval gate. Task profiles determine phase instructions, capabilities, output fields and completion checks. Writable tasks use isolated worktrees at an explicit Git revision; the designated integrator assembles the result, the runner checks the assembled changes, and a non-integrating participant must approve them. The caller's checkout is not an integration target. Ten general-task behavior scenarios were pinned in `tests/test_tasks.py` before implementation.

- General-task checks passed for all three presets with three simulated participants, including shared adapters, real private Git clones/worktrees, integrated patches and executable checks. Read-only task checks covered research, reviews, writing and general deliverables. Debugging covered diagnosis with an expected failing reproduction and a corrected implementation in fix mode.
- The first two live implementation attempts stopped with native Claude permission denials during source inspection. Adding shell read grants alone did not resolve the second denial. A focused probe of the identical command succeeded with the same `dontAsk` mode and explicit `--add-dir` for source evidence. The adapter now declares source/check directories and grants peer snapshot access after reveal. No bypass or user permission-setting change was used.
- A general-task correction also freezes each file contribution before reveal; later working-copy edits cannot change another participant's fixed-round evidence. Diagnose mode checks source immutability after every participant round, including review.
- The user asked about ACP, then explicitly chose to finish the current implementation before deciding on a transport change. ACP remains deferred; this branch uses the two CLI adapters.


## Final verification

- Final offline suite: **50 tests passed, no skips**, in 31.0 seconds. Command: `python3 -m unittest discover -s agent-panel/tests -v`. The suite includes all seven task kinds, all three presets, repeated adapters, isolated worktrees, frozen contribution files, exact result hashes, executable checks, source preservation, recovery and cancellation.
- Successful live implementation run: `/tmp/agent-panel-implementation-live-i2t7znfc/run6/report.json`. Claude `fable` and Codex `gpt-6-astra` completed six native dispatches under `leader-members`, integrated `slug.py`, passed the five immutable acceptance tests, and both approved `b1-r1` at hash `e0f3aa045e79dba8ebc4f17cea3d0406ed8ce698b61aed4bfb0baeb6832b5852`.
- Persisted checks confirmed that only `slug.py` changed, the acceptance script and `.gitignore` matched the source snapshot, the caller's checkout stayed clean, both sessions stayed separate across resume, and the frozen result hash matched both approvals.
- Intermediate live attempts returned incomplete on native permission denials for source-directory access, complex shell programs, or directory-qualified Git commands. An ad-hoc permission probe also reported a Unicode assertion failure; it was not counted as a successful task check. These records remain in the same temporary validation directory.
- The user subsequently chose automatic tool permissions for all agents. The final Claude adapter uses native `auto` with prompts disabled and no Bash command allowlist. Codex retains `approval_policy="never"` and the task's sandbox. Task tool availability, source-edit restrictions and final reviewer approval remain separate from automatic tool permission decisions.
- Live verification of the final permission policy resumed both successful implementation sessions. Both executed the smoke check, returned the expected JSON result and retained their session IDs. Evidence: `/tmp/agent-panel-implementation-live-i2t7znfc/auto-permission-check/report.json`.
- Design discussion and leader/member implementation have live acceptance evidence. Research, review, writing and general tasks have offline checks across all presets; debugging covers diagnose/fix through independent discussion. No broader task-quality comparison or enforced filesystem-isolation claim is made.
- Source compilation, CLI help, frontmatter checks, JSON data checks, documentation links and whitespace checks passed. The bundled validator's two-field limitation remains documented above.
- Changes remain uncommitted on `feat/agent-panel`. The design v5 hash is unchanged. No push or installed-skill update was performed. ACP remains deferred by the user's direction.


## Task-independent runner

- Removed the runtime category registry, profile JSON files and category-specific prompt/result handling. Optional examples now live in `references/brief-examples.md` and are never loaded by the runner.
- Replaced `task` configuration with explicit `execution` settings. These describe workspace access, web access and checks without inferring them from the brief's subject. The result envelope accepts arbitrary structured `data`; text, data and file changes remain bound to exact-revision approval.
- The manifest format is version 3. Completed older reports remain readable; an unfinished earlier-format run requires a new run. Old `task` configuration fails with a migration message instead of silently changing permissions.
- All **53 tests passed with no skips** in 31.5 seconds. They retain the existing scheduling, permission, worktree, verification, recovery and cancellation coverage and add unfamiliar briefs, arbitrary result data and fresh approval after data changes.
- A bounded live flat-peer run used Claude `fable` and Codex `gpt-6-astra` with automatic tool permissions. With no task category or profile supplied, they completed the observation-allocation brief and approved identical structured output. Evidence: `/tmp/agent-panel-brief-live-obub3q7y/run/report.json`.
- The live result's data, both approvals and content hash were verified directly. Compilation, documentation links and whitespace checks passed. Design v5 remains unchanged as a historical reference; ACP remains deferred.

## Adapter registration and repository-only tests

- The CLI now accepts repeated `--adapter NAME=FILE` registrations for trusted modules exporting `create_adapter()`. Another harness can use the existing adapter contract without editing the scheduler. Claude and Codex remain the two bundled production integrations.
- An external subprocess adapter passed all three presets through the CLI with three participants and distinct resumed sessions. Invalid module paths, duplicate names and invalid contracts fail before dispatch.
- Tests, fixtures and this validation record moved to `tests/agent-panel/`. The installable skill contains runtime files and references only.
- All **55 tests passed with no skips** after relocation. Run `python3 -m unittest discover -s tests/agent-panel -v` from the repository root.

## Read-only evidence and roster fixes

- The ACP discussion exposed a capability mismatch: the shared prompt declared `shell: false`, so Codex declined to use its sandboxed shell to read evidence. Removed that tool-availability claim, declared `file_reads: true`, and explicitly permitted read-only inspection through the harness's file-reading mechanism. Native read-only sandbox/tool settings remain unchanged.
- The regression failed before the fix. Both new tests now pass across all presets, including checks that Codex starts/resumes read-only and Claude retains its read tools. The full suite passed **57 tests with no skips**.
- Live evidence: `/tmp/agent-panel-readonly-regression-uqfjrdv7/run/report.json`. Both participants returned the generated initial marker and the separate review-stage marker, neither of which appeared in the brief. Codex's captured native command events show successful reads of both files. The source hash stayed unchanged and both reviewers approved the same candidate.
- The live run skipped one timed-out Codex critique after confirmed process exit, then resumed that participant for successful final review. This was an agreed result with the skipped contribution recorded, not a failure-free run.
- Added an explicit roster-confirmation step that includes models and reasoning effort. Reuse an already-provided or approved roster/effort default; reconfirm material roster or effort changes.
- The user subsequently restricted live testing to Claude Sonnet and GPT Luna. The earlier run was already complete when checked; no additional Fable/Astra test invocation was launched. Future live testing follows the model restriction in this directory's README.
