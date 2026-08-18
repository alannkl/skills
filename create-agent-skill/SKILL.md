---
name: create-agent-skill
description: Create Agent Skill files from reusable workflows, domain expertise, or project conventions. Use when the user asks to write, scaffold, implement, package, install, or update an actual SKILL.md file or skill directory; do not use for plan-only skill design unless the user explicitly asks to create files.
---

# Create Agent Skill

## Boundaries

- Do not write files for planning-only requests. This includes plans, designs, critiques, outlines, requirements, and skill-shape discussions.
- If a request mixes planning and creation, resolve the plan first; write files only after the implementation path is clear.
- Treat named tools, skills, frameworks, and workflows as context, not permission to switch from planning to file creation.

## Workflow

1. Confirm scope.
   - Identify the concrete artifact to create or update: skill directory, `SKILL.md`, references, scripts, assets, or inventory docs.
   - If file-writing intent is ambiguous and edits would be surprising, ask for confirmation before editing.
   - Identify the task, workflow, project convention, or domain the skill covers.
   - Capture the prompts, contexts, files, and workflows that should trigger it.
   - Note adjacent requests and near-misses that should not trigger it.
   - Decide whether the skill needs instructions only or also references, scripts, assets, templates, or sample files.
   - Ground the skill in real expertise — completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches — and collect the reference material it should preserve.

2. Choose the skill name and location.
   - Use a directory name that matches the `name` field: 1-64 characters of lowercase letters, numbers, and hyphens.
   - Do not start or end with a hyphen, or use consecutive hyphens.

3. Write `SKILL.md`.
   - Start with YAML frontmatter containing at least `name` and `description`.
   - Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they carry useful information.
   - Write the description following the Description Pattern section.
   - Default to model-invocation. Only when the user says the skill should run solely by explicit invocation, set `disable-model-invocation: true` and write the description as a one-line human-facing summary without trigger lists.
   - Do not restate the description in the body. When the skill needs activation or scope rules the description cannot carry, put them in a `## Boundaries` section; skip the section when the description is already clear, and put execution defaults in the workflow steps.
   - Focus the body on procedures, defaults, examples, gotchas, scripts, and validation steps.
   - Give workflow steps a checkable done-condition where one naturally exists, and prefer exhaustive phrasing ("every changed file reviewed") over vague phrasing ("review the changes"). For judgment steps with no objective criterion, cover their outcome with concrete checks in a final validation step instead of forcing an artificial metric.
   - Write every body line for the agent executing the skill. Omit authoring rationale, request history, and explanations of the skill's shape.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Prefer a self-contained skill that works with no other skill installed. When the workflow genuinely needs another skill, declare the dependency explicitly: name it and instruct the agent to load it at the step that uses it. Do not copy or summarize that skill's guidance as a substitute for the dependency.

4. Apply progressive disclosure.
   - Keep `SKILL.md` to the core instructions the agent needs on every run.
   - Use ~100 non-empty body lines as a reference point for when to split, not a hard limit or target.
   - Prioritize completeness and correctness over size; never omit or weaken instructions just to fit.
   - Split files when `SKILL.md` approaches that reference point, content spans distinct domains, or advanced features are rarely needed.
   - Move detailed documentation into `references/`, and reusable templates, images, sample files, or static data into `assets/`; the Scripts section governs `scripts/`.
   - Keep supporting resources one level deep, relative to the skill directory, and state when to load each file.

5. Review the result.
   - Present the draft when scope is uncertain or the skill encodes domain-specific preferences. Ask whether it covers the use cases, what is missing or unclear, and what should be more or less detailed.
   - Keep terminology consistent across `SKILL.md` and supporting files.
   - For model-invoked skills, sanity-check the description against realistic positive prompts and near-miss negative prompts. Revise wording that is too broad or too narrow.
   - If formal evals would be useful, suggest them as a next step for the user; do not run manual evals as part of this workflow. When the user asks to evaluate, prune, or iterate on an existing skill, load `references/evaluating-skills.md`.

## Description Pattern

For model-invoked skills, keep the description under 1024 characters, in third person, with this structure:

```md
description: [What the skill enables]. Use when [specific user intents, keywords, contexts, or file types].
```

Make the first sentence say what the skill does. Start the second sentence with `Use when`; include trigger phrases, adjacent near-misses, and load conditions.

Prefer:

```md
description: Review accessibility issues in React interfaces and suggest concrete fixes. Use when the user asks for accessibility review, WCAG checks, keyboard navigation fixes, or ARIA guidance for React components.
```

Avoid:

```md
description: Helps with accessibility.
```

## Scripts

- Prefer a script when the operation is deterministic and either repeated or easy to get subtly wrong; otherwise use direct instructions or one-off commands.
- If using one-off commands, pin versions and state prerequisites.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Scripts should provide concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout with diagnostics on stderr.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.

## Lightweight Skills

For narrow instruction-only skills, keep the skill as small as practical and prefer a single-file `SKILL.md` with:

- The shortest workflow that covers the decisions the agent might get wrong.
- Gotchas, examples, and validation steps only when they prevent likely mistakes.
- No `references/`, `scripts/`, `assets/`, templates, or other supporting files.

Use the fuller structure when the skill needs reusable resources, fragile procedures, domain-specific references, deterministic scripts, or multi-step validation.

## Starter Shape

```md
---
name: skill-name
description: Do a specific reusable task. Use when the user asks for concrete intents, contexts, or file types that should trigger this skill.
---

# Skill Name

## Workflow

1. Follow the domain-specific procedure.
2. Use the default tool or format; mention alternatives only as escape hatches.
3. Validate output and fix failures before finalizing.

## Gotchas

- Add concrete mistakes the agent would make without this skill.
```

## Quality Bar

- The skill is a coherent unit of reusable work, not a general knowledge dump.
- The instructions cover what the agent would likely get wrong without the skill and omit what it already knows.
- Every instruction should change behavior in some situation. Cut sentences no agent could act on differently — "check your tools", "use judgment", "be thorough" — and hedges that restate what the harness already guarantees.
- State each rule once, where it applies. Cut restatements of a rule elsewhere in the skill, including gotchas that only negate a rule the workflow already states.
- Defaults are clear; alternatives appear only when they change a decision.
- Every prohibition names what to do instead.
- Reserve prescriptive steps for fragile operations; for flexible tasks, explain intent.
- When included, examples are concrete and realistic, and validation catches common mistakes.
