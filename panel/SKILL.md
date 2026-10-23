---
name: panel
description: Keep a multi-agent panel across harnesses, or read-only consultants, available in the current chat, consulting them when independent input is worth the cost and completing requested or promised reviews.
disable-model-invocation: true
---

# Panel

Choose between two modes:

- **Consult:** the host does the work with advice from read-only consultants, one by default.
- **Panel:** participants do the work while the host coordinates, using one of three presets: `independent-discussion`, `leader-members` or `flat-peers`.

Web retrieval is on by default in both modes. For tasks restricted to supplied evidence, set `execution.web: false` in the panel roster or pass `--no-web` when opening a consultant. Both modes need Python 3.10+ on Linux or macOS and authenticated harness CLIs; no Python packages are required.

## Keep the panel in the chat

Invocation, by slash command or explicit request, routes the first request through the selected consultants or panel under that mode's consultation and review rules. Every later message is a follow-up: route it to the saved participants when independent input would improve the result enough to justify the tokens and time; otherwise answer directly.

- **Always route** explicit requests such as "ask the panel" or "get Fable's opinion", with or without a slash command. Merely discussing the skill is not a request.
- **Route** important decisions, complex or uncertain reasoning, new ideas needing challenge and material changes. Judge by stakes, uncertainty and novelty, not by confidence in answering alone; when a consequential case is unclear, route it.
- **Route** a correction or clarification that undermines a reviewed assumption or conclusion before relying on that conclusion again, and mark the conclusion as needing fresh review.
- **Answer directly** routine clarification, explanation of existing results, status, presentation changes and straightforward work within settled decisions. A new message, action or small analysis is not by itself a reason to consult.

Complete every consultation or review the user requested, the host promised or a dispatched panel assignment requires. Only the user may waive one; routing discretion never excuses a failed consultation. Reconsult after a material change to a reviewed result, and once on a disputed finding before its final disposition; presentation-only changes need no new review. Consult with the agreed mode and roster; changing either follows the reset and authorization rules below, except adding or removing a consultant, covered in `references/consult-mode.md`.

Keep host answers distinct from panel conclusions or consultant advice, and claim review only for the result actually reviewed.

The selected consultants or panel stay available until the user stops it, resets it or asks to answer solo. Keep its mode, directory, resolved roster or model settings, adapter registrations, authorization and shared decisions in the persistent working record and any continuation handoff, along with user decisions, host actions, new evidence and standing routing preferences, which also go into the next consultation. At each new message, restore the record and read the saved manifest before dispatch. After context compaction, reload this skill and the active mode's reference.

- **Routed follow-up:** in panel mode, resume the saved panel as described under Continuing the conversation in `references/panel-mode.md`, passing `--fresh-sessions` when the recorded briefs, results and decisions carry everything the next assignment needs and keeping the saved sessions when it depends on context nobody recorded. In consult mode, `ask` the saved consultants. Reuse existing authorization and resolve changes outside it before launch.
- **Stop or answer solo:** close the panel or consultation without further participant work, keeping its directory and saved settings.
- **Resume or reopen, on explicit request:** `--reopen` for a stopped panel, `consult.py reopen` for each closed consultation, with the new question and the decisions made while stopped.
- **Reset:** close the old panel and prepare a new one with fresh sessions, retaining the old artifacts.
- **One-message solo exception, on explicit request:** answer solo, record any resulting user decisions and return to the routing rule afterward.

When a saved session is terminally unavailable on resume, the runner starts a fresh session with the recorded context and the same settings; report that replacement in either mode. Transient errors, permission denials and uncertain termination do not permit replacement.

In user-facing progress, reply headings, relayed advice and final ledgers, name each member or consultant by the short name of the model actually selected after any fallback, such as `Fable` or `Astra`. If names collide, append the participant ID or a stable session label, such as `Fable a` and `Fable b`, and show the mapping in the pre-launch report.

## Prepare

1. Write a brief defining the goal, scope, evidence, deliverable and acceptance criteria, adapting `references/brief-examples.md` when useful. To run an existing skill collaboratively, first read that skill and `references/skill-collaboration.md`.
2. Select the mode. Invoking `panel` alone selects consult mode with one consultant, and a request for several consultants or second opinions selects consult mode with that many; an explicit request for a panel, a group discussion or multiple agents doing the work selects panel mode. Honor an explicit mode or preset name: "consult" or "pair" selects consult mode, "independent" or "independent discussion" selects `independent-discussion`, "leader" or "leader and members" selects `leader-members`, and "peers" or "flat peers" selects `flat-peers`. Use the same criteria when running an interactive skill, without overriding that skill's own mode-selection rules.
3. Apply `references/consult-mode.md` for consult mode or `references/panel-mode.md` for panel mode, through preparation, running, follow-ups and delivery.

## Default roster

An unspecified panel roster has two participants; `references/consult-mode.md` sets how many consultants run and on which harnesses. Participants and consultants follow these per-harness defaults:

| Harness | Preferred model | Effort |
| --- | --- | --- |
| Claude Code | Claude Fable 5.1 | `high` |
| Codex | GPT-6 Astra | `high` |

1. Preserve explicit user choices and apply task-specific model restrictions only within their stated scope. Fill unspecified models and effort on matching harnesses from the table.
2. Resolve exact model identifiers for the installed harness and current account from current model listings or account availability evidence, consulting current official vendor guidance when identifiers or capability are unclear. If a preferred model is unavailable, choose that harness's most capable available model for general reasoning and coding, ranked by current model descriptions rather than names or speed/cost defaults; apply the same rule to other requested harnesses. Report fallbacks and reasons, or unresolved availability or ranking, before launch; never invent an identifier.
3. Set `high` explicitly where supported. If effort control exists but lacks `high`, disclose the supported choices and resolve effort before launch. Report harnesses without effort control.

## Deliver the current answer

For a direct follow-up, answer as the host without a new report or consultation ledger. For routed work, check the deliverable against every acceptance criterion, then deliver as the mode's reference directs. For another skill, also verify its completion rules and deliver its required output once for the team. Agreement on an intermediate question or proposal completes only that assignment. Deliver the requested content, data or files, including frozen files, the patch and verification evidence for file changes.
