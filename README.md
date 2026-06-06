# Skills

A personal collection of agent skills: portable instruction packages that teach AI agents repeatable workflows.

Each skill lives in its own directory with a `SKILL.md` file containing YAML frontmatter and markdown instructions. Skills may also include `references/`, `scripts/`, and `assets/`, and follow the [agentskills.io specification](https://agentskills.io/specification).

## Available Skills

| Skill                                               | Description                                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create, revise, and validate agent skills that follow the [agentskills.io](https://agentskills.io) format and practical skill-writing guidance.                                                                                                                                                                                                 |
| [`coding-discipline`](coding-discipline/SKILL.md)   | Apply disciplined software engineering habits that keep agent-written code simple, scoped, maintainable, and verifiable. Based on [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md), broadened for practical, production-ready engineering.                             |
| [`commit-message`](commit-message/SKILL.md)         | Draft clear Conventional Commit messages from real git state, using staged changes by default when they exist. Includes behavior-oriented bullets, explicit breaking-change or required-action notes, and a copyable commit command when appropriate.                                                                                           |
| [`grill-to-plan`](grill-to-plan/SKILL.md)           | Clarify casual ideas or stress-test plans, designs, and vague goals until they become decisions and an actionable plan. Based on [`grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) and [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs). |
| [`refine-it`](refine-it/SKILL.md)                   | Refine an existing artifact into a stronger, ready-to-use version while preserving its intent, scope, and direction. Useful for cleanup, final-pass editing, tightening, polishing, and clearer writing without silently redesigning the artifact.                                                                                              |

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
