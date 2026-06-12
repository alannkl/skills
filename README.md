# Skills

A personal collection of agent skills: portable instruction packages that teach AI agents repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available Skills

| Skill                                               | Description                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create agent skills from reusable workflows, domain expertise, or project conventions.                                                                                                                                                                                                              |
| [`coding-discipline`](coding-discipline/SKILL.md)   | Apply disciplined engineering habits for simple, scoped, maintainable agent-written code. Based on [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md).                                                                       |
| [`code-review`](code-review/SKILL.md)               | Produce findings-led code review reports for concrete code changes.                                                                                                                                                                                                                                 |
| [`commit-message`](commit-message/SKILL.md)         | Draft accurate Conventional Commit messages from real git changes.                                                                                                                                                                                                                                  |
| [`document-code`](document-code/SKILL.md)           | Improve source-code understanding by adding only useful comments, docstrings, or focused docs without changing behavior.                                                                                                                                                                            |
| [`grill-to-plan`](grill-to-plan/SKILL.md)           | Turn vague ideas and plans into clear decisions through scoped questioning. Based on [`grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) and [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs). |
| [`refine-it`](refine-it/SKILL.md)                   | Refine written artifacts for clarity and readiness while preserving intent and scope.                                                                                                                                                                                                               |
| [`shorten-it`](shorten-it/SKILL.md)                 | Shorten text while preserving meaning, tone, and important details.                                                                                                                                                                                                                                 |
| [`simplify-code`](simplify-code/SKILL.md)           | Simplify source code for clarity and maintainability while preserving behavior. Based on [`code-simplifier`](https://github.com/anthropics/claude-code/blob/main/plugins/pr-review-toolkit/agents/code-simplifier.md).                                                                              |

## Docs

Background notes and research behind these skills:

- [Working with Agents](docs/working-with-agents.md) — human-facing principles for directing an agent to complete tasks, synthesized from Anthropic, OpenAI, Microsoft Research, Ethan Mollick, Simon Willison, and academic human-AI collaboration research.

## Repository Layout

```text
<skill-name>/
  SKILL.md
  references/  # optional supporting docs
  scripts/     # optional deterministic helpers
  assets/      # optional templates, images, or static data
```

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

**Manual** — copy or symlink a skill directory into your agent's skills path:

| Scope   | Universal (Cursor, Codex, Claude Code, and others) | Agent-specific (also supported)          |
| ------- | -------------------------------------------------- | ---------------------------------------- |
| Global  | `~/.agents/skills/`                                | `~/.cursor/skills/`, `~/.claude/skills/` |
| Project | `.agents/skills/`                                  | `.cursor/skills/`, `.claude/skills/`     |

If an agent does not read `~/.agents/skills/` directly, symlink from there:

```bash
ln -sfn ~/.agents/skills/commit-message ~/.cursor/skills/commit-message
```

## License

MIT — see [LICENSE](LICENSE).
