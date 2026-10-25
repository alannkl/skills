# Skills

Agent skills for repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and Markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available skills

### Foundation

Loaded before the work starts rather than for a task. Wire both into your instruction file; see [Using it yourself](#using-it-yourself).

| Skill                                             | Description                                                                                                                                                                                                                                    |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`constitution`](constitution/SKILL.md)           | The Collaboration Constitution as an installable skill: universal rules for how the agent leads the collaboration. Mirrors [`AGENTS.md`](AGENTS.md); always loaded.                                                                            |
| [`coding-discipline`](coding-discipline/SKILL.md) | Apply disciplined engineering habits for simple, scoped, maintainable, well-structured agent-written code. Based on [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md). |

### Agent workflow

| Skill                                               | Description                                                                                                                                                                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`create-agent-skill`](create-agent-skill/SKILL.md) | Create agent skills from reusable workflows, domain expertise, or project conventions. Aligned with [`writing-for-agents`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md). |
| [`spawn-agent`](spawn-agent/SKILL.md)               | Spawn a headless coding-agent CLI run (`agy -p`, `claude -p`, `agent -p`, or `codex exec`) for one scoped subtask, with a shared workflow and one reference per supported harness.                                          |
| [`panel`](panel/SKILL.md)                           | Keep N agents across different harnesses in the current chat, resume their discussion on follow-ups, and verify each combined result; or pair the host with one read-only consultant for second opinions. User-invoked.     |
| [`handoff`](handoff/SKILL.md)                       | Create a compact temporary handoff so another agent can continue the current conversation.                                                                                                                                  |

### Coding

| Skill                                       | Description                                                                                                                                                                                                            |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`simplify-code`](simplify-code/SKILL.md)   | Simplify source code for clarity and maintainability while preserving behavior. Based on [`code-simplifier`](https://github.com/anthropics/claude-code/blob/main/plugins/pr-review-toolkit/agents/code-simplifier.md). |
| [`document-code`](document-code/SKILL.md)   | Improve source-code understanding by adding only useful comments, docstrings, or focused docs without changing behavior.                                                                                               |
| [`explain-code`](explain-code/SKILL.md)     | Explain a completed change, a module, or the whole codebase, with an optional quiz to surface understanding gaps and an optional interactive micro-world for complex logic.                                            |
| [`commit-message`](commit-message/SKILL.md) | Draft accurate Conventional Commit messages from real git changes.                                                                                                                                                     |

### Reviewing

| Skill                                               | Description                                                                                                                                                                                                                                                                   |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`code-review`](code-review/SKILL.md)               | Produce findings-led code review reports for concrete code changes.                                                                                                                                                                                                           |
| [`adversarial-review`](adversarial-review/SKILL.md) | Hunt material failures in a diff, branch, or files. Return structured findings with failure scenarios, but never apply fixes.                                                                                                                                                 |
| [`review-triage`](review-triage/SKILL.md)           | Triage review findings as the code's owner. Validate each, weigh fix cost against deployed complexity, and return dispositions instead of fixing everything.                                                                                                                  |
| [`review-panel`](review-panel/SKILL.md)             | Run a parallel panel of reviewer models, then merge and triage findings. Fixes are user-gated by default; `/review-panel auto-fix` approves them upfront. Spawns several agent sessions (cost scales with preset); strongest with multiple harnesses installed. User-invoked. |

### Planning

| Skill                                     | Description                                                                                                                                                                                                                                                                                         |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`brainstorm`](brainstorm/SKILL.md)       | Host a structured brainstorming session as both facilitator and participant, from problem framing through divergent ideation to an actionable shortlist.                                                                                                                                            |
| [`grill-to-plan`](grill-to-plan/SKILL.md) | Turn vague ideas and plans into clear decisions through scoped questioning. Based on [`grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) and [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs). |

### Writing

| Skill                               | Description                                                                           |
| ----------------------------------- | ------------------------------------------------------------------------------------- |
| [`refine-it`](refine-it/SKILL.md)   | Refine written artifacts for clarity and readiness while preserving intent and scope. |
| [`shorten-it`](shorten-it/SKILL.md) | Shorten text while preserving meaning, tone, and important details.                   |

Four skills are user-invoked (`disable-model-invocation: true`): they load only when you type `/<name>`, and cost no always-loaded context. Fourteen are model-invoked so agents reach them on their own when the ask arrives in natural language: `coding-discipline` (auto-loads before code work), `constitution` (loads when an instruction file asks for it), `code-review`, `adversarial-review`, `review-triage`, `commit-message`, `simplify-code`, `document-code`, `explain-code`, `create-agent-skill`, `spawn-agent`, `refine-it`, `shorten-it`, and `handoff`.

## AGENTS.md

Besides skills, this repo includes [`AGENTS.md`](AGENTS.md), the Collaboration Constitution. Its task-agnostic rules tell the agent how to lead the collaboration: surface assumptions, define done, hold scope, and push back on real issues. It is the agent-side counterpart to [Working with Agents](docs/working-with-agents.md). The file is active in this repo, with `CLAUDE.md` importing it via `@AGENTS.md`, so agents working here already follow it.

### Using it yourself

The constitution is meant to be always loaded. Install it as the [`constitution`](constitution/SKILL.md) skill, a copy of `AGENTS.md`. For coding projects, also install [`coding-discipline`](coding-discipline/SKILL.md):

```bash
npx skills add alannkl/skills --skill constitution -y
npx skills add alannkl/skills --skill coding-discipline -y
```

Run these commands from your project directory. Add `-g` to install globally for use across projects.

## Repository layout

```text
<skill-name>/
  SKILL.md
  references/  # optional supporting docs
  scripts/     # optional deterministic helpers
  assets/      # optional templates, images, or static data
```

## License

MIT. See [LICENSE](LICENSE).
