---
name: learn-from
description: Improve anything you maintain, such as a skill, doc, config, codebase, plan, or process, from how others do the same job. Studies the sources, grades each idea by evidence and fit, proposes adopt, reject, or defer, and applies the changes the user picks.
disable-model-invocation: true
argument-hint: <sources or study report> [into <target>]
---

# Learn From

## Workflow

1. Resolve the target. It is one of:
   - **artifact**: anything the user maintains and can change, such as a skill, doc, config, codebase module, or process;
   - **idea**: a plan, notes, or brainstorm output with no artifact yet;
   - **none**: the user says there is nothing of their own yet. The job is then the user's stated question.
   - When the user named none of these, follow [Target discovery](references/integration.md#target-discovery). One clear match: name it as an assumption and continue with analysis only; edit authority is unchanged. Several candidates: ask. No candidate: say so and offer to create a new artifact from the study or to stop at the study. Unattended: recommend the strongest candidate and stop before any edit.
   - For an artifact or idea, read it as it is: its stated job, structure, and constraints, and the preferences on record in instruction files, memory, and prior decisions. Mark each preference as user-stated or inferred.

2. Resolve the sources. Load `study` first; its evidence contract governs every record and any existing report.
   - Accept raw sources (URLs, repositories, files, conversation transcripts) or an existing study report.
   - For raw sources, run `study` with the job from step 1 as the question, limited to the named sources unless the user asks for a wider search. One named source still produces source records, with no fan-out.
   - For transcripts, read [Session evidence](references/integration.md#session-evidence) before weighing their claims.

3. Build proposals. For every candidate idea in the study, fill the [proposal record](references/integration.md#proposal-record) and give it a disposition:
   - **adopt**: a demonstrated gap, an expected improvement that outweighs the added complexity, and a check that will show the change worked. For target `none`, adopt on suitability for the stated job, expected benefit, complexity, and a check against the proposed approach;
   - **already satisfied**: the target does this, with the location;
   - **reject** or **defer**: with the reason and the condition that would reopen it.
   - Consensus among sources is one input. A demonstrated gap and fit with user-stated preferences decide; an inferred preference is weaker evidence of fit than a stated one.
   - Shape the result per [Output by target](references/integration.md#output-by-target).
   - An empty adopt list with the reasons recorded is a complete result.

4. Deliver the proposals, grouped by disposition and ranked by expected improvement: each adopt as its full proposal record, each other disposition as one line with its reason and location or reconsideration condition. Proceed to step 5 only within existing authorization; otherwise stop for the user's pick, including unattended.

5. Apply the picked changes.
   - Make one coherent, independently valid change per edit set; coupled ideas may share one. A target that is not a file, such as a process, ends at the recommendation.
   - Run the target's own checks. For a skill, apply `create-agent-skill` as a checklist on the finished file.
   - Approval to edit is not approval to commit. Commit only when asked, with the source, the gap, and the claim IDs in the commit body.
   - Place provenance where a reader needs it: a README credit line when the artifact is substantially built on one source; inside the artifact only when a license requires it, when naming the source makes a surprising rule credible, or when correct application depends on knowing the origin.
   - Terminal outcomes: **applied and checked**; **applied, checks failed or unavailable**, naming the remaining issue; **proposals delivered**, awaiting the pick; **recommendation delivered**, for target `none`; **nothing worth changing**; **needs a target decision**.
