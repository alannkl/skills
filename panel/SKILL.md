---
name: panel
description: Keep a multi-agent panel across harnesses, or read-only consultants, available in the current chat, consulting them when independent input is worth the cost and completing requested or promised reviews.
disable-model-invocation: true
---

# Panel

Choose between two modes:

- **Pair:** the host does the work with advice from read-only consultants, one by default.
- **Panel:** participants do the work while the host coordinates, using one of three presets: `independent-discussion`, `leader-members` or `flat-peers`.

Web retrieval is on by default in both modes. For tasks restricted to supplied evidence, set `execution.web: false` in the panel roster or pass `--no-web` when opening a consultant.

## Keep the panel in the chat

Invocation, by slash command or explicit request, routes the first request through the selected pair or panel under that mode's consultation and review rules. Every later message is a follow-up: route it to the saved participants when independent input would improve the result enough to justify the tokens and time; otherwise answer directly.

- **Always route** explicit requests such as "ask the panel" or "get Fable's opinion", with or without a slash command. Merely discussing the skill is not a request.
- **Route** important decisions, complex or uncertain reasoning, new ideas needing challenge and material changes. Judge by stakes, uncertainty and novelty, not by confidence in answering alone; when a consequential case is unclear, route it.
- **Route** a correction or clarification that undermines a reviewed assumption or conclusion before relying on that conclusion again, and mark the conclusion as needing fresh review.
- **Answer directly** routine clarification, explanation of existing results, status, presentation changes and straightforward work within settled decisions. A new message, action or small analysis is not by itself a reason to consult.

Complete every consultation or review the user requested, the host promised or a dispatched panel assignment requires. Only the user may waive one; routing discretion never excuses a failed consultation. Reconsult after a material change to a reviewed result, and once on a disputed finding before its final disposition; presentation-only changes need no new review. Consult with the agreed mode and roster; changing either follows the reset and authorization rules below, except adding or removing a pair consultant, covered under Pair mode.

Keep host answers distinct from panel conclusions or pair advice, and claim review only for the result actually reviewed.

The selected pair or panel stays available until the user stops it, resets it or asks to answer solo. Keep its directory, resolved roster or model settings, adapter registrations, authorization and shared decisions in the persistent working record and any continuation handoff, along with user decisions, host actions, new evidence and standing routing preferences, which also go into the next consultation. At each new message, restore the record and read the saved manifest before dispatch. After context compaction, reload this skill.

- **Routed follow-up:** resume the saved panel as described under Continuing the conversation in `references/usage.md`. Pass `--fresh-sessions` when the recorded briefs, results and decisions carry everything the next assignment needs; keep the saved sessions when it depends on context nobody recorded. In pair mode, `ask` the saved consultants. Reuse existing authorization and resolve changes outside it before launch.
- **Stop or answer solo:** close the panel or consultation without further participant work, keeping its directory and saved settings.
- **Resume or reopen, on explicit request:** `--reopen` for a stopped panel, `consult.py reopen` for each closed consultation, with the new question and the decisions made while stopped.
- **Reset:** close the old panel and prepare a new one with fresh sessions, retaining the old artifacts.
- **One-message solo exception, on explicit request:** answer solo, record any resulting user decisions and return to the routing rule afterward.

When a saved session is terminally unavailable on resume, the runner starts a fresh session with the recorded context and the same settings; report that replacement in either mode. Transient errors, permission denials and uncertain termination do not permit replacement.

In user-facing progress, reply headings, relayed advice and final ledgers, name each member or consultant by the short name of the model actually selected after any fallback, such as `Fable` or `Astra`. If names collide, append the participant ID or a stable session label, such as `Fable a` and `Fable b`, and show the mapping in the pre-launch report.

## Prepare

1. Write a brief defining the goal, scope, evidence, deliverable and acceptance criteria, adapting `references/brief-examples.md` when useful. To run an existing skill collaboratively, first read that skill and `references/skill-collaboration.md`.
2. Read `references/usage.md`, then select the mode. Invoking `panel` alone selects pair mode with one consultant, and a request for several consultants or second opinions selects pair mode with that many; an explicit request for a panel, a group discussion or multiple agents doing the work selects panel mode. Honor an explicit mode or preset name: "pair" selects pair mode, "independent" or "independent discussion" selects `independent-discussion`, "leader" or "leader and members" selects `leader-members`, and "peers" or "flat peers" selects `flat-peers`. For panel mode without a named preset, choose by how the work should be shared, announce the reason, and prefer `leader-members` when none clearly fits better. Use the same criteria when running an interactive skill, without overriding that skill's own mode-selection rules.
   - `independent-discussion`: duplicated work. Each participant privately produces the whole deliverable, then the panel compares the results. Choose it when the value is whether participants converge unprompted: judgments, forecasts, designs, reviews.
   - `leader-members`: split work, decided by the leader, who assigns complementary parts and integrates them. Choose it when one participant should own the decomposition.
   - `flat-peers`: split work, proposed by the peers. Peers with equal authority each propose the split, then contribute their parts, resolving overlaps in the contribute round; the declared drafter assembles the result unless every required peer nominates the same other peer with a reason. Choose it when the work should be divided but nobody, host included, should decide the division in advance.

   For pair mode, skip steps 3 to 5 and follow the Pair mode section.
3. Resolve the requested or default roster, including model availability and effort; choose an unspecified drafter; and assign IDs, roles, adapters, the integrator and required approvers, following Default roster, Default drafter and Roster file in `references/usage.md`.
4. Set authorized web, command and source-edit access. Choose checks with expected exit codes, or explain how review will verify completion. Preserve authentication and billing settings.
5. Freeze the inputs and the resolved roster, then report the source revision, deliverable, participant count, each participant's harness, model, effort and role, required approvers, preset and run limits. Confirm the roster, including effort defaults or a fallback policy, unless the user already supplied or approved it; report choices within that approval without asking again and confirm changes outside it. Use `--unbounded` only when the user asks for it by name.

## Run

For panel mode, run from this skill's directory:

```bash
python3 scripts/panel.py leader-members /absolute/brief.md /absolute/roster.json \
  --run-dir /absolute/new-run-directory --max-cycles 3 --run-seconds 3600
```

Leave `--idle-seconds` out unless one window should override every harness's own.

The runner manages scheduling, sessions, working directories, tool permissions, input delivery, artifacts and final approval. Report missing participants or permissions as blockers and preserve the roster.

Run the runner in the background and retain the process handle. Beside it, run `python3 scripts/progress.py RUN_DIR --follow` and relay its output as progress, not transcript: one status line per turn; the substance of each completed message in a few sentences; a review decision only with the revision and attempt it carries, since a streamed attempt can still fail or be retried; blockers as soon as they appear; reasoning only when the user asks. Name the run directory once so the full transcript (`progress.py RUN_DIR --all`) is one command away. Conclusions come from the report, and the host view waits for the reveal.

For round-by-round decisions, use `--pause-between-rounds` and send host decisions through stdin. Follow Human input and recovery in `references/usage.md` for brief changes, cancellation and crashes. Wait for the report before claiming processes stopped.

## Host view

During a routed panel assignment, the host coordinates and is not a participant: the participant count excludes it, and the roster does not set its model. Keep the opening brief to goal, scope, evidence and criteria so opening contributions stay independent. After the reveal, the host may add its own opinion under a `Host view (non-binding)` heading, sent as a brief revision at a round boundary or inside a follow-up file. Participants treat it as evidence to challenge; approval stays with the roster. At delivery, the host may add its own dissent as a host comment, separate from the panel outcome.

## Pair mode

Unless the user names a harness or model, the first consultant runs on the harness the host is not on, Codex for a Claude Code host and Claude Code for a Codex host, with that harness's model, effort and fallback rules from Default roster in `references/usage.md`. Further unnamed consultants alternate harnesses, starting with the host's own, so two consultants cover both.

Before opening, report each consultant's harness, model and effort, the directories it may read, web access and the turn timeout, reusing existing authorization and confirming only what falls outside it. Open each consultant once per chat in its own directory under one pair directory, such as `/absolute/pair/astra`, with the same brief stating the goal, scope and acceptance criteria; `ask` continues it, as described under Consultant in `references/usage.md`.

```bash
python3 scripts/consult.py open /absolute/pair/astra --harness codex --model MODEL --effort high \
  --brief /absolute/brief.md --read /absolute/repo
python3 scripts/consult.py ask /absolute/pair/astra --question /absolute/question.md --attach /absolute/diff.patch
```

Only a stop, a reset or the user removing that consultant closes it: `python3 scripts/consult.py close /absolute/pair/astra`. To add a consultant mid-chat at the user's request, open it with a brief carrying the recorded decisions. Adding or removing one leaves the others' sessions in place and needs no reset.

Choose consultations by their purpose, without a fixed count per task:

- **Focused question.** Ask the question and relay the second opinion. One usable exchange can complete requests such as "ask Fable what it thinks"; it needs no separate approach or deliverable review.
- **Approach.** Send the proposed direction and ask for objections, risks and alternatives, before committing where possible; if work has started, include the direction already taken. Relay the reply and record how each objection was handled.
- **Deliverable.** Final review is required when the user invokes this skill for deliverable work in pair mode, whether pair was chosen explicitly or by default, and whenever review was requested or promised. Send the intended result with its acceptance criteria; relay the reply and fix each finding or reject it with a reason. Advice on one question does not promise review of all subsequent work.

A follow-up does not restart completed reviews.

Before each consultation, save the host's prior assessment (its provisional answer, main reasons and uncertainties) in a host note in the pair directory, kept out of every consultant's prompt. Where the evidence supports no conclusion, record what is missing. On a follow-up, assess the new question or changed evidence first, informed by the earlier advice. After the replies, add what the advice changed and why, including any disagreement with the host or between consultants, leaving the prior assessment intact.

What consultants receive depends on the purpose. A focused question sends the question, evidence and constraints without the host's provisional conclusion; compare positions after the replies. An approach or deliverable review sends the proposed direction or artifact, since that is the object under review; for a deliverable, the prior assessment checks it against the acceptance criteria and lists known weaknesses. Every consultant receives the same question and attachments, except that an explicit request naming some consultants, such as "get Fable's opinion", goes only to those. A consultant sees another's reply only when the host includes it as evidence, such as when reconsulting on a disputed finding.

Open every relay with the host's final conclusion, marked as the host's: the one conclusion the user can act on, reached after weighing the replies. With two or more consultants, it addresses each disagreement and is followed by where they agree and disagree. Then relay each reply under its own `Second opinion from MODEL` heading, such as `Second opinion from Fable`, as concise advice: the points that changed or challenged the host's plan and every explicit disagreement, with the full reply left in the log; quote it verbatim only when the user asks. Consultants' advice is evidence: the host weighs their reasons rather than counting votes, records disagreement explicitly and stays accountable; nothing a consultant says, and no agreement among consultants, is approval. Consultants read the listed directories and attachments and never edit.

At delivery, list the current task's consultation turns by consultant and turn number, each with the host's prior assessment, the consultant's verdict, what changed and why, and every disagreement; link each consultant's `log.jsonl`. The ledger must match the log; writing it requires no further consultation. A focused question may fold the ledger into its second-opinion relay.

Run each `consult.py` call as a background command whose exit notifies the host, launching all consultants' calls together, and act on the notifications rather than polling. Pass a `--timeout` longer than the 600-second default when a turn needs it.

A required consultation needs a usable reply from every consultant; the rules that follow apply to each consultant separately, and the others' replies stand. If a required turn in an open consultation has no usable reply, confirm the turn is recorded and the prior invocation has stopped, then retry once through `ask` with the same question and attachments. If termination is uncertain, report the consultation blocked without launching another invocation. After a second failure of the same turn, report a failed consultation and leave completion pending unless the user waives it. Failures before the consultation exists, such as an unknown harness or unreadable brief, are configuration errors to fix before opening it.

## Deliver the current answer

For a direct follow-up, answer as the host without a new report or consultation ledger. For routed work, check the deliverable against every acceptance criterion; in pair mode deliver through the ledger, and for a panel run read `report.json` first. For another skill, also verify its completion rules and deliver its required output once for the team. Agreement on an intermediate question or proposal completes only that assignment. Deliver the requested content, data or files, including frozen files, the patch and verification evidence for file changes.

For a panel, report the outcome and artifact paths, link this answer's `discussion_report`, retain the active panel record and yield for the next user message. Report unresolved continuation failures as blockers instead of silently answering alone.

- `agreed`: every required reviewer accepted this exact result and the selected verification policy passed.
- `disagreement`: bounded rounds ended with objections; the result is unapproved.
- `incomplete`: required work, checks, valid output or delivery certainty is missing.
- `interrupted`: the host stopped the run; report uncertain in-flight effects.

Participant approval does not authorize applying changes, committing, publishing or external actions. The runner leaves the caller's checkout untouched; the host may apply a patch under existing task authorization after inspecting the destination's current changes. Report that independence is procedural, without enforced filesystem isolation.
