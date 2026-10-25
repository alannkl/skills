# Collaborating on an existing skill

When the user asks a team to execute an existing skill, naming it is sufficient; no mode toggle is needed. The skill defines the process and output; the panel coordinates participation.

## Prepare one shared execution

1. Read the selected `SKILL.md` and every reference needed for the work. Freeze shared instructions and evidence, including the goal, settled decisions and acceptance criteria, in the brief or references all participants can read.
2. Designate one coordinator. The host owns the skill's sequence, human interaction, approval gates and decision record. A panel leader coordinates assigned agent work. Assign stage responsibilities rather than having each member repeat the whole skill.
3. Preserve the skill's dependencies, serial steps, role separation and verification requirements. Parallelize only where allowed. Choose and announce a collaboration preset if unspecified; resolve the skill's own modes by its instructions.
4. State the current stage and expected contribution in each bounded panel brief. Share one decision record distinguishing user decisions, verified facts, agent recommendations and open questions.

## When the skill needs user input

Use this loop when the skill requires a user decision or missing context; otherwise continue its stages.

Before asking, have participants propose and discuss the next question: whether evidence already answers it, which uncertainty matters most, what depends on the answer, and which options and trade-offs the user needs. The host consolidates their discussion and asks one question at a time unless the skill permits batching independent questions.

Record and share the answer. Have participants examine its implications, conflicts with settled decisions and remaining ambiguity. Resolve those issues before dependent decisions, asking follow-up questions for material gaps. Agent agreement cannot supply an unstated user preference or authorization.

Participants propose questions and analyze answers through the host, without separate user conversations. Keep required questions pending until answered; silence is not a decision.

## Deliver one result

Maintain one shared work product and decision record, using prescribed artifacts where applicable. The integrator combines contributions; required reviewers check the same final result against the brief and skill requirements.

Complete the skill only when all required stages and decisions are resolved or explicitly deferred under its rules. Deliver one output in the required format, identifying unresolved work. Agreement on a stage artifact, such as a proposed question, does not complete the whole skill.

## Using the current runner

The host interprets the skill and manages its stages. The runner executes bounded preset rounds; it neither schedules `SKILL.md` steps nor forwards questions to the user.

Run the current bounded assignment, carrying shared instructions and decisions into subsequent briefs. Use `--pause-between-rounds` for host checkpoints. Substantive brief updates restart opening rounds within the original limits. Start a new run for stages needing new bounds or execution settings, carrying required context into its fresh sessions.

Supply the skill instructions, current stage and output requirements through the existing brief and result envelope; do not add a skill-specific runner branch or task profile.
