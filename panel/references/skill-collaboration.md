# Collaborating on an existing skill

Use these instructions when running an existing skill in either pair or panel mode. The selected skill defines the process and output. Choose the collaboration mode and any panel preset through Prepare in `SKILL.md`.

## Prepare one shared execution

1. Read the selected `SKILL.md` and every reference needed for the work. Freeze shared instructions and evidence, including the goal, settled decisions and acceptance criteria, in the brief or in references all participants can read.
2. The host owns the skill's sequence, human interaction, approval gates and decision record in both modes.
3. Preserve the skill's dependencies, serial steps, role separation and verification requirements. Parallelize only where allowed; resolve the skill's own modes by its instructions.
4. State the current stage and expected contribution in each brief or consultation question. Share one decision record distinguishing user decisions, verified facts, agent recommendations and open questions.

In panel mode, the preset allocates the current stage: the leader assigns complementary parts in `leader-members`, peers propose the split in `flat-peers`, and every participant independently produces the stage's whole deliverable in `independent-discussion`. The host writes neither assignments nor viewpoint roles.

## Pair mode

The host executes the selected skill and maintains its work product. Follow Pair mode in `SKILL.md` for consultations, required review and the turn ledger. Apply the routing rule under Keep the panel in the chat in `SKILL.md` after the first delivered answer; a stage boundary alone adds no consultation requirement. Advice informs the host's decisions and never supplies approval.

For routed follow-ups, use `consult.py ask`, described under Consultant in `references/usage.md`, with the saved consultation, including relevant user answers, corrections, stage context and new evidence. Keep it open after delivery and close it only on stop or reset. On an explicit request to resume after stopping, use `consult.py reopen` with the new question and the decisions made while stopped.

## When the skill needs user input

Use this loop when the skill requires a user decision or missing context; otherwise continue its stages.

In pair mode, the host checks the evidence, asks the needed questions and examines the answers, consulting under the rules above. In panel mode, apply the routing rule and use the participant discussion below when independent input is needed.

When a question to the user is routed, have participants propose and discuss it before the host asks: whether evidence already answers it, which uncertainty matters most, what depends on the answer, and which options and trade-offs the user needs. The host consolidates their discussion and asks one question at a time unless the skill permits batching independent questions.

Record the answer. If the question was routed, have participants examine the answer's implications, conflicts with settled decisions and remaining ambiguity; otherwise the host examines it and applies the routing rule to any new issue. Either way, resolve material gaps before dependent decisions. Agent agreement cannot supply an unstated user preference or authorization.

Panel participants propose questions and analyze answers through the host, without separate user conversations. In both modes, keep required questions pending until answered; silence is not a decision.

## Deliver one result

Maintain one shared work product and decision record, using prescribed artifacts where applicable. In pair mode, the host completes any required review and delivers the result with the consultation ledger. For a routed panel assignment, the integrator combines contributions and required reviewers check the same final result against the brief and skill requirements. Direct follow-ups use the host's normal answer format.

Complete the skill only when all required stages and decisions are resolved or explicitly deferred under its rules. Deliver one output in the required format, identifying unresolved work. Agreement on a stage artifact, such as a proposed question, does not complete the whole skill. Completing the selected skill leaves the pair or panel active for later questions in this chat.

## Using the current runner

This section applies to panel mode. The host interprets the skill and manages its stages. The runner executes bounded preset rounds; it neither schedules `SKILL.md` steps nor forwards questions to the user.

Run the current bounded assignment, then apply the routing rule to user answers, corrections and subsequent stages. For routed work, continue the saved panel per Continuing the conversation in `references/usage.md`, carrying shared instructions and decisions into the follow-up brief.

Use `--pause-between-rounds` for host decisions inside a discussion; brief updates restart opening rounds within that discussion's original limits. A continued discussion renews those limits. Changed execution settings require an explicit reset under the existing authorization rules.

Supply the skill instructions, current stage and output requirements through the existing brief and result envelope.
