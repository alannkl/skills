---
name: adversarial-review
description: Adversarial code review that hunts material failures and returns structured findings with failure scenarios. Use when asked to review a diff, branch, or files adversarially. Never applies fixes; not for style passes.
---

# Adversarial review

Review for failure, not perfection. Raise the floor, not the ceiling. An empty blocking list is a successful review outcome.

The reviewer must bring fresh eyes. A context that authored the code tends to defend its own bugs. A context reviewing someone else's code already counts as fresh. If this context authored the code under review, the invoker must pass the skill to a fresh context.

## Inputs

1. **Scope.** The code under review: a diff, a branch against its base, or named files. If the invoker did not specify the scope, review the current branch's changes against its merge base.
2. **Brief.** The author's review brief, if one exists: intent, requirements satisfied, deliberate trade-offs, known limitations, and declared non-goals. Do not write findings that contradict its declared trade-offs.

## Charter

Hunt material failures only:

- correctness failures
- unmet explicit requirements
- security and data-loss risks
- realistic reliability issues
- invalid assumptions
- implementation paths unlikely to work

Treat speculative future requirements, abstraction or style preferences, unrelated refactors, generalized frameworks, and marginal improvements as non-blocking. List at most three under suggestions.

Every blocking finding must include a concrete **failure scenario**: the inputs, the state, and the wrong outcome. A finding without one is a suggestion.

## Output

Return this report as markdown:

```markdown
Verdict: PASS | REVISE | REJECT

## Blocking findings

### <id> [<severity>/<confidence>] <claim, one sentence> at <file:line>

<failure scenario: these inputs, this state, this wrong outcome>

## Non-blocking suggestions (max 3)

- ...
```

Assign severity as critical/high/medium/low based on impact and likelihood. Assign confidence as high/med/low.

Return the report and stop. Do not soften findings or apply fixes.
