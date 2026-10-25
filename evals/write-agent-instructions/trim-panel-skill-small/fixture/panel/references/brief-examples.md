# Brief examples

Adapt these examples' goals, evidence, deliverables and acceptance criteria to the user's request. The runner does not load them.

In pair mode, put the task context in the brief, then ask for objections or review; Pair mode in `SKILL.md` sets which consultations to run and when they are complete.

## Pair consultation examples

### Focused question

User request: "Ask Fable whether this retry policy risks duplicate payments." Give a second opinion on the attached policy, identifying the failure scenario and the evidence needed to resolve any uncertainty. One usable reply can complete this consultation; no separate approach or deliverable review is implied.

### Approach

The host is comparing two queueing approaches under the supplied service constraints. It plans to assess ordering, failure recovery, throughput and operating cost, then recommend one approach. Before it starts, challenge that plan: identify missing criteria, assumptions, risks and alternatives. Acceptance: the plan can produce a recommendation supported by the supplied constraints and identify any experiments still needed.

### Deliverable

The host's proposed queueing recommendation and evidence are attached. Review them against the service constraints and the criteria above. Identify unsupported claims, missed failure scenarios and reasons an alternative would fit better. State explicitly if there are no material findings. Acceptance: the recommendation addresses all four criteria and identifies remaining uncertainty.

## Review a change

Review the exact supplied diff against its intended behavior. Return material findings with locations, failure scenarios and evidence. Validate disagreements and merge duplicates. Return an explicit empty findings list when no material defect is supported. Do not apply fixes.

## An unfamiliar task

Allocate observation slots for a fictional moon. Return the allocation and the reasoning needed to verify it. Give each requested observer one slot, without overlaps, and satisfy every stated visibility constraint.

Any subject works the same way: specify the deliverable and checks in the brief and choose the required access.

## Continue after an answer

User follow-up: "Keep this document generic; the audience-specific guidance belongs in the individual skills. Which recommendations change?"

User decision: the shared document addresses communication for any audience. Revise the prior recommendation accordingly, retaining other settled decisions. Return the revised recommendation and explain what changed; do not edit files. Acceptance: every proposed change respects the generic document's scope, and the answer identifies any remaining uncertainty.

First apply the routing rule under Keep the panel in the chat in `SKILL.md`. An explanation of an earlier recommendation can stay with the host; a changed assumption that undermines it needs fresh consultation. In panel mode, resume the saved participants with `panel.py`, passing the active directory to `--continue` and this brief file to `--follow-up`.

In pair mode, put the routed follow-up and the host's current approach or proposed answer in the question, asking for objections or review as appropriate, and resume each saved consultation:

```bash
python3 scripts/consult.py ask /absolute/pair/astra --question /absolute/follow-up.md
```

See Consultant in `references/usage.md` for attachments and access settings.
