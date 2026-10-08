---
name: create-agent-skill
description: Writes or reviews agent skills and slash commands built from reusable workflows, domain expertise, project conventions, or shortcut instructions. Use before creating, editing, or reviewing any skill or slash-command file, and when the user asks to package repeated instructions behind a name or to evaluate or prune an existing skill.
---

# Create agent skill

## Boundaries

- Answer planning-only requests in conversation: plans, designs, critiques, outlines, requirements, and discussions of skill structure. For mixed requests, resolve the plan first and write files once the implementation path is clear.
- Treat named tools, skills, frameworks, and workflows as context for the plan; switch to file creation only on the user's explicit ask. When file-writing intent is ambiguous and edits would be surprising, ask before editing.
- To review an existing skill file, check it against this skill's rules and report findings in conversation.
- When the user asks to evaluate, prune, or iterate on an existing skill, load `references/evaluating-skills.md`.

## Workflow

1. Confirm scope.
   - Identify the concrete artifact to create or update: skill directory, `SKILL.md`, references, scripts, assets, or inventory docs.
   - Identify the task, workflow, project convention, or domain the skill covers.
   - For a shortcut that packages instructions the user retypes, skip steps 2–5 and 7: name it per step 3, give it user-invoked frontmatter with a one-line description, put the instructions in the body, then apply step 6.
   - Capture the prompts, contexts, files, and workflows that should trigger the skill, plus adjacent requests and near-misses that should not.

2. Gather and allocate the material.
   - Ground the skill in completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches. Collect the reference material it should preserve.
   - Before writing a lesson as instructions, check whether a lint rule, type, runtime check, or script can enforce it. When enforcement fits in the skill's own artifacts, such as a bundled script or hook, put it there and omit the prose rule; when it belongs in the target repo, recommend it rather than editing beyond the skill.
   - Separate judgment and approval from mechanical steps. Assign each mechanical step to a script or direct call per [Scripts](#scripts), then choose supporting references, assets, templates, or sample files.

3. Choose the skill name and location.
   - Name the directory to match the `name` field: 1-64 characters of lowercase letters, numbers, and single hyphens, starting and ending with a letter or number.

4. Write `SKILL.md`.
   - Start with YAML frontmatter containing at least `name` and `description`.
   - Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they carry information.
   - Make the skill model-invoked only when the agent must invoke it on its own or another skill must load it. Its description stays in context every turn; write it per [Description pattern](#description-pattern). Otherwise set `disable-model-invocation: true` and use a one-line human-facing description without trigger lists. A user-invoked skill costs no context, and typing its name still invokes it.
   - When user-invoked skills become hard to remember, suggest one user-invoked router skill that names the others and when to use each. Update the router whenever a routed skill is added, renamed, or removed.
   - Keep the description out of the body. When the skill needs activation or scope rules the description cannot carry, put them in a `## Boundaries` section; skip the section when the description is already clear, and put execution defaults in the workflow steps.
   - Focus the body on procedures, defaults, examples, gotchas, scripts, and validation steps.
   - Define what a finished run delivers, listing terminal outcomes when the work can end more than one way. For audit, review, and maintenance skills, include "nothing worth changing" as a complete result without padding the report.
   - Anchor recurring concepts on leading words: compact terms the user's prompts and the domain already use, repeated as the same token across the description and body. Collapse spelled-out enumerations and paraphrases into the word.
   - Give workflow steps a checkable done-condition where one naturally exists, and prefer exhaustive phrasing ("every changed file reviewed") over vague phrasing ("review the changes"). For judgment steps with no objective criterion, cover their outcome with concrete checks in a final validation step instead of forcing an artificial metric.
   - Write every body line for the agent executing the skill. Omit authoring rationale, request history, and explanations of the skill's shape.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Prefer a skill that works with no other skill installed. When the workflow genuinely needs another skill, name it and instruct the agent to load it at the step that uses it, rather than copying or summarizing its guidance.

5. Apply progressive disclosure.
   - Keep what every run needs in `SKILL.md`. Move material needed only by some branches into supporting files, behind pointers that name the branch that loads each one.
   - Treat ~100 non-empty body lines as a smell that inline material belongs behind a pointer, not a limit or target; completeness and correctness outrank size.
   - A narrow instruction-only skill needs no supporting files: a single `SKILL.md` with the shortest workflow that covers the decisions the agent would get wrong, plus gotchas, examples, and validation only where they prevent likely mistakes.
   - Move detailed documentation into `references/`, and reusable templates, images, sample files, or static data into `assets/`; the Scripts section governs `scripts/`. Keep supporting resources one level deep, relative to the skill directory.

6. Polish the instruction prose.
   - Load `refine-it`, then `shorten-it`, and run each over the whole of every instruction file created or edited.
   - Compare the polished text with the pre-polish version and restore any change to triggers, requirements, permissions, workflow order, or other operational meaning. Leave wording unchanged where neither pass improves it.

7. Review the result.
   - Present the draft when scope is uncertain or the skill encodes domain-specific preferences. Ask whether it covers the use cases, what is missing or unclear, and what should be more or less detailed.
   - Keep terminology consistent across `SKILL.md` and supporting files.
   - Check each mechanical step against [Scripts](#scripts). Verify documented arguments and outputs against the bundled scripts.
   - For model-invoked skills, sanity-check the description against realistic positive prompts and near-miss negative prompts. Revise wording that is too broad or too narrow.
   - If formal evals such as trigger tests or comparative runs would be useful, suggest them as a next step for the user; do not run manual evals as part of this workflow.

## Description pattern

For model-invoked skills, keep the description under 1024 characters, in third person, with this structure:

```md
description: [What the skill enables]. [Conditions that invoke it: specific user intents, keywords, contexts, or file types].
```

State what the skill does in the first sentence, front-loading the vocabulary the user actually types. In the second, state its invocation conditions, one trigger per distinct branch. Collapse synonyms for the same branch and omit details already covered by the first sentence. Write for model invocation; users can invoke any skill by name. Add an exclusion only for a real near-miss the triggers would otherwise catch.

Prefer:

```md
description: Reviews accessibility issues in React interfaces and suggests concrete fixes. Use when the user asks for accessibility review, WCAG checks, keyboard navigation fixes, or ARIA guidance for React components.
```

Avoid vagueness, and avoid synonym-stuffing one branch:

```md
description: Helps with accessibility.
```

```md
description: ... Use when the user asks to review, check, audit, inspect, examine, or assess accessibility.
```

## Scripts

- Script a mechanical step when it replaces several tool rounds with one, handles ordering, exact flags, or cleanup the agent would otherwise get wrong, condenses verbose output to what the next decision needs, or enforces a rule the skill would otherwise state in prose.
- Call a step directly when a script would not pay off: the agent can run it correctly as one shell line from the skill text, including a call to an existing tool, or flags for workflow variants would cost more than the direct calls they replace.
- Keep judgment and authorization with the agent. Scripts must expose failures that affect the next decision.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Give scripts concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout limited to what the next decision needs. Write full logs to a file and print its path. Keep full logs out of stderr, which also consumes context.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.
- At each bundled-script call site, describe the required and optional arguments, defaults, outputs, and exit behavior the agent needs to run it without a separate help lookup. Keep these summaries aligned with the scripts; leave implementation details in code.
- Run bundled scripts and exact commands end to end once before delivery. Exercise destructive or stateful operations through their dry-run, help, or confirmation paths or against disposable fixtures, never against real targets.

## Starter shape

```md
---
name: skill-name
description: Does a specific reusable task. Use when the user asks for concrete intents, contexts, or file types that should trigger this skill.
---

# Skill name

## Workflow

1. Follow the domain-specific procedure.
2. Use the default tool or format; mention alternatives only as escape hatches.
3. Validate output and fix failures before finalizing.

## Gotchas

- State the correct behavior for a case the agent gets wrong by default; name the mistake itself only when the correct form alone won't prevent it.
```

## Quality bar

- The skill is a coherent unit of reusable work, not a general knowledge dump.
- The instructions cover what the agent would likely get wrong without the skill.
- The workflow batches independent operations into one tool round. Batches stop at steps that need judgment or user authorization, and failures stay visible.
- Keep environment-derived facts in the environment that owns them. Document the unwritten conventions, reasons, and gotchas it cannot supply.
- Every instruction changes behavior in some situation. Cut sentences no agent could act on differently, such as "check your tools", "use judgment", or "be thorough", and hedges that restate what the agent's environment already guarantees.
- State each rule once, where it applies. Cut restatements of a rule elsewhere in the skill, including gotchas that only negate a rule the workflow already states.
- Keep a concept's definition, rules, and caveats together under one heading.
- Defaults are clear; alternatives appear only when they change a decision.
- Every prohibition names what to do instead.
- Reserve prescriptive steps for fragile operations; for flexible tasks, explain intent.
- When included, examples are concrete and realistic, and validation catches common mistakes.
