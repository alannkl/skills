# Grill to Plan Session Record Format

Use the session record as the current state of the discussion, not as a full transcript. Use the plan as the forward-looking synthesis that comes out of it.

## Location

- Each session gets one folder: `plans/{yyyy-mm-dd}-{slug}/` containing `session.md` (the session record) and `plan.md` (the final plan).
- The folder name is a stable ID: the date is the session start date, fixed when the folder is created. When a session resumes on a later day, never rename the folder; update the `Date:` fields inside the documents instead.
- Use an existing repo convention instead when the project already has a planning, discovery, or decision-log folder.
- Create `session.md` when the first question is answered or the first decision is made; create `plan.md` when the session concludes with a synthesis.
- Create missing parent directories the first time you write a document.

## Session Record Shape (`session.md`)

```md
# {Goal Or Plan Name}

Date: {yyyy-mm-dd}
Status: In progress | Complete | Paused

## Current Understanding

{Concise restatement of the goal, scope, and end state.}

## Question Log

### Q1: {Short question title}

Context: {What was known before asking.}

Question: {The exact decision question.}

Recommendation: {The agent's recommended answer and why.}

Discussion: {Short summary of debate, objections, and alternatives.}

Conclusion: {Settled decision, explicit deferral, or documented disagreement.}

Follow-up: {Optional next action or dependency.}

## Decisions

- {Decision}: {Reason}

## Open Questions

- {Question or deferred branch}

## Risks / Watchpoints

- {Risk and why it matters}
```

## Plan Shape (`plan.md`)

```md
# {Goal Or Plan Name} — Plan

Date: {yyyy-mm-dd}

{One-paragraph statement of the goal and end state.}

## Plan

{The final synthesis: what to build and in what order, led by the parts most likely to be revised.}

## Acceptance Criteria

- {Falsifiable check confirmed with the user; the plan is done when every check passes}

## Open Questions

- {Deferred decision and when it must be resolved}

## Risks / Watchpoints

- {Risk and why it matters}

See [session.md](session.md) for the decision history.
```

## Rules

- Write both documents as cross-session hand-offs. Implementation happens in a fresh session without this conversation, so every decision, constraint, verified research finding, and integration contract the implementer needs must be in these documents or linked from them.
- Update `session.md` after each resolved question before asking the next one.
- Keep entries concise enough to guide the next question.
- Phrase open questions as questions, not assertions, so the human's answer is the resolution.
- Do not duplicate ADRs; link to them when they exist.
- Keep `plan.md` forward-looking; do not restate the question log or the reasoning behind settled decisions — link to `session.md` instead.
- Overwrite `plan.md` when a resumed session changes the plan; the pair should always reflect the latest settled state.
