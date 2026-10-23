# Consult mode

## Open consultants

Unless the user names a harness or model, the first consultant runs on the harness the host is not on, Codex for a Claude Code host and Claude Code for a Codex host, with that harness's model, effort and fallback rules from Default roster in `SKILL.md`. Further unnamed consultants alternate harnesses, starting with the host's own, so two consultants cover both.

Before opening, report each consultant's harness, model and effort, the directories it may read, web access and the turn timeout, reusing existing authorization and confirming only what falls outside it. Open each consultant once per chat in its own directory under one consultation directory, such as `/absolute/consult/astra`, with the same brief stating the goal, scope and acceptance criteria; `ask` continues it, as described under Consultant commands. Run from this skill's directory:

```bash
python3 scripts/consult.py open /absolute/consult/astra --harness codex --model MODEL --effort high \
  --brief /absolute/brief.md --read /absolute/repo
python3 scripts/consult.py ask /absolute/consult/astra --question /absolute/question.md --attach /absolute/diff.patch
```

Only a stop, a reset or the user removing that consultant closes it: `python3 scripts/consult.py close /absolute/consult/astra`. To add a consultant mid-chat at the user's request, open it with a brief carrying the recorded decisions. Adding or removing one leaves the others' sessions in place and needs no reset.

## Consultations

Choose consultations by their purpose, without a fixed count per task:

- **Focused question.** Ask the question and relay the second opinion. One usable exchange can complete requests such as "ask Fable what it thinks"; it needs no separate approach or deliverable review.
- **Approach.** Send the proposed direction and ask for objections, risks and alternatives, before committing where possible; if work has started, include the direction already taken. Relay the reply and record how each objection was handled.
- **Deliverable.** Final review is required when the user invokes this skill for deliverable work in consult mode, whether it was chosen explicitly or by default, and whenever review was requested or promised. Send the intended result with its acceptance criteria; relay the reply and fix each finding or reject it with a reason. Advice on one question does not promise review of all subsequent work.

A follow-up does not restart completed reviews.

Before each consultation, save the host's prior assessment (its provisional answer, main reasons and uncertainties) in a host note in the consultation directory, kept out of every consultant's prompt. Where the evidence supports no conclusion, record what is missing. On a follow-up, assess the new question or changed evidence first, informed by the earlier advice. After the replies, add what the advice changed and why, including any disagreement with the host or between consultants, leaving the prior assessment intact.

What consultants receive depends on the purpose. A focused question sends the question, evidence and constraints without the host's provisional conclusion; compare positions after the replies. An approach or deliverable review sends the proposed direction or artifact, since that is the object under review; for a deliverable, the prior assessment checks it against the acceptance criteria and lists known weaknesses. Every consultant receives the same question and attachments, except that an explicit request naming some consultants, such as "get Fable's opinion", goes only to those. A consultant sees another's reply only when the host includes it as evidence, such as when reconsulting on a disputed finding.

Run each `consult.py` call as a background command whose exit notifies the host, launching all consultants' calls together, and act on the notifications rather than polling. Pass a longer `--timeout` when a turn needs it.

A required consultation needs a usable reply from every consultant; the rules that follow apply to each consultant separately, and the others' replies stand. If a required turn in an open consultation has no usable reply, confirm the turn is recorded and the prior invocation has stopped, then retry once through `ask` with the same question and attachments. If termination is uncertain, report the consultation blocked without launching another invocation. After a second failure of the same turn, report a failed consultation and leave completion pending unless the user waives it. Failures before the consultation exists, such as an unknown harness or unreadable brief, are configuration errors to fix before opening it.

## Relay and deliver

Open every relay with the host's final conclusion, marked as the host's: the one conclusion the user can act on, reached after weighing the replies. With two or more consultants, it addresses each disagreement and is followed by where they agree and disagree. Then relay each reply under its own `Second opinion from MODEL` heading, such as `Second opinion from Fable`, as concise advice: the points that changed or challenged the host's plan and every explicit disagreement, with the full reply left in the log; quote it verbatim only when the user asks. Consultants' advice is evidence: the host weighs their reasons rather than counting votes, records disagreement explicitly and stays accountable; nothing a consultant says, and no agreement among consultants, is approval. Consultants read the listed directories and attachments and never edit.

Deliver routed work through the consultation ledger: list the current task's consultation turns by consultant and turn number, each with the host's prior assessment, the consultant's verdict, what changed and why, and every disagreement; link each consultant's `log.jsonl`. The ledger must match the log; writing it requires no further consultation. A focused question may fold the ledger into its second-opinion relay.

## Consultant commands

`scripts/consult.py` runs one read-only participant per directory while the host does the work.

| Command | Behavior |
| --- | --- |
| `open DIR --harness H --model M [--effort E] [--web \| --no-web] --brief FILE [--read DIR ...]` | Start a session and answer the brief. Web retrieval defaults to enabled; `--no-web` disables it. A fresh consultation requires a new directory. |
| `ask DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Resume the saved session. Also the retry path for a failed opening turn once the consultation exists, since a second `open` rejects that directory. Rejects closed consultations. |
| `close DIR` | Close the consultation on stop or reset. |
| `reopen DIR --question FILE [--attach FILE ...] [--read DIR ...]` | Reopen a closed consultation and answer the new question with the saved session, model, effort and permissions. |

Attachments are inlined into the question. `--read` grants directory access through Claude's `--add-dir` or Codex's read-only sandbox. Neither harness grants the consultant write capability; consultants keep file reads, skills, subagents and web when enabled, and can read installed skills. Register external harnesses with `--adapter NAME=FILE`, as described under Additional harnesses in `references/panel-mode.md`.

A one-field schema requires each reply as text. `--timeout` defaults to 600 seconds and cancels a turn that never returns, leaving the session open. Stdout carries one JSON object with `ok`, `text` and the turn number. Exit 2 means no reply; the `error` text distinguishes a timeout, failed turn or configuration error. An unconfirmed timeout cancellation warns that the process may still be running.

`DIR/consult.json` records the harness, model, session and readable directories. `DIR/log.jsonl` records every question and reply; `DIR/turns/tN/` holds native captures.

All consultation commands take a writer lock. Before dispatch, the runner records `pending_turn` and clears the marker only after recording a determinate outcome. Active writers, missing completion records, unfinished turns and uncertain termination block asking, closing and reopening. Reconcile the saved records and confirm termination before resuming; changing the closed/open flag does not resolve these conditions.

A terminal session-loading failure starts one fresh session within the same turn timeout. It retains prior questions, captured attachments and replies as context and records `replacement` in the reply and log, with the old session under `retired_sessions` in the manifest. The original attempt stays in `turns/tN/`; the fresh attempt uses `turns/tN/fresh/`. Normal follow-ups then use the replacement session. A missing saved session ID is an incomplete record, not proof of a terminal native failure.
