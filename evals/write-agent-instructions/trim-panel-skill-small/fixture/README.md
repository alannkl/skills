# Skills

Agent skills for repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and Markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available skills

### Agent workflow

| Skill                                               | Description                                                                                                                                                                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`write-agent-instructions`](write-agent-instructions/SKILL.md) | Write, edit, review, evaluate, and prune instructions for agents: skills, slash commands, `AGENTS.md`, `CLAUDE.md`, and system or task prompts. Incorporates guidance from [`writing-for-agents`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md). |
| [`spawn-agent`](spawn-agent/SKILL.md)               | Spawn a headless coding-agent CLI run (`agy -p`, `claude -p`, `agent -p`, or `codex exec`) for one scoped subtask, with a shared workflow and one reference per supported harness.                                          |
| [`delegate`](delegate/SKILL.md)                     | Delegate bounded steps when cheaper than doing them inline, or faster at bounded extra cost when the user is waiting or has a deadline. Weigh the cost, choose a collector, runner, digester, or implementer, write the work order, check the returned record, and report a delegation ledger at delivery. |
| [`panel`](panel/SKILL.md)                           | Keep a multi-agent panel across harnesses, or read-only consultants, available in the current chat; consult them when independent input is worth the cost and complete requested or promised reviews. User-invoked.         |
| [`handoff`](handoff/SKILL.md)                       | Create a compact temporary handoff so another agent can continue the current conversation.                                                                                                                                  |
| [`retrospect`](retrospect/SKILL.md)                 | Mine recent sessions across projects and harnesses for repeated corrections and friction, then turn the lessons you pick into checks, rules, skill fixes, or hand-off briefs where each belongs. User-invoked.              |

## License

MIT. See [LICENSE](LICENSE).
