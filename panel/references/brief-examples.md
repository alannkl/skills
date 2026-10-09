# Brief examples

Adapt these examples' goals, evidence, deliverables and acceptance criteria to the user's request. The runner does not load them.

In pair mode, the host does the work and the read-only consultant advises. Include the task context in the brief, then ask for objections or review. Follow Pair mode in `SKILL.md` to choose the consultations and completion criteria.

## Pair consultation examples

### Focused question

User request: "Ask Fable whether this retry policy risks duplicate payments." Give a second opinion on the attached policy, identifying the failure scenario and the evidence needed to resolve any uncertainty. One usable reply can complete this consultation; no separate approach or deliverable review is implied.

### Approach

The host is comparing two queueing approaches under the supplied service constraints. It plans to assess ordering, failure recovery, throughput and operating cost, then recommend one approach. Before it starts, challenge that plan: identify missing criteria, assumptions, risks and alternatives. Acceptance: the plan can produce a recommendation supported by the supplied constraints and identify any experiments still needed.

### Deliverable

The host's proposed queueing recommendation and evidence are attached. Review them against the service constraints and the criteria above. Identify unsupported claims, missed failure scenarios and reasons an alternative would fit better. State explicitly if there are no material findings. Acceptance: the recommendation addresses all four criteria and identifies remaining uncertainty.

## Compare alternatives

Compare two queueing approaches under the supplied service constraints. Return a recommendation with alternatives, trade-offs, assumptions and unresolved experiments. Assess ordering, failure recovery, throughput and operating cost. Include a diagram only if it explains the proposed flow.

## Investigate evidence

Determine what the supplied evidence establishes about the reported trend. Return a cited answer distinguishing observations from inference, resolving conflicting sources where possible, and stating uncertainty. Attribute important claims to sources. An inconclusive answer is valid when evidence is insufficient.

## Review a change

Review the exact supplied diff against its intended behavior. Return material findings with locations, failure scenarios and evidence. Validate disagreements and merge duplicates. Return an explicit empty findings list when no material defect is supported. Do not apply fixes.

## Implement behavior

Implement the specified behavior at the selected repository revision. Return assembled changes, a concise explanation and named check results. Cover supplied edge cases and preserve unrelated behavior. For competing solutions, choose one base and port useful improvements. For complementary work, resolve interfaces and integrate in dependency order.

## Diagnose a failure

Reproduce the symptom and establish its cause using the supplied logs, code and checks. Return the reproduction, causal evidence and remaining uncertainty. Keep source unchanged unless a correction is requested. A reproduction check may expect failure; specify its expected exit code explicitly.

## Produce finished writing

Write finished copy for the requested audience, purpose, tone, format and length. Preserve supplied facts and required points; identify assumptions separately when needed. Review against those constraints rather than imposing a standard report layout.

## An unfamiliar task

Allocate observation slots for a fictional moon. Return the allocation and the reasoning needed to verify it. Give each requested observer one slot, without overlaps, and satisfy every stated visibility constraint.

Any subject works the same way: specify the deliverable and checks in the brief and choose the required access.

## Continue after an answer

User follow-up: "Keep this document generic; the audience-specific guidance belongs in the individual skills. Which recommendations change?"

User decision: the shared document addresses communication for any audience. Revise the prior recommendation accordingly, retaining other settled decisions. Return the revised recommendation and explain what changed; do not edit files. Acceptance: every proposed change respects the generic document's scope, and the answer identifies any remaining uncertainty.

First apply the routing rule under Keep the panel in the chat in `SKILL.md`. An explanation of an earlier recommendation can stay with the host; a changed assumption that undermines it needs fresh consultation. In panel mode, resume the saved participants with `panel.py`, passing the active directory to `--continue` and this brief file to `--follow-up`.

In pair mode, put the routed follow-up and the host's current approach or proposed answer in the question, asking for objections or review as appropriate, and resume the saved consultation:

```bash
python3 scripts/consult.py ask /absolute/consult-dir --question /absolute/follow-up.md
```

See Consultant in `references/usage.md` for attachments and access settings. Reuse the saved session for each consultation.
