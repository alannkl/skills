---
name: study
description: Research a question from sources into an evidence-graded report, either one subject in depth or how several sources and approaches answer one question. Use when the answer must be built from sources rather than from what the agent already knows: how a tool, product, or system works under the hood, what the landscape of an area is, how others handle a problem, what the literature or the market says, or a survey or comparison of tools, prompts, or practices; also loaded by learn-from. Not for explaining code in the working tree, explaining a concept the agent already knows, or a single fact lookup.
---

# Study

## Workflow

1. Frame the study.
   - When the question's shape or sub-questions are ambiguous, ask once, at most a few questions, before framing. Unattended, frame on the safest reading and say so.
   - Write the question in one sentence and name its shape: **subject**, one thing and how it works or what is known about it, or **field**, how several sources or approaches answer one question. The shape is fixed here; thin discovery later is a coverage gap, never a reason to change it.
   - List the sub-questions the report must answer; for a field, the dimensions to compare. The stop test in step 4 runs against this list.
   - Set the budget: source count estimate, time, tokens, and whether web access is granted.
   - Read `references/evidence-contract.md`, the evidence contract. Every record in the study follows it.

2. Choose sources. Follow `references/research.md` for the scout and collector work orders.
   - Sources the user named are in and seed the scout. Skip scouting only when the user limits the study to the named sources.
   - Scout: a shallow sweep from the seeds that returns candidate sources, one line each, with no close reading.
   - Select collection units. A unit is one system, work, or author's source family at one version or surface. For a field, group candidates by family, a system, author, or school rather than a URL, and take one representative per family with the best primary access, plus every outlier that answers the question differently and every user-named source. Expect three to six units; take the whole field when it is small. For a subject, take the surfaces and versions the sub-questions need. Record each dropped candidate and the reason in the study header.
   - Before collecting, report the frame and selected units. Separate user-named sources from scouted additions, and give each addition's purpose and budget impact. Unless the user requires approval of additions, continue without waiting for a reply; when they do, request it in that report and leave additions uncollected until approved.
   - Collect independent named units first. Then apply any corrections received and reassess additions against the remaining budget. Record additions left out for budget or missing approval as dropped candidates, and deliver **partial** when consequential coverage gaps remain.

3. Collect.
   - Fill one source record per unit from primary material: the prompt, code, config, or vendor document. Secondary coverage fills gaps and is labeled as such. A source you cannot access is a coverage gap in the record.
   - Hand units to subagents when that is cheaper than reading them yourself. Each collector gets the contract and its unit and returns its source record in its reply. Read every returned record yourself.
   - Save every record in a working directory for the study. A rerun skips units whose record is already there.
   - Decide which claims will carry weight in the synthesis, then open each cited location and confirm it says what the record says. When the claim count makes it cheaper, hand the check to a subagent as a fixed procedure over the claims and locations; the choice of claims stays yours.

4. Synthesize and stop.
   - Stop when every sub-question is answered or its remaining uncertainty is explained. For a field, also require: every selected family covered; for each agreement, a counterexample search documented across the records and the dropped candidates' scout lines, with its result; and every disagreement documented, resolved or not. A family nobody checked is a coverage gap, not a confirmation. Reaching the source estimate is not a stop.
   - When the budget expires with consequential gaps, stop and deliver **partial**.
   - Write the synthesis yourself; check every cited claim in a subagent's draft against its record before keeping it.
   - A counterexample is a family that documents the opposite, or a surface of the same source that differs. Build the disagreement list from `contradicts` links and from agreements with a counterexample.
   - Carry every record's `gaps` and `limitations` into the header's coverage gaps.

5. Deliver.
   - In chat, deliver the report body per the contract's Report shape section, and offer to save it.
   - Save when the user names a path or accepts the offer: one file, the body followed by the `Evidence records` appendix, at the named path or else at `<dir>/study/<slug>.md` in the current project, where `<dir>` is the project's established research-report location, or `docs` when it has none.
   - Terminal outcomes: **complete**; **partial**, naming the sub-questions still open and why; **blocked**, when the sources that decide the question are inaccessible.

## Gotchas

- Provenance records where a claim came from; basis records what it establishes. Source code establishes control flow. A measurement establishes the reported outcome under its method and conditions; assess its relevance and causal limits before it carries weight.
- A vendor name is not one policy. Record the surface and version each claim belongs to; one vendor's plugin, hosted product, and CLI are separate units.
- Vendor metrics are self-reported unless the record cites an independent measurement.
- "Not documented" is a coverage gap on that source, never a claim that the source lacks the mechanism.
