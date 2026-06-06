# Grill to Plan Session Record Format

Use the session record as the current state of the discussion, not as a full transcript.

## Location

- Default location: `docs/grill-to-plan/{yyyy-mm-dd}-{slug}.md`.
- Use an existing repo convention instead when the project already has a planning, discovery, or decision-log folder.
- Create the document when the first question is answered or the first decision is made.

## Shape

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

## Rules

- Update the record after each resolved question before asking the next one.
- Keep entries concise enough to guide the next question.
- Do not duplicate ADRs; link to them when they exist.
