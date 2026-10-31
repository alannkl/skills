# Skill mechanics

Use this when creating or reviewing a skill or slash command, or when changing its name, invocation, description, packaging, bundled scripts, or interfaces. The workflow in `SKILL.md` still governs the writing.

## Shortcuts

For a shortcut that packages instructions the user retypes, name it per the Name and layout section, make it user-invoked per the Invocation section with a one-line description, put the user's instructions in the body, then apply steps 5 and 6 of `SKILL.md`. Keep every instruction the user gave; keep their exact wording only when they asked for it verbatim. Skip the other steps.

## Scope and splitting

- Make each skill a coherent unit of reusable work, not a general knowledge dump.
- Split off a model-invoked skill only when a distinct trigger word the user actually types should reach it on its own, or another skill must load it. Its description adds always-loaded context, so that independent reach must be worth it.
- Put reference that several skills need in one place: a model-invoked skill that holds the reference, which other skills can load, or a plain file outside the skill system that any skill can point at. Use the plain file when the target harness prevents the consuming skills from loading each other.

## Name and layout

- Name the directory to match the `name` field: 1-64 characters of lowercase letters, numbers, and single hyphens, starting and ending with a letter or number.
- A narrow instruction-only skill needs only `SKILL.md`.
- Update any inventory that lists skills, such as a README table or a router skill.
- Move detailed documentation into `references/`, and reusable templates, images, sample files, or static data into `assets/`; the Scripts section governs `scripts/`. Keep supporting files one level deep, referenced by paths relative to the skill directory.

## Invocation

- Start `SKILL.md` with YAML frontmatter containing at least `name` and `description`; quote the description. Add optional fields such as `license`, `compatibility`, `metadata`, or `allowed-tools` only when they carry information.
- Make the skill model-invoked only when the agent must invoke it on its own or another skill must load it. Its description returns on every request where the harness supplies the skill list to the model; write it per the Description pattern section.
- Otherwise set `disable-model-invocation: true`, use a one-line human-facing description without trigger lists, and add `agents/openai.yaml` setting `policy.allow_implicit_invocation` to an unquoted `false`, because Codex ignores the frontmatter field. Typing the skill's name still invokes it. A harness that honors neither setting still lists the skill to the model, so check the target harness before relying on a user-invoked skill costing no context.
- When user-invoked skills become hard to remember, suggest one user-invoked router skill that names the others and when to use each. Update the router whenever a routed skill is added, renamed, or removed.
- Keep the description out of the body. When the skill needs activation or scope rules the description cannot carry, put them in a `## Boundaries` section; skip the section when the description is already clear, and put execution defaults in the workflow steps.

## Description pattern

Before writing a description, list the prompts, contexts, and files that should trigger the skill and the near-misses that should not. For model-invoked skills, keep the description under 1024 characters, in third person, with this structure:

```md
description: "[What the skill enables]. [Conditions that invoke it: specific user intents, keywords, contexts, or file types]."
```

State what the skill does in the first sentence, front-loading the vocabulary the user actually types. In the second, state its invocation conditions, one trigger per distinct branch. Collapse synonyms for the same branch and omit details already covered by the first sentence. Write for model invocation; users can invoke any skill by name. Add an exclusion only for a real near-miss the triggers would otherwise catch. For workflows that publish, send, or change external state, a check, review, or readiness trigger needs a body branch that stops before that action; add the branch or leave the trigger out.

Prefer:

```md
description: "Reviews accessibility issues in React interfaces and suggests concrete fixes. Use when the user asks for accessibility review, WCAG checks, keyboard navigation fixes, or ARIA guidance for React components."
```

Avoid vagueness, and avoid synonym-stuffing one branch:

```md
description: "Helps with accessibility."
```

```md
description: "... Use when the user asks to review, check, audit, inspect, examine, or assess accessibility."
```

Check a new description against realistic matching and near-miss prompts, revise it if too broad or too narrow, and report both sets. A change to an existing description that alters which cases reach it uses the Trigger checks section of `references/evaluating-instructions.md` instead.

## Scripts

- Script a mechanical step when it replaces several tool rounds with one, handles ordering, exact flags, or cleanup the agent would otherwise get wrong, condenses verbose output to what the next decision needs, or enforces a rule the skill would otherwise state in prose.
- Call a step directly when a script would not pay off: the agent can run it correctly as one shell line from the skill text, including a call to an existing tool, or flags for workflow variants would cost more than the direct calls they replace.
- Keep judgment and authorization with the agent. Scripts must expose failures that affect the next decision.
- If bundling scripts, make them self-contained, non-interactive, idempotent, and runnable from the skill root with relative paths.
- Make scripts run under both macOS and Linux tools, with no GNU-only flags.
- Give scripts concise `--help`, helpful errors, meaningful exit codes, safe defaults, and structured stdout limited to what the next decision needs. Write full logs to a file and print its path. Keep full logs out of stderr, which also consumes context.
- For destructive or stateful operations, include dry-run or explicit confirmation flags.
- At each bundled-script call site, describe the required and optional arguments, defaults, outputs, and exit behavior the agent needs to run it without a separate help lookup. Keep these summaries aligned with the scripts; leave implementation details in code.
- Run bundled scripts and exact commands end to end once before delivery. Exercise destructive or stateful operations through their dry-run, help, or confirmation paths or against disposable fixtures, never against real targets.

## Starter shape

```md
---
name: skill-name
description: "Does a specific reusable task. Use when the user asks for concrete intents, contexts, or file types that should trigger this skill."
---

# Skill name

<Deliverable, required content, and constraints.>

Done when: <completion criterion>.
Check: <concrete command or comparison, when applicable>.

## Gotchas

- State the correct behavior for a case the agent gets wrong by default; name the mistake itself only when the correct form alone won't prevent it.
```
