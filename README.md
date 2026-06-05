# Skills

Personal collection of agent skills — portable instruction packages that teach AI agents how to perform specific, repeatable workflows.

Each skill is a directory with a `SKILL.md` file (YAML frontmatter + markdown instructions), optionally bundled with `references/`, `scripts/`, and `assets/`. Skills follow the [agentskills.io specification](https://agentskills.io/specification).

## Skills directory

| Skill                                               | Description                                                                                                                                     |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create, revise, and validate agent skills that follow the [agentskills.io](https://agentskills.io) format and practical skill-writing guidance. |

## Install

### Skills CLI

List skills in this repo:

```bash
npx skills add alannkl/skills --list
```

Install all skills (project-local):

```bash
npx skills add alannkl/skills --all -y
```

Add `-g` for a global install. Use `--skill <name>` instead of `--all` to install one skill.

**Manual** — copy or symlink a skill directory into your agent's skills path:

| Agent       | Typical path                                          |
| ----------- | ----------------------------------------------------- |
| Cursor      | `~/.cursor/skills/` or `.cursor/skills/` in a project |
| Claude Code | `~/.claude/skills/`                                   |

## License

MIT — see [LICENSE](LICENSE).
