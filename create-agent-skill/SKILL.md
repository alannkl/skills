---
name: create-agent-skill
description: Create Agent Skill files from reusable workflows, domain expertise, project conventions, or shortcut instructions. Use when the user asks to create or update a skill or slash command, package repeated instructions behind a name, or evaluate and iterate on an existing skill.
---

# Create agent skill

## Boundaries

- Answer planning-only requests in conversation, including plans, designs, critiques, outlines, requirements, and discussions of skill structure. For mixed requests, resolve the plan first and write files once the implementation path is clear.
- Treat named tools, skills, frameworks, and workflows as context for the plan; switch to file creation only on the user's explicit ask.

## Workflow

1. Confirm scope.
   - Identify the concrete artifact to create or update: skill directory, `SKILL.md`, references, scripts, assets, or inventory docs.
   - If file-writing intent is ambiguous and edits would be surprising, ask for confirmation before editing.
   - Identify the task, workflow, project convention, or domain the skill covers.
   - For a shortcut that packages instructions the user retypes, write it directly and stop. Name it per step 2, use user-invoked frontmatter with a one-line description, and put the instructions in the body.
   - Capture the prompts, contexts, files, and workflows that should trigger it.
   - Note adjacent requests and near-misses that should not trigger it.
   - Ground the skill in completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches. Collect the reference material it should preserve.
   - Before drafting, separate judgment and approval from mechanical operations. Use [Scripts](#scripts) to assign each mechanical sequence to an existing tool, script, or direct command. Then choose supporting references, assets, templates, or sample files.
   - Before writing a lesson as instructions, check whether a lint rule, type, runtime check, or script can enforce it. Put enforcement in the skill's own artifacts, such as a bundled script or hook, when it fits there, and omit the prose rule. When enforcement belongs in the target repo, recommend it rather than editing beyond the skill.

2. Choose the skill name and location.
   - Use a directory name that matches the `name` field: 1-64 characters of lowercase letters, numbers, and hyphens.
   - Do not start or end with a hyphen, or use consecutive hyphens.

3. Write `SKILL.md`.
   - Start with YAML frontmatter containing at least `name` and `description`.
   - Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they carry useful information.
   - Make the skill model-invoked only when the agent must invoke it on its own or another skill must load it. Its description stays in context on every turn, so follow the Description pattern section. Otherwise set `disable-model-invocation: true` and use a one-line human-facing description without trigger lists. A user-invoked skill costs no context, and typing its name still invokes it.
   - When user-invoked skills become hard to remember, suggest one user-invoked router skill that names the others and when to use each. Update the router whenever a routed skill is added, renamed, or removed.
   - Do not restate the description in the body. When the skill needs activation or scope rules the description cannot carry, put them in a `## Boundaries` section; skip the section when the description is already clear, and put execution defaults in the workflow steps.
   - Focus the body on procedures, defaults, examples, gotchas, scripts, and validation steps.
   - Define what a finished run delivers, listing terminal outcomes when the work can end more than one way. For audit, review, and maintenance skills, include "nothing worth changing" as a complete result without padding the report.
   - Anchor recurring concepts on leading words: compact terms the user's prompts and the domain already use, repeated as the same token across the description and body. Collapse spelled-out enumerations and paraphrases into the word instead of restating the idea in new phrasing.
   - Give workflow steps a checkable done-condition where one naturally exists, and prefer exhaustive phrasing ("every changed file reviewed") over vague phrasing ("review the changes"). For judgment steps with no objective criterion, cover their outcome with concrete checks in a final validation step instead of forcing an artificial metric.
   - Write every body line for the agent executing the skill. Omit authoring rationale, request history, and explanations of the skill's shape.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Prefer a self-contained skill that works with no other skill installed. When the workflow genuinely needs another skill, declare the dependency explicitly: name it and instruct the agent to load it at the step that uses it. Do not copy or summarize that skill's guidance as a substitute for the dependency.

4. Apply progressive disclosure.
   - Keep what every run needs in `SKILL.md`. Move material needed only by some branches into supporting files, behind pointers that name the branch that loads each one.
   - Treat ~100 non-empty body lines as a smell that inline material belongs behind a pointer, not a limit or target; prioritize completeness and correctness over size.
   - A narrow instruction-only skill needs no supporting files: a single `SKILL.md` with the shortest workflow that covers the decisions the agent would get wrong, plus gotchas, examples, and validation only where they prevent likely mistakes.
   - Move detailed documentation into `references/`, and reusable templates, images, sample files, or static data into `assets/`; the Scripts section governs `scripts/`. Keep supporting resources one level deep, relative to the skill directory.

5. Review the result.
   - Present the draft when scope is uncertain or the skill encodes domain-specific preferences. Ask whether it covers the use cases, what is missing or unclear, and what should be more or less detailed.
   - Keep terminology consistent across `SKILL.md` and supporting files.
   - Check remaining mechanical sequences against [Scripts](#scripts) and verify documented arguments and outputs against the bundled scripts.
   - For model-invoked skills, sanity-check the description against realistic positive prompts and near-miss negative prompts. Revise wording that is too broad or too narrow.
   - If formal evals would be useful, suggest them as a next step for the user; do not run manual evals as part of this workflow. When the user asks to evaluate, prune, or iterate on an existing skill, load `references/evaluating-skills.md`.

## Description pattern

For model-invoked skills, keep the description under 1024 characters, in third person, with this structure:

```md
description: [What the skill enables]. Use when [specific user intents, keywords, contexts, or file types].
```

Make the first sentence say what the skill does, front-loading the vocabulary the user actually types. Start the second sentence with `Use when`, listing one trigger per distinct branch the skill handles; collapse synonyms that rename the same branch, and cut identity the first sentence already carries. Add a `do not use for` clause only for a real near-miss the triggers would otherwise catch.

Prefer:

```md
description: Review accessibility issues in React interfaces and suggest concrete fixes. Use when the user asks for accessibility review, WCAG checks, keyboard navigation fixes, or ARIA guidance for React components.
```

Avoid vagueness, and avoid synonym-stuffing one branch:

```md
description: Helps with accessibility.
```

```md
description: ... Use when the user asks to review, check, audit, inspect, examine, or assess accessibility.
```

## Scripts

- Reuse existing tools first. Add a script only when the workflow is expected to repeat and the script combines several commands to reduce round trips or improve reliability; a single command stays a direct command. Prefer direct commands when workflow variants would complicate a script.
- Leave judgment and authorization with the agent; scripts must expose failures that affect the next decision.
- If using one-off commands, pin versions and state prerequisites.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Give scripts concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout with diagnostics on stderr.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.
- Run bundled scripts and exact commands end to end once before delivery; a skill whose executable content has not run is still a draft. Exercise destructive or stateful operations through their dry-run, help, or confirmation paths or against disposable fixtures, never against real targets. Suggest trigger tests and comparative evals as a next step.

## Starter shape

```md
---
name: skill-name
description: Do a specific reusable task. Use when the user asks for concrete intents, contexts, or file types that should trigger this skill.
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
- The instructions cover what the agent would likely get wrong without the skill and omit what it already knows.
- The workflow batches independent operations into one tool round. Batches stop at steps that need judgment or user authorization, and failures stay visible.
- Keep environment-derived facts in the environment that owns them. Document unwritten conventions, reasons, and gotchas it cannot supply. At each bundled-script call site, describe the required and optional arguments, defaults, outputs, and exit behavior the agent needs to run it without a separate help lookup. Keep these summaries aligned with the scripts; leave implementation details in code.
- Every instruction should change behavior in some situation. Cut sentences no agent could act on differently, such as "check your tools", "use judgment", or "be thorough", and hedges that restate what the agent's environment already guarantees.
- State each rule once, where it applies. Cut restatements of a rule elsewhere in the skill, including gotchas that only negate a rule the workflow already states.
- Keep a concept's definition, rules, and caveats under one heading, without duplicating or scattering them.
- Defaults are clear; alternatives appear only when they change a decision.
- Every prohibition names what to do instead.
- Reserve prescriptive steps for fragile operations; for flexible tasks, explain intent.
- When included, examples are concrete and realistic, and validation catches common mistakes.
