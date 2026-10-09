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

2. Resolve the sources and frame the learning. Load `study` first; its evidence contract governs every record and any existing report.
   - Accept raw sources (URLs, repositories, files, conversation transcripts) or an existing study report.
   - Unless the user names another level, learn transferable high-level ideas and principles: the problem each solves, its trade-offs, and when it applies. Frame `study`'s question and sub-questions around them for the job from step 1, or select lessons from a supplied report the same way. Use low-level details to show how a principle works, whether it fits the target, and how to apply it.
   - For raw sources, run `study` with that framing, the named sources as required seeds, and any source limits the user set. Follow its scouting, budget and pre-collection reporting rules. If it selects one collection unit, collect it directly without fan-out.
   - For transcripts, read [Session evidence](references/integration.md#session-evidence) before weighing their claims.
   - For a saved learn-from result, retain recorded `user decision` values unless the user changes them. Check each proposal against the current target and evidence; recommend reconsidering a recorded decision only when its `reconsider when` condition holds or new evidence invalidates its reason, and say what changed. Grade `not recorded` proposals normally. A past `picked` decision is not completion evidence or permission for new scope.

3. Build proposals at the chosen learning level. Group supporting details with the idea they support; split proposed changes only when the user can choose them independently. At the default level, a detail stands alone only to fix a demonstrated target defect. For every candidate, fill the [proposal record](references/integration.md#proposal-record) and give it a disposition:
   - **adopt**: a demonstrated gap, an expected improvement that outweighs the added complexity, and a check that will show the change worked. For target `none`, adopt on suitability for the stated job, expected benefit, complexity, and a check against the proposed approach;
   - **already satisfied**: an existing instruction, mechanism or design decision serves the same purpose, with its location, even if its wording or implementation differs;
   - **reject** or **defer**: with the reason and the condition that would reopen it.
   - Consensus among sources is one input. A demonstrated gap and fit with user-stated preferences decide; an inferred preference is weaker evidence of fit than a stated one.
   - Shape the result per [Output by target](references/integration.md#output-by-target).
   - An empty adopt list with the reasons recorded is a complete result.

4. Deliver the proposals, grouped by disposition and ranked by expected improvement: each adopt as its full proposal record, each other disposition as one line with its reason and its location or reconsideration condition.
   - Proceed to step 5 only within existing authorization; otherwise stop for the user's pick, including unattended.
   - Make `study`'s save offer here. When saving is authorized, follow its save rule and shape the file per [Saved result](references/integration.md#saved-result). Update the file whenever the user picks, declines, defers or changes a decision, including any stated revisit condition.

5. Apply the picked changes.
   - Make one coherent, independently valid change per edit set; coupled ideas may share one. A target that is not a file, such as a process, ends at the recommendation.
   - Run the target's own checks. For a skill, apply `create-agent-skill` as a checklist on the finished file.
   - Approval to edit is not approval to commit. Commit only when asked, with the source, the gap, and the claim IDs in the commit body.
   - Place provenance where a reader needs it: a README credit line when the artifact is substantially built on one source; inside the artifact only when a license requires it, when naming the source makes a surprising rule credible, or when correct application depends on knowing the origin.
   - Terminal outcomes: **applied and checked**; **applied, checks failed or unavailable**, naming the remaining issue; **proposals delivered**, awaiting the pick; **recommendation delivered**, for target `none`; **nothing worth changing**; **needs a target decision**.
