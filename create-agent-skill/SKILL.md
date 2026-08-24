---
name: create-agent-skill
description: Create Agent Skill files from reusable workflows, domain expertise, or project conventions.
disable-model-invocation: true
---

# Create Agent Skill

## Boundaries

- Answer planning-only requests — plans, designs, critiques, outlines, requirements, skill-shape discussions — in conversation; for mixed requests, resolve the plan first and write files once the implementation path is clear.
- Treat named tools, skills, frameworks, and workflows as context for the plan; switch to file creation only on the user's explicit ask.

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
   - Choose invocation by who must reach the skill. Make it model-invoked only when the agent must fire it on its own or another skill must load it; its description then stays in context on every turn, so write it following the Description Pattern section. Otherwise set `disable-model-invocation: true` and write the description as a one-line human-facing summary without trigger lists — zero context cost, and typing the name still invokes it.
   - When user-invoked skills multiply past easy recall, suggest a router skill: one user-invoked skill that names the others and when to reach for each.
   - Do not restate the description in the body. When the skill needs activation or scope rules the description cannot carry, put them in a `## Boundaries` section; skip the section when the description is already clear, and put execution defaults in the workflow steps.
   - Focus the body on procedures, defaults, examples, gotchas, scripts, and validation steps.
   - Anchor recurring concepts on leading words: compact terms the user's prompts and the domain already use, repeated as the same token across the description and body. Collapse spelled-out enumerations and paraphrases into the word instead of restating the idea in new phrasing.
   - Give workflow steps a checkable done-condition where one naturally exists, and prefer exhaustive phrasing ("every changed file reviewed") over vague phrasing ("review the changes"). For judgment steps with no objective criterion, cover their outcome with concrete checks in a final validation step instead of forcing an artificial metric.
   - Write every body line for the agent executing the skill. Omit authoring rationale, request history, and explanations of the skill's shape.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Prefer a self-contained skill that works with no other skill installed. When the workflow genuinely needs another skill, declare the dependency explicitly: name it and instruct the agent to load it at the step that uses it. Do not copy or summarize that skill's guidance as a substitute for the dependency.

4. Apply progressive disclosure.
   - Decide branch by branch: keep in `SKILL.md` what every run needs; push what only some branches reach into a supporting file behind a pointer that states when to load it.
   - Treat ~100 non-empty body lines as a smell that inline material belongs behind a pointer, not a limit or target; prioritize completeness and correctness over size.
   - A narrow instruction-only skill needs no supporting files: a single `SKILL.md` with the shortest workflow that covers the decisions the agent would get wrong, plus gotchas, examples, and validation only where they prevent likely mistakes.
   - Move detailed documentation into `references/`, and reusable templates, images, sample files, or static data into `assets/`; the Scripts section governs `scripts/`. Keep supporting resources one level deep, relative to the skill directory.

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

- Prefer a script when the operation is deterministic and either repeated or easy to get subtly wrong; otherwise use direct instructions or one-off commands.
- If using one-off commands, pin versions and state prerequisites.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Scripts should provide concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout with diagnostics on stderr.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.

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

- State the correct behavior for a case the agent gets wrong by default; name the mistake itself only when the correct form alone won't prevent it.
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
