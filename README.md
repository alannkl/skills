# Skills

Agent skills for repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available Skills

| Skill                                               | Description                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create agent skills from reusable workflows, domain expertise, or project conventions. Aligned with [`writing-for-agents`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md).                                                                         |
| [`brainstorm`](brainstorm/SKILL.md)                 | Host a structured brainstorming session as both facilitator and participant, from problem framing through divergent ideation to an actionable shortlist.                                                                                                                                            |
| [`coding-discipline`](coding-discipline/SKILL.md)   | Apply disciplined engineering habits for simple, scoped, maintainable, well-structured agent-written code. Based on [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md).                                                      |
| [`code-review`](code-review/SKILL.md)               | Produce findings-led code review reports for concrete code changes.                                                                                                                                                                                                                                 |
| [`commit-message`](commit-message/SKILL.md)         | Draft accurate Conventional Commit messages from real git changes.                                                                                                                                                                                                                                  |
| [`document-code`](document-code/SKILL.md)           | Improve source-code understanding by adding only useful comments, docstrings, or focused docs without changing behavior.                                                                                                                                                                            |
| [`explain-code`](explain-code/SKILL.md)             | Explain code at any scope — a completed change, a module, or the whole codebase — with an optional quiz that surfaces understanding gaps and an optional interactive micro-world for complex logic.                                                                                                 |
| [`grill-to-plan`](grill-to-plan/SKILL.md)           | Turn vague ideas and plans into clear decisions through scoped questioning. Based on [`grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) and [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs). |
| [`handoff`](handoff/SKILL.md)                       | Create a compact temporary handoff so another agent can continue the current conversation.                                                                                                                                                                                                          |
| [`refine-it`](refine-it/SKILL.md)                   | Refine written artifacts for clarity and readiness while preserving intent and scope.                                                                                                                                                                                                               |
| [`shorten-it`](shorten-it/SKILL.md)                 | Shorten text while preserving meaning, tone, and important details.                                                                                                                                                                                                                                 |
| [`simplify-code`](simplify-code/SKILL.md)           | Simplify source code for clarity and maintainability while preserving behavior. Based on [`code-simplifier`](https://github.com/anthropics/claude-code/blob/main/plugins/pr-review-toolkit/agents/code-simplifier.md).                                                                              |

Most skills are user-invoked (`disable-model-invocation: true`): they load only when you type `/<name>`, and cost no always-loaded context. Five are model-invoked so agents reach them on their own when the ask arrives in natural language: `coding-discipline` (auto-loads before code work), `code-review`, `commit-message`, `simplify-code`, and `document-code`.

## Installation

### Skills CLI

List the skills in this repo:

```bash
npx skills add alannkl/skills --list
```

Install every skill globally:

```bash
npx skills add alannkl/skills --all -g -y
```

Omit `-g` for a project-local install. Use `--skill <name>` instead of `--all` to install a single skill.

To remove a skill, use `npx skills remove --skill <name> -g -y` (omit `-g` for project-local). Run `npx skills remove -g` to pick skills interactively. `--all` removes every installed skill in that scope, not just this repo.

### Manual

Copy or symlink a skill directory into your agent's skills path:

| Scope   | Universal (Cursor, Codex, Claude Code, and others) | Agent-specific (also supported)          |
| ------- | -------------------------------------------------- | ---------------------------------------- |
| Global  | `~/.agents/skills/`                                | `~/.cursor/skills/`, `~/.claude/skills/` |
| Project | `.agents/skills/`                                  | `.cursor/skills/`, `.claude/skills/`     |

If an agent does not read `~/.agents/skills/` directly, symlink from there:

```bash
ln -sfn ~/.agents/skills/commit-message ~/.cursor/skills/commit-message
```

To uninstall manually, delete the skill directory (and any symlinks) from the same paths.

## Recommended Skills

External skills that pair well with this repo:

- [`writing-for-agents`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md) — the reference on writing documents agents consume: skills, `AGENTS.md`/`CLAUDE.md`, and docs behind pointers. [`create-agent-skill`](create-agent-skill/SKILL.md) applies its levers in condensed form; install the full reference when authoring or reviewing agent-facing docs.

  ```bash
  npx skills add mattpocock/skills --skill writing-for-agents -g -y
  ```

- [`unslop`](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) — cut AI tells from any writing. [`refine-it`](refine-it/SKILL.md) and [`shorten-it`](shorten-it/SKILL.md) improve structure and length; unslop strips the patterns that make text read as generated. Model-invoked, so agents load it on their own once installed.

  ```bash
  npx skills add cursor/plugins --skill unslop -g -y
  ```

## AGENTS.md

Besides skills, this repo includes [`AGENTS.md`](AGENTS.md) — the Collaboration Constitution: task-agnostic rules so the agent itself leads the collaboration — surfacing assumptions, defining done, holding scope, pushing back on real issues. It is the agent-side counterpart to [Working with Agents](docs/working-with-agents.md), and it is live in this repo (with `CLAUDE.md` symlinked to it), so agents working here already follow it.

### Using it yourself

Unlike skills, the constitution is not installed — it is meant to be always loaded. Copy the whole of [AGENTS.md](AGENTS.md) into an always-loaded instruction file:

| Scope   | File                                              |
| ------- | ------------------------------------------------- |
| Global  | `~/.claude/CLAUDE.md`                             |
| Project | `CLAUDE.md` or `AGENTS.md` at the repository root |

Then fill in the **Project-specific instructions** section at the end. When extending the universal rules, add only what pays off in every session — anything more specific belongs in a skill, a doc, or the project section.

### Linking the coding-discipline skill

For coding projects with the [`coding-discipline`](coding-discipline/SKILL.md) skill installed, point the project-specific section at it so every session loads it before code work:

```markdown
## Project-specific instructions

### Coding Discipline

Before any code work, load the `coding-discipline` skill first and follow it.
Skip only for trivial formatting, pure prose edits, or explicitly throwaway
prototypes.
```

Referencing the skill by name works for any install scope. If your agent does not resolve skills by name, link the installed `SKILL.md` path instead (e.g. `.agents/skills/coding-discipline/SKILL.md` for a project-local install).

## Docs

Background notes and research behind these skills:

- [Philosophy](docs/philosophy.md) — a standalone article of personal beliefs about engineering with AI.
- [Working with Agents](docs/working-with-agents.md) — human-facing principles for directing an agent to complete tasks, synthesized from Anthropic, OpenAI, Microsoft Research, Ethan Mollick, Simon Willison, and academic human-AI collaboration research. Its agent-side counterpart is the [Collaboration Constitution](#agentsmd) above.
- [Codebase Structure Principles](docs/codebase-structure.md) — durable principles for organizing code around ownership, change patterns, dependency direction, and module boundaries.
- [Behavior-First Testing for Agentic Coding](docs/behavior-first-testing-for-agentic-coding.md) — a behavior-scaffold workflow that establishes intended behavior before the change's code or executable test mechanics exist to bias it.

## Repository Layout

```text
<skill-name>/
  SKILL.md
  references/  # optional supporting docs
  scripts/     # optional deterministic helpers
  assets/      # optional templates, images, or static data
```

## License

MIT — see [LICENSE](LICENSE).
