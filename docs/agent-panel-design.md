# Agent-panel design v5

Status: proposed shared design. This document requires independent approval by both designing agents before being presented as their agreed design. Design approval does not authorize implementation or external actions.

## Goal and required behavior

A human gives a configurable roster of N coding-agent participants the same task. Participants may use the same harness or different harnesses. Each designs independently, then they exchange evidence, challenge alternatives, revise one shared proposal, and return the exact design every required approver accepts. The human can inspect the discussion and intervene between rounds. If agreement cannot be reached, the result explains the remaining disagreement or incomplete work.

The product must support three named presets: leader + members, flat peers, and independent work + discussion. The first live acceptance scenario is this tool's own design using two independent designers followed by joint approval. Two participants are the initial live test setup, not a limit on roster size. Authority, visibility, allocation, combination, and verification remain internal design concepts, not a combinatorial user interface.

## First implementation

The skill is named `agent-panel`. Its `SKILL.md` invokes one local runner with headless adapters for Claude Code and Codex, bundled under the skill's `scripts/` directory. The existing spawn-agent references supply launch, output parsing, permission, and resume conventions. Managed sessions only; preserve explicit settings and working directories across resume.

Ship the skill instructions, runner, adapters, preset data, and tests as one skill package. Document the required harness CLIs and script runtime as prerequisites. A separate runner repository or independently versioned package is not required for the first implementation.

The runner owns participant scheduling, input construction, artifact capture, bounded execution, and terminal status. The skill supplies the task brief, role instructions, and how to interpret the result. The host starts the run and communicates with the human. It does not choose individual speakers during a scheduled phase.

Use files: a run manifest, an append-only JSONL event log, and participant/proposal artifacts. Store these in a separate per-run directory outside the installed skill package. The manifest records the brief and source snapshot, preset, participants and session IDs, directories, required approvers, settings, limits, and designated drafter. Events record phase changes, messages, dispatch attempts, terminal results, objections, approvals, and human decisions. Assignments and decisions are event types. The runner is the sole writer of authoritative records; participant outputs are ingested as data.

MCP, a room server, a dedicated UI, live steering, ACP integration, external chat bridges, and attachment to existing interactive sessions are deferred. Process cancellation and timeouts remain required. Transport adoption later is driven by a tested capability need, not a universal preference for one protocol.

## v1 scope

The first runner implements exactly the following and nothing more. Anything outside this list is a later revision.

- Event kinds: run_start, phase_start, phase_end, message, dispatch, terminal_result, candidate (revision ID and content hash), review (approve, object, or unable to assess, naming a revision), human_decision, cancel.
- Adapter contract: start(input, settings) and resume(session_id, input, settings) immediately return a run handle containing a completion promise; cancel(handle) terminates that invocation and waits for confirmed process exit or reports an indeterminate termination. The completion result includes the known session ID, normalized terminal result, and reported usage. The implementation may use the equivalent future/task mechanism in its chosen language. A terminal result carries raw text, the parsed structured block, exit status, and usage where the harness reports it. Two adapters, Claude Code and Codex, following the spawn-agent references.
- Roster: support N participants from the first implementation. Each participant has a unique ID, role, harness selection, settings, separate session ID, and independent delivery/review state. Multiple participants may share one harness adapter, including participants with different models or roles. Schedule rounds, route messages, track failures, and evaluate required approvals by participant ID over the configured roster, never by a hardcoded pair or harness name. The initial two adapters do not limit participant count. A future harness implements the existing adapter contract without changing the collaboration engine.
- Command line: one command taking a preset name, a brief path, and a roster path. It exits with one of agreed, disagreement, incomplete, or interrupted, and prints the paths of the latest candidate and the report.
- Presets are data files. Independent + discussion is implemented and exercised first. Leader + members and flat peers are written as data and exercised against their acceptance checks before being advertised.
- Independence is procedural in v1, checked by provenance markers and dispatch records. Enforced isolation through filesystem controls is a later addition and is reported as absent until then.
- No summarizer call by default. No MCP, room server, UI, live steering, ACP, chat bridge, or attachment to interactive sessions.

## Discussion and joint approval

1. Freeze the brief and required approvers. Start separate participant sessions with identical task evidence and no peer contributions.
2. Collect initial designs. Wait for every required initial contribution before reveal. A missing required participant produces an incomplete outcome after recovery attempts are exhausted.
3. Reveal initial designs to the participants and run a parallel critique round. Each contribution identifies concrete objections, evidence, alternatives, and proposed resolutions.
4. Give a designated drafter all contributions. The drafter produces one candidate document and explains how objections were handled. The drafter has editorial responsibility, not unilateral authority to declare agreement.
5. Freeze the candidate bytes and compute a revision ID and content hash. Every required approver receives the same candidate and relevant unresolved objections. Require a structured response naming that revision: approve, object, or unable to assess, with reasons and any remaining assumptions.
6. Return agreed only when every required approver explicitly approves that exact candidate and the latest required reviews leave no unresolved blocking objection. The drafter participates in this review; writing the candidate is not approval. The runner checks the response format, identity, and revision, while the agents supply the substantive judgment.
7. If anyone objects, schedule a bounded clarification round among the required reviewers, then another draft and review cycle. Every change creates a new revision and requires fresh approval from all required approvers. When limits are reached, report disagreement or incomplete work with the latest candidate clearly marked unapproved.

Agreement means all required approvers judge the proposal strongest against the brief and considered alternatives. It is not a guarantee of objective optimality or empirical correctness. Agreed assumptions and experiments remain visible in the final design.

For the first runner, use deterministic full rounds with one contribution per required participant. Mentions refer to intended recipients but do not independently enqueue unlimited work. Each round's inputs use a fixed event-log cutoff, so faster responses cannot change what slower members see within the same round. At most one invocation may be active for a participant session.

A human intervention is ingested through the host's explicit input channel between rounds. A substantive change to the brief creates a new brief revision and invalidates earlier candidate approvals. An immediate stop cancels outstanding processes and records an interrupted outcome.

## Preset semantics

| Preset | Planning and coordination | Authority |
| --- | --- | --- |
| Leader + members | A leader proposes assignments and integrates member contributions. The runner validates the roster and schedules the next bounded phase. | Leader chooses the proposed approach within the brief. |
| Flat peers | Members discuss in scheduled rounds and propose responsibilities. A declared drafter assembles the candidate. | Agreement among required peers; unresolved objections return to the human. |
| Independent + discussion | Initial contributions remain private until reveal, followed by critique, drafting, and joint review. | Agreement among required peers after reveal. |

For joint design tasks, the required final approvers default to all designated designers, regardless of who leads or drafts. The initial two-agent live test therefore requires both designers; larger rosters require every designated approver. A different task may explicitly choose a different approval policy at run creation. A failed participant never silently changes that policy. The presets share execution machinery but need separate behavioral acceptance checks; they are not assumed to work automatically because one preset works.

## Evidence and workspace boundaries

For design-only tasks, give each participant the same immutable source snapshot and a separate artifact directory. Permit evidence gathering without modifying the source. If independent implementations are requested later, give each writer a worktree at the same base revision.

Worktrees isolate edits; they do not restrict what another process can read. Before reveal, input construction excludes peer output, and peer artifact paths are withheld. For a claim of enforced independence, use filesystem access controls or isolated mounts that prevent reading peer artifacts and the coordinator log. Where a harness cannot provide that restriction, report the limitation as procedural independence rather than a tested isolation guarantee.

Later code execution distinguishes competing complete solutions from complementary subtasks. For competing solutions, choose one base and port selected ideas. For complementary work, establish interfaces and ownership, then integrate in dependency order. A single integration writer reconciles overlaps. Verify the assembled result, with review by a participant that did not author the integration. Clean text merges alone are insufficient.

## Delivery, failures, and context

Each event has an ID, runtime-assigned sender, phase, and visibility. Each dispatch records a stable turn ID, participant, exact input event IDs, brief/proposal revision, attempt number, and terminal outcome. Visibility grants access; the phase schedule determines whether a prompt is sent.

Advance the completed-input cursor only after a valid terminal response is durably recorded. A crash between harness execution and recording can leave delivery indeterminate. Do not promise exactly-once delivery into the model. Record the uncertain attempt, reconcile persisted harness output when possible, and apply a successfully recovered turn result only once. If completion cannot be established, stop incomplete rather than automatically repeating possibly completed side effects. A known pre-dispatch transient failure may be retried once under the original limits.

A failed or timed-out required participant remains required. In a critique or clarification round, after allowed recovery attempts are exhausted, the run may record the contribution as missing and continue only if the prior attempt is confirmed inactive and its completion state is reconciled; unresolved indeterminate attempts stop the run as incomplete under the preceding recovery rule. A participant whose contribution was skipped receives the still-uncompleted eligible events on its next dispatch and remains required for final approval. In the initial-contribution and final-review phases the run cannot proceed without it, so preserve partial outputs and report incomplete. The user may explicitly restart with a changed roster; the new run requires new approval. Normal disagreement at the round cap returns disagreement. Cancellation returns interrupted. Only joint approval produces agreed.

Per-turn and whole-run deadlines include a reserved allowance for final reporting. Round limits are hard. Usage ceilings are enforced only to the extent the adapter supports timely measurement and generation bounds; report actual usage where available.

Resumed participants receive newly eligible events plus the current brief, candidate, and unresolved-objection references as needed. Delta delivery does not erase old context. Avoid an extra summarizer call at every phase by default. Add a recorded summary or context checkpoint only when needed, preserving exact decisions and objection references. A recovered participant must still read and approve the exact final candidate.

Participant approval and human authorization are separate records. The runner assigns sender identity from the process/adapter binding. Human input enters through a separate host-controlled channel; a member cannot become human by setting a sender field. Native permission denials are reported as blocked; the runner does not assume every headless harness supports interactive permission forwarding.

## Acceptance and evaluation

- Initial live test: one Claude Code participant and one Codex participant retain separate session histories across at least one reciprocal critique/revision cycle, and both explicitly review the final candidate.
- Roster tests: use three or more simulated participants across all three presets, including multiple participants sharing one harness adapter. Verify separate sessions and delivery cursors, round scheduling, message routing, cancellation, failure handling, and approval tracking by participant ID. Two approvals out of three required reviewers must not produce agreed; a stale or missing required third review remains blocking.
- Adapter extension test: register a test adapter under another harness name and run a roster through the unchanged scheduler and approval logic. No extra production harness integration is required for v1.
- No peer-specific contribution appears in an initial prompt. With enforced isolation enabled, attempts to read peer artifacts are denied. Test provenance with unique participant markers and dispatch records, not arbitrary overlapping text.
- Each scheduled round sees the declared fixed log cutoff. Normal prompt rendering includes each selected event once; crash recovery records uncertainty and does not claim exactly-once model processing.
- An approval for revision A cannot satisfy revision B. Changing the brief or required roster invalidates prior approval for the result.
- Persistent objections reach a bounded disagreement result. A failed required member reaches incomplete, never agreed by a smaller remaining set.
- A participant claiming to be human cannot authorize a gated action. Cancellation stops further scheduling and records any uncertain in-flight effects.
- Exercise all three presets against their authority and visibility rules before advertising support.
- Evaluate discussion against both independent attempts plus synthesis and an equal-budget extra private revision round plus synthesis. Keep task, source snapshot, roster, and rubric fixed; use repeated tasks, executable checks where possible, and blind quality assessment. Record quality, regressions, cost, latency, and human correction effort.

The experiment determines whether discussion improves task quality for the tested cases. A later room server additionally addresses live interaction and recovery requirements, which are separate product benefits.
