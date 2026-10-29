---
name: write-agent-instructions
description: "Writes, edits, reviews, evaluates, and prunes agent instructions: skills, slash commands, AGENTS.md, CLAUDE.md, system or developer prompts, and prompt files or prompts inside application code. Use for any change to one of these, however small, including wording-only polishing or shortening and adding one rule to AGENTS.md; for any request to review, critique, evaluate, or improve one, including requests for advice only; and when packaging repeated instructions behind a name. Not for ordinary conversation or human-facing prose."
---

# Write agent instructions

Agent instructions are text a model or agent executes: skills and slash commands, `AGENTS.md` and `CLAUDE.md`, system and developer prompts, and task prompts written for an agent. In a mixed artifact, such as a prompt inside application code, change only the instruction content; the repository's own workflow owns code integration and runtime checks.

## Boundaries

- Answer planning-only requests in conversation: plans, designs, critiques, outlines, and discussions of instruction structure. For mixed requests, resolve the plan first and write files once the implementation path is clear.
- Treat named tools, skills, frameworks, and workflows as context for the plan; switch to file creation only on the user's explicit ask. When file-writing intent is ambiguous and edits would be surprising, ask before editing.
- A review-only or evaluation-only request stays read-only: check the artifact against this skill's rules and report findings in conversation.
- Existing explicit authorization carries forward. Ask only about unresolved scope or material preferences.

## References

Load a reference at the step named here when its condition holds, or where another pointer names it.

| Reference | Step | Load when |
| --- | --- | --- |
| `references/skill-mechanics.md` | 1 | Creating or reviewing a skill or slash command, or changing its name, invocation, description, packaging, bundled scripts, interfaces, or how its body tells the agent to run a bundled script. Not for other changes to body wording. |
| `references/pruning-instructions.md` | 2 | Pruning, renaming, or structurally reorganizing an existing artifact, including changes to its required sections, ordering, output formats, or loading behavior; recommending such a change in a review; or uncertainty about whether a change is structural. |
| `references/context-design.md` | 4 | Designing or changing retrieval or loading paths, such as choosing which sources an agent reads or retrieves at run time, moving an existing artifact's material into or out of a conditional reference, adding a load condition, or changing which branches reach an existing pointer's target; designing retained context or continuation state; an explicit request to design context management; or uncertainty about one of these decisions. Rewording a condition without changing its target or the branches it covers, and the ordinary placement of a new skill's own references, follow step 4 alone. A persistent file, a long task, or several agents are not reasons on their own. |
| `references/evaluating-instructions.md` | 1 for an explicit evaluation request, otherwise 5 or 6 | An explicit evaluation request, a consequential authorized behavior change (a removed, added, or changed safeguard or approval gate, consumer format, ordering, or load condition), a disputed no-op, or a change to an existing description or pointer condition that alters which cases reach it. Use the section that applies. |

## Workflow

1. Identify the job.
   - Name the artifact, the agent that executes it, the outcome the user wants, and the operation: create, wording edit, structural revision including pruning, review, or evaluation.
   - A wording edit, such as shortening or polishing, keeps every requirement. Removing, merging, or reordering requirements is a structural revision; make one only when the request calls for it.

2. Gather the material.
   - Ground new instructions in completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches, and identify what the executing agent gets wrong without them.
   - For an existing artifact, its current requirements are the baseline: explicit user preferences, constraints and permissions, necessary ordering, safeguards, and formats its consumers rely on.
   - When deciding where material lives, establish how the executing agent receives the artifact and what it can read, from the request, project docs, or the code that loads it.
   - Before writing a lesson as an instruction, check whether a lint rule, type, runtime check, script, or hook can enforce it. When enforcement fits in the artifact's own files, put it there and omit the prose rule; when it belongs in the target repo, recommend it rather than editing beyond the artifact.
   - Separate judgment and approval from mechanical steps, and give each mechanical step a script or a direct command where the executor can run one, choosing per the Scripts section of `references/skill-mechanics.md` when the choice is unclear.

3. Write for the outcome. Write each rule in the fewest words that state it; add detail or an example only for a failure you can name.
   - Start with what a finished run delivers and its required content. List terminal outcomes when the work can end more than one way; for audit, review, and maintenance work, include "nothing worth changing" as a complete result without padding the report.
   - Use ordered steps when sequence matters. Prescribe other steps, fixed headings, or templates only for fragile operations, cases the agent gets wrong by default, or formats another skill or tool consumes. Otherwise state the outcome and constraints; let the agent choose the method and form.
   - Give steps and sets of rules a checkable completion criterion where one naturally exists; prefer exhaustive phrasing ("every changed file reviewed") over vague phrasing ("review the changes"). Name concrete checks for judgment outcomes instead of forcing artificial metrics.
   - Anchor recurring concepts on leading words: established terms the user's prompts and the domain already use, repeated as the same token throughout. Collapse spelled-out enumerations and paraphrases into the word. Define a coined term where it first appears.
   - Write plain, precise sentences with concrete actions. Keep commands, flags, paths, and identifiers exact, and state real uncertainty.
   - State the target behavior. Keep a prohibition only as a guardrail, paired with what to do instead.
   - Write every line for the executing agent. Omit authoring rationale, request history, and explanations of the artifact's shape; keep a reason only when it informs a call the agent must make unaided. Write decided values, never verification status or staged values ("start at X, lower after measurement"); when a value is undecided, ask before writing.
   - Avoid time-sensitive facts unless the instructions say how to refresh them.
   - Keep a concept's definition, rules, and caveats together under one heading. Make defaults clear; mention alternatives only when they change a decision.
   - Make the workflow batch independent operations into one tool round. Batches stop at steps that need judgment or user authorization, and failures stay visible.
   - Make included examples concrete and realistic.
   - A rule the user dictates goes in as one line in the file's own terms, as short as its neighbours, with no examples or directives they did not give.
   - Prefer instructions that work with no other skill installed. When the workflow needs another skill or document, name it and load it at the step that uses it, rather than copying or summarizing its guidance.

4. Place the material.
   - Always-loaded text, such as an instruction file, a system prompt, or a model-invoked skill's description, returns on every later request that retains or reassembles it and in every agent context that inherits it. Text loaded on demand may also stay for later turns. Give always-loaded text the strictest retention bar.
   - Keep what every run needs in the main file, including universal constraints. Move material that only some branches need behind a pointer, unless the pointer and the extra read would cost about as much as the material. A reference that every run loads organizes the text but saves no context.
   - A pointer names its target and a load condition the agent can recognize without first reading the target. Write it as a plain path, such as `references/context-design.md`, not a Markdown link, and name sections in prose, such as "the Scripts section". When a pointer fails to fire on a branch that needs its target, sharpen the wording before inlining the material.
   - Place every pointer target where the executing agent can retrieve it. Before moving material out of the text that agent receives, confirm that agent will reach the new location and add the pointer or loading step that gets it there. When you cannot confirm that, keep the material inline, supply it with the task, or ask how to deliver it.
   - Count the full read path: the main file plus every reference, skill, and inherited instruction a run loads, including `refine-it` and `shorten-it` when used. Loading a reference adds to context and clears nothing earlier.
   - Weigh agent context against human load: material with no pointer depends on the human remembering to invoke it. Spend that load only where human judgment matters.
   - Treat a long main file, such as a `SKILL.md` body over ~100 non-empty lines, as a sign that branch material belongs behind a pointer, not as a length target; completeness and correctness outrank size. Reduce the main file by moving branch material, not by fragmenting text or adding headings.

5. Prune, then polish.
   - When creating an artifact or making a structural revision, remove within the requested scope the requirements and sub-steps the agent can reliably infer from the outcome, whole sentences that change no behavior relative to the executing agent's default, and material that no longer bears on the task.
   - Preserve explicit user preferences, necessary ordering, consumer-required formats, and safeguards against specific likely or costly failures. A stated user preference stays even if the agent would follow it unprompted; if it predates the request, list it as a suggested removal. Keep a safeguard only when you can name the failure and why the executing agent's default would miss it. Keep each retained requirement's meaning exactly; report an ambiguity you notice instead of resolving it in the artifact.
   - Before removing a rule because another source covers it, confirm the source applies everywhere the rule does, including tasks an exception or load condition excludes from it; otherwise keep the rule for the uncovered cases or ask; don't widen where the other source applies to make it cover them.
   - In a wording edit, report pure emphasis that the polish cuts as a removal.
   - Name the action, not the steps the agent takes on its own: "apply `references/x.md`", not "read and apply `references/x.md`". State each rule once, where it applies; merge duplicates, including gotchas that merely negate a workflow rule.
   - Load `refine-it`, then `shorten-it`, and run each over the whole of every instruction artifact created or structurally revised, and over the changed text of other edits, or the whole artifact when the request is artifact-wide. Polish text the user supplied as well, unless they asked for it verbatim.
   - Name each command, tool, and path once, as what its step acts on. An identifier in parentheses after words that name the same thing is a duplicate: rewrite "load settings from the config file (`config.yaml`)" as "load settings from `config.yaml`", and "upload the build (`aws s3 cp`, the deploy skill)" as "upload the build with `aws s3 cp`, which the deploy skill documents". Keep what the identifier does not say, such as purpose, conditions, arguments, or where it is documented.
   - Compare the polished text with the post-pruning draft. Restore any change the polish introduced to triggers, requirements, permissions, workflow order, or other operational meaning. Leave wording unchanged where neither pass improves it.

6. Check and report.
   - Check the artifact against its job and every format a consumer requires. Keep terminology consistent across the main file and its references, and verify each pointer, documented command, argument, and output against its target.
   - A wording edit needs a meaning review, not behavior runs. Outside the evaluation reference's conditions, suggest useful behavior checks rather than running them.
   - Report what changed, each intentionally removed requirement separately from wording changes, suggested removals, the checks performed, and material limits.
