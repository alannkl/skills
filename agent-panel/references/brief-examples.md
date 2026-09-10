# Brief examples

Adapt these examples' goals, evidence, deliverables and acceptance criteria to the user's request. They illustrate briefs; the runner neither loads them nor assigns task categories.

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

Allocate observation slots for a fictional moon. Return the allocation and reasoning needed to verify it. Give each requested observer one slot, without overlaps, and satisfy every stated visibility constraint.

For any subject, specify the deliverable and checks in the brief and choose the required access; no new runtime type is needed.

## Continue after an answer

User follow-up: "Keep this document generic; the audience-specific guidance belongs in the individual skills. Which recommendations change?"

User decision: the shared document addresses communication for any audience. Revise the prior recommendation accordingly, retaining other settled decisions. Return the revised recommendation and explain what changed; do not edit files. Acceptance: every proposed change respects the generic document's scope, and the answer identifies any remaining uncertainty.

Send this brief through `--continue` with the active panel directory and `--follow-up` with this file. Resume the existing participants; they already took part in the earlier discussion.
