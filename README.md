# Skills

Personal collection of agent skills — portable instruction packages that teach AI agents how to perform specific, repeatable workflows.

Each skill is a directory with a `SKILL.md` file (YAML frontmatter + markdown instructions), optionally bundled with `references/`, `scripts/`, and `assets/`. Skills follow the [agentskills.io specification](https://agentskills.io/specification).

## Skills directory

| Skill                                               | Description                                                                                                                                     |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create, revise, and validate agent skills that follow the [agentskills.io](https://agentskills.io) format and practical skill-writing guidance. |

## Install

**Skills CLI** (recommended):

```bash
# List available skills
npx skills add alannkl/skills --list

# Install one skill (project-local)
npx skills add alannkl/skills --skill create-agent-skill -y

# Install globally
npx skills add alannkl/skills --skill create-agent-skill -g -y
```

**Manual** — copy or symlink a skill directory into your agent's skills path:

| Agent       | Typical path                                          |
| ----------- | ----------------------------------------------------- |
| Cursor      | `~/.cursor/skills/` or `.cursor/skills/` in a project |
| Claude Code | `~/.claude/skills/`                                   |

## License

MIT — see [LICENSE](LICENSE).
