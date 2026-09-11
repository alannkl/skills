# Collaborating on an existing skill

Use these instructions when running an existing skill in either pair or panel mode. The selected skill defines the process and output. Choose the collaboration mode and any panel preset through [Prepare](../SKILL.md#prepare).

## Prepare one shared execution

1. Read the selected `SKILL.md` and every reference needed for the work. Freeze shared instructions and evidence, including the goal, settled decisions and acceptance criteria, in the brief or references all participants can read.
2. The host owns the skill's sequence, human interaction, approval gates and decision record in both modes.
3. Preserve the skill's dependencies, serial steps, role separation and verification requirements. Parallelize only where allowed; resolve the skill's own modes by its instructions.
4. State the current stage and expected contribution in each brief or consultation question. Share one decision record distinguishing user decisions, verified facts, agent recommendations and open questions.

In panel mode, the preset determines allocation for the current stage: the leader assigns complementary parts in `leader-members`, peers propose the split in `flat-peers`, and every participant independently produces the current stage's whole deliverable in `independent-discussion`. The host writes neither assignments nor viewpoint roles.

## Pair mode

The host executes the selected skill and maintains its work product. Follow [Pair mode](../SKILL.md#pair-mode) for the required approach and deliverable consultations, reconsultation rules and turn ledger. These checkpoints apply to the skill task; a stage boundary alone adds no consultation requirement. Advice is evidence for the host to weigh and never supplies approval.

Continue the same saved consultation with [`consult.py ask`](usage.md#consultant). Include relevant user answers, corrections, stage context and updated evidence in subsequent questions. Keep the consultation open after delivering the skill's result; close it only on stop or reset.

## When the skill needs user input

Use this loop when the skill requires a user decision or missing context; otherwise continue its stages.

In pair mode, the host checks the evidence, asks the needed questions and examines the answers while following the checkpoints above. In panel mode, use the participant discussion below.

Before asking, have participants propose and discuss the next question: whether evidence already answers it, which uncertainty matters most, what depends on the answer, and which options and trade-offs the user needs. The host consolidates their discussion and asks one question at a time unless the skill permits batching independent questions.

Record and share the answer. Have participants examine its implications, conflicts with settled decisions and remaining ambiguity. Resolve those issues before dependent decisions, asking follow-up questions for material gaps. Agent agreement cannot supply an unstated user preference or authorization.

Panel participants propose questions and analyze answers through the host, without separate user conversations. In both modes, keep required questions pending until answered; silence is not a decision.

## Deliver one result

Maintain one shared work product and decision record, using prescribed artifacts where applicable. In pair mode, the host delivers the reviewed result and the current task's consultation ledger. In panel mode, the integrator combines contributions; required reviewers check the same final result against the brief and skill requirements.

Complete the skill only when all required stages and decisions are resolved or explicitly deferred under its rules. Deliver one output in the required format, identifying unresolved work. Agreement on a stage artifact, such as a proposed question, does not complete the whole skill. Completion of the selected skill leaves the pair or panel active for later questions in this chat.

## Using the current runner

This section applies to panel mode. The host interprets the skill and manages its stages. The runner executes bounded preset rounds; it neither schedules `SKILL.md` steps nor forwards questions to the user.

Run the current bounded assignment, then [continue the saved panel](usage.md#continuing-the-conversation) for user answers, corrections and subsequent stages. Carry shared instructions and decisions into follow-up briefs while resuming the same participant sessions. Use `--pause-between-rounds` for checkpoints inside a discussion; brief updates there restart opening rounds within its original limits. Each follow-up renews those limits. Stages needing changed execution settings require an explicit reset under the existing authorization rules.

Supply the skill instructions, current stage and output requirements through the existing brief and result envelope; do not add a skill-specific runner branch or task profile.
