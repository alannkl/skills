---
name: create-agent-skill
description: Create Agent Skill files from reusable workflows, domain expertise, or project conventions. Use when the user asks to write, scaffold, implement, package, install, or update an actual SKILL.md file or skill directory; do not use for plan-only skill design unless the user explicitly asks to create files.
---

# Create Agent Skill

Use this workflow to create or update a portable Agent Skill: a focused `SKILL.md` plus optional supporting resources that load only when needed.

## Activation Boundary

- Use this skill only when the user wants skill files created or updated.
- Keep planning-only requests in planning mode. This includes plans, designs, critiques, outlines, requirements, and skill-shape discussions.
- If a request mixes planning and creation, resolve the plan before editing. Write files only after the implementation path is clear.
- Named tools, skills, frameworks, and workflows do not override the user's requested mode.

## Workflow

1. Confirm scope.
   - Identify the concrete artifact to create or update: skill directory, `SKILL.md`, references, scripts, assets, or inventory docs.
   - If file-writing intent is ambiguous and edits would be surprising, ask for confirmation before editing.
   - Identify the task, workflow, project convention, or domain the skill covers.
   - Capture the prompts, contexts, files, or workflows that should trigger it.
   - Note adjacent requests that should not trigger it.
   - Decide whether the skill needs instructions only or also references, scripts, assets, templates, or sample files.
   - Collect or summarize the reference material the skill should preserve.
   - Ground the skill in real expertise: completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches.

2. Choose the skill name and location.
   - Use a lowercase, hyphenated directory name that matches the `name` field and is 1-64 characters.
   - Use only lowercase letters, numbers, and hyphens.
   - Do not start or end with a hyphen, or use consecutive hyphens.

3. Write `SKILL.md`.
   - Start with YAML frontmatter containing at least `name` and `description`.
   - Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they add useful information.
   - Keep the description under 1024 characters and write it in third person.
   - Make the first sentence say what the skill does.
   - Start the second sentence with `Use when`; include trigger phrases, adjacent near-misses, and load conditions.
   - Focus the body on procedures, defaults, examples, gotchas, scripts, and validation steps.

4. Apply progressive disclosure.
   - Keep `SKILL.md` to the core instructions the agent needs on every run.
   - Use ~100 non-empty body lines as a reference point for when to split, not a hard limit or target.
   - Prioritize completeness and correctness over staying under that size. Never omit or weaken instructions just to fit.
   - Split files when `SKILL.md` approaches that reference point, content spans distinct domains, or advanced features are rarely needed.
   - Move detailed documentation into `references/`.
   - Move reusable templates, images, sample files, or static data into `assets/`.
   - Add scripts in `scripts/` only for deterministic operations that would otherwise be recreated repeatedly.
   - Keep supporting resources one level deep and state when to load each file.

5. Review and validate the result.
   - Present the draft when scope is uncertain or the skill encodes domain-specific preferences.
   - Ask whether it covers the use cases, what is missing or unclear, and what should be more or less detailed.
   - Confirm the directory name matches the frontmatter `name`.
   - Confirm frontmatter parses as YAML.
   - Confirm `description` has specific trigger language.
   - Check non-empty body line count (~100, excluding YAML frontmatter and blank lines) as a split cue, not a pass/fail limit.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Keep terminology consistent across `SKILL.md` and references.
   - Sanity-check the description against realistic positive prompts and near-miss negative prompts. Revise wording that is too broad or too narrow.
   - If formal evals would be useful, suggest them as a next step for the user; do not run manual evals as part of this workflow.

## Description Pattern

Use this structure:

```md
description: [What the skill enables]. Use when [specific user intents, keywords, contexts, file types, or workflow names].
```

Prefer:

```md
description: Review accessibility issues in React interfaces and suggest concrete fixes. Use when the user asks for accessibility review, WCAG checks, keyboard navigation fixes, or ARIA guidance for React components.
```

Avoid:

```md
description: Helps with accessibility.
```

## Scripts

- Prefer no script unless the operation is deterministic, repeated, or easy to get subtly wrong.
- If using one-off commands, pin versions and state prerequisites.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Scripts should provide concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout with diagnostics on stderr.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.

## Lightweight Skills

For narrow, instruction-only skills, keep the skill as small as practical and prefer a single-file `SKILL.md` with:

- Frontmatter containing `name` and a specific, trigger-focused `description`.
- The shortest workflow that covers the decisions the agent might get wrong.
- Gotchas only when they prevent likely mistakes.
- No `references/`, `scripts/`, `assets/`, templates, or other supporting files.

Add a short purpose paragraph only when the description alone is not enough to guide execution. Omit examples, sections, and validation steps unless they prevent likely failure.

Use the fuller structure when the skill needs reusable resources, fragile procedures, domain-specific references, deterministic scripts, or multi-step validation.

## Starter Shape

```md
---
name: skill-name
description: Do a specific reusable task. Use when the user asks for concrete intents, contexts, file types, or workflow names that should trigger this skill.
---

# Skill Name

## Quick Start

- Include a minimal working example when it clarifies use.

## Workflow

1. Follow the domain-specific procedure.
2. Use the default tool or format; mention alternatives only as escape hatches.
3. Validate output and fix failures before finalizing.

## Gotchas

- Add concrete mistakes the agent would make without this skill.
```

## Quality Bar

- Completeness and correctness beat brevity; a longer `SKILL.md` is fine when the workflow needs it.
- The skill is a coherent unit of reusable work, not a general knowledge dump.
- The instructions cover what the agent would likely get wrong without the skill and omit what it already knows.
- Defaults are clear; alternatives appear only when they change a decision.
- Reserve prescriptive steps for fragile operations; for flexible tasks, explain intent.
- Examples are concrete and realistic, and validation catches common mistakes.
