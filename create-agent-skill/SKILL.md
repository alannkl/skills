---
name: create-agent-skill
description: Create, revise, and validate Agent Skills that follow the agentskills.io format and practical skill-writing guidance. Use when the user asks to create an agent skill, write a SKILL.md file, package reusable agent instructions, optimize skill descriptions, or turn a repeated workflow into a portable skill.
---

# Create Agent Skill

Use this workflow to create a portable Agent Skill: a directory whose `SKILL.md` contains frontmatter plus concise instructions, with optional resources loaded only when needed.

## Workflow
1. Gather requirements.
   - Identify the task or domain the skill covers.
   - Capture the specific use cases and concrete user prompts that should trigger it.
   - Note any prompts that should not trigger it.
   - Decide whether it needs executable scripts, references, assets, templates, or just instructions.
   - Collect reference materials to include or summarize.
   - Ground the skill in real expertise: completed tasks, user corrections, project docs, runbooks, schemas, review comments, issues, or patches.

2. Choose the skill name and location.
   - Use a lowercase, hyphenated directory name that matches the `name` field and is 1-64 characters.
   - Use only lowercase letters, numbers, and hyphens.
   - Do not start/end with a hyphen or use consecutive hyphens.

3. Write `SKILL.md`.
   - Start with YAML frontmatter containing at least `name` and `description`.
   - Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they add useful information.
   - Keep the description under 1024 characters and write it in third person.
   - First sentence says what it does; second sentence starts `Use when` with triggers, adjacent near-misses, and when the skill should load.
   - Keep the body focused on procedures, defaults, examples, gotchas, scripts, and validation.

4. Apply progressive disclosure.
   - Keep `SKILL.md` as the core instructions the agent needs on every run.
   - Split files when `SKILL.md` exceeds 100 lines, content spans distinct domains, or advanced features are rarely needed.
   - Move detailed documentation into `references/`.
   - Move reusable templates, images, sample files, or static data into `assets/`.
   - Add scripts in `scripts/` only for deterministic operations that would otherwise be recreated repeatedly.
   - Keep references one level deep and say exactly when to load each file.

5. Review and validate the result.
   - Present the draft when scope is uncertain or the skill encodes domain-specific preferences.
   - Ask whether it covers the use cases, what is missing or unclear, and what should be more or less detailed.
   - Confirm the directory name matches the frontmatter `name`.
   - Confirm frontmatter parses as YAML.
   - Confirm `description` has specific trigger language and `SKILL.md` stays under 100 lines.
   - Avoid time-sensitive facts unless the skill tells the agent how to refresh them.
   - Keep terminology consistent across `SKILL.md` and references.
   - Try realistic positive prompts and near-miss negative prompts; revise broad or narrow descriptions.
   - For formal evals, read `references/evaluating-skills.md` only when the user asks to evaluate or benchmark a skill.

## Description Pattern
Use this shape:
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
- The skill is a coherent unit of reusable work, not a general knowledge dump.
- The instructions include what the agent would likely get wrong without the skill and omit what it already knows.
- Defaults are clear; alternatives are included only when they change the decision.
- Prescriptive steps are reserved for fragile operations; flexible tasks explain intent.
- Examples are concrete and realistic, and validation catches common mistakes.
