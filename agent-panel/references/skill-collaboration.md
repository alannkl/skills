# Collaborating on an existing skill

Use this procedure when the user asks a team to execute any existing skill. Naming the skill is sufficient; no additional mode toggle is needed. The selected skill defines the process and output, and the panel coordinates participation.

## Prepare one shared execution

1. Read the selected `SKILL.md` and every reference required for the current work. Freeze the same instructions and evidence for all participants, including the goal, settled decisions and acceptance criteria. Include the instructions in the brief or provide frozen references each participant can read.
2. Designate one coordinator. The host owns the skill's sequence, human interaction, approval gates and shared decision record. A panel leader coordinates its assigned agent work. Give members responsibilities within the current stage rather than asking each to repeat the complete skill independently.
3. Preserve the skill's dependencies, serial steps, role separation and verification requirements. Parallelize only work that those rules allow. Choose a collaboration preset when the user leaves it unspecified and state the choice before starting. Resolve the selected skill's own modes according to its instructions.
4. Put the current stage and its expected contribution in each bounded panel brief. Share the same decision record with every participant. Distinguish user decisions, verified facts, agent recommendations and open questions.

## When the skill needs user input

Use this discussion loop only when the selected skill requires a user decision or unresolved context. Otherwise continue through its own stages.

Before asking the user, have participants propose and discuss the next question. Check whether available evidence already answers it, which uncertainty matters most, what depends on the answer, and which options and trade-offs the user needs. The coordinator consolidates the discussion and asks one question at a time unless the selected skill permits batching independent questions.

After the user answers, record the answer and share it with the team. Have participants examine its implications, conflicts with settled decisions and remaining ambiguity. Resolve those issues before advancing to dependent decisions. Ask a follow-up when the answer leaves a material gap; agent agreement cannot supply an unstated user preference or authorization.

Keep the human interaction in the host. Participants propose questions and analyze answers; they do not each open a separate conversation with the user. When an answer is required, retain the pending question and wait rather than treating silence as a decision.

## Deliver one result

Maintain one shared work product and decision record, using the selected skill's prescribed artifacts when applicable. The integrator combines contributions, and required reviewers check the same final result against the brief and the skill's requirements.

Complete the shared skill only when all required stages and decisions are resolved or explicitly deferred under its rules. Deliver one final output in its required format, with unresolved work identified. A panel's agreement on a stage artifact, such as a proposed question, is not completion of the whole skill.

## Using the current runner

The host currently interprets the selected skill and manages its stages. The runner executes bounded preset rounds; it does not parse `SKILL.md` into a schedule or automatically forward participant questions to the user.

Use panel runs for the current bounded assignment and carry the shared instructions and decision record into subsequent briefs. `--pause-between-rounds` provides a host checkpoint within a run. A substantive brief update restarts opening rounds within the original limits; use a new run when a later stage needs new bounds or execution settings. New runs create fresh sessions, so carry forward the required context explicitly.

Do not add a skill-specific runner branch or task profile. The host supplies the selected instructions, current stage and output requirements through the existing brief and result envelope.
