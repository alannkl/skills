# Skills

Agent skills for repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and Markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available skills

### Foundation

Loaded before the work starts rather than for a task. Wire both into your instruction file; see [Using it yourself](#using-it-yourself).

| Skill                                             | Description                                                                                                                                                                                                                                    |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`constitution`](constitution/SKILL.md)           | The Collaboration Constitution as an installable skill: universal rules for how the agent leads the collaboration; always loaded.                                                                                                              |
| [`coding-discipline`](coding-discipline/SKILL.md) | Apply disciplined engineering habits for simple, scoped, maintainable, well-structured agent-written code. Based on [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md). |

### Agent workflow

| Skill                                               | Description                                                                                                                                                                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`write-agent-instructions`](write-agent-instructions/SKILL.md) | Write, edit, review, evaluate, and prune instructions for agents: skills, slash commands, `AGENTS.md`, `CLAUDE.md`, and system or task prompts. Incorporates guidance from [`writing-for-agents`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md). |
| [`spawn-agent`](spawn-agent/SKILL.md)               | Spawn a headless coding-agent CLI run (`agy -p`, `claude -p`, `agent -p`, or `codex exec`) for one scoped subtask, with a shared workflow and one reference per supported harness.                                          |
| [`delegate`](delegate/SKILL.md)                     | Delegate bounded steps when cheaper than doing them inline, or faster at bounded extra cost when the user is waiting or has a deadline. Weigh the cost, choose a collector, runner, digester, or implementer, write the work order, check the returned record, and report a delegation ledger at delivery. |
| [`panel`](panel/SKILL.md)                           | Keep a multi-agent panel across harnesses, or read-only consultants, available in the current chat; consult them when independent input is worth the cost and complete requested or promised reviews. User-invoked.         |
| [`handoff`](handoff/SKILL.md)                       | Create a compact temporary handoff so another agent can continue the current conversation.                                                                                                                                  |
| [`retrospect`](retrospect/SKILL.md)                 | Mine recent sessions across projects and harnesses for repeated corrections and friction, then turn the lessons you pick into checks, rules, skill fixes, or hand-off briefs where each belongs. User-invoked.              |

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
| [`review-pr`](review-pr/SKILL.md)                   | Review an open GitHub pull request in its own worktree, with its comments collected by a bundled script, then request changes (via a bundled submitter) or apply approved fixes and follow the project's commit and push conventions. User-invoked.                                               |

### Research

| Skill                               | Description                                                                                                                                                                                                                                                                                                             |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`study`](study/SKILL.md)           | Research a question from sources into an evidence-graded report, one subject in depth or how several sources answer one question, shown in chat and saved on request. Collectors fill source records under a versioned evidence contract; the host selects sources, synthesizes, and stops on coverage, not on a count. |
| [`learn-from`](learn-from/SKILL.md) | Improve anything you maintain, from a skill or doc to a codebase or process, using how others do the same job. Runs `study` on the sources, grades each idea by evidence and fit, proposes adopt, reject, or defer with reasons, and applies the changes you pick. User-invoked.                                        |

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

Seven skills are user-invoked: they load when you type `/<name>` (`$<name>` in Codex) and stay out of the model's skill list. Each sets `disable-model-invocation: true` in its frontmatter and carries `agents/openai.yaml` with `allow_implicit_invocation: false`, because Codex ignores the frontmatter field; a harness that honors neither still lists them to the model. Sixteen are model-invoked so agents reach them on their own when the ask arrives in natural language: `coding-discipline` (auto-loads before code work), `constitution` (loads when an instruction file asks for it), `code-review`, `adversarial-review`, `review-triage`, `commit-message`, `simplify-code`, `document-code`, `explain-code`, `write-agent-instructions`, `spawn-agent`, `delegate`, `study`, `refine-it`, `shorten-it`, and `handoff`.

## Installation

This repo plus the [recommended](#recommended-skills) skill, globally:

```bash
npx skills add alannkl/skills --all -g -y && npx skills add cursor/plugins --skill unslop -g -y
```

### Skills CLI

List the skills in this repo:

```bash
npx skills add alannkl/skills --list
```

Install every skill from this repo globally:

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

## Recommended skills

An external skill that pairs well with this repo:

- Install [`unslop`](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) to cut AI tells from any writing. [`refine-it`](refine-it/SKILL.md) and [`shorten-it`](shorten-it/SKILL.md) improve structure and length; `unslop` removes generated-sounding patterns. It is user-invoked: use `/unslop` for a writing pass.

  ```bash
  npx skills add cursor/plugins --skill unslop -g -y
  ```

## Collaboration Constitution

Besides skills, this repo includes the Collaboration Constitution, shipped as the [`constitution`](constitution/SKILL.md) skill. Its task-agnostic rules tell the agent how to lead the collaboration: surface assumptions, define done, hold scope, and push back on real issues. It is the agent-side counterpart to [Working with Agents](docs/working-with-agents.md). This repo's [`AGENTS.md`](AGENTS.md) points agents to it, and `CLAUDE.md` imports `AGENTS.md` via `@AGENTS.md`, so agents working here already follow it.

### Using it yourself

The constitution is meant to be always loaded. Install it as the [`constitution`](constitution/SKILL.md) skill. For coding projects, also install [`coding-discipline`](coding-discipline/SKILL.md):

```bash
npx skills add alannkl/skills --skill constitution -y
npx skills add alannkl/skills --skill coding-discipline -y
```

Run these commands from your project directory. Add `-g` to install globally for use across projects.

Add the following at the top of your project's `AGENTS.md`. Each skill has its own line so you can omit either one if you do not use it:

```markdown
Apply the `constitution` skill from the start.
Apply the `coding-discipline` skill to code work, except trivial formatting, pure prose edits, or explicitly throwaway prototypes.

If a required skill is missing, say so and stop the affected work.
Project-specific instructions below take precedence over the skills above.

## Project-specific instructions

<!-- build/test commands, conventions, domain context, gotchas -->
```

Your `AGENTS.md` stays yours: `npx skills update -p` (or `-g` for a global install) refreshes the constitution without touching it. An update follows the source's current revision; the skills lock file records a content hash, not a version, and pinning to a specific revision is unverified. For Claude Code, which reads `CLAUDE.md` rather than `AGENTS.md`, add a `CLAUDE.md` containing the single line `@AGENTS.md`; a plain file needs no symlink support, which some Windows setups and archive workflows lack.

Copying the body of [`constitution/SKILL.md`](constitution/SKILL.md) into an always-loaded instruction file still works, but every copy then has to be updated by hand.

Add to the universal rules only when the addition pays off in every session. Anything more specific belongs in a skill, a doc, or the project section.

Referencing the skill by name works for any install scope. If your agent does not resolve skills by name, link the installed `SKILL.md` path instead (e.g. `.agents/skills/coding-discipline/SKILL.md` for a project-local install).

## Docs

Background notes and research behind these skills:

- [Philosophy](docs/philosophy.md): a standalone, slowly growing list of personal beliefs about engineering with AI.
- [Working with Agents](docs/working-with-agents.md): human-facing principles for directing an agent to complete tasks, synthesized from Anthropic, OpenAI, Microsoft Research, Ethan Mollick, Simon Willison, and academic human-AI collaboration research. Its agent-side counterpart is the [Collaboration Constitution](#collaboration-constitution) above.
- [How an agent should communicate with its human](docs/agent-communication.md): the evidence base behind the Communicating section of the [Collaboration Constitution](constitution/SKILL.md), from a survey of this repo's skills and related sources.
- [Codebase Structure Principles](docs/codebase-structure.md): durable principles for organizing code around ownership, change patterns, dependency direction, and module boundaries.
- [Behavior-First Testing for Agentic Coding](docs/behavior-first-testing-for-agentic-coding.md): a behavior-scaffold workflow that establishes intended behavior before the change's code or executable test mechanics can bias it.
- [Cheap Code, Expensive Systems](docs/cheap-code-expensive-systems.md): a cost model for adversarial review and review triage, so findings that are valid but not worth fixing stay unfixed.

## Repository layout

```text
<skill-name>/
  SKILL.md
  references/  # optional supporting docs
  scripts/     # optional deterministic helpers
  assets/      # optional templates, images, or static data
  agents/      # openai.yaml invocation policy for Codex (user-invoked skills)
```

## Evals

Eval cases live in `evals/<skill-name>/`, outside the skill folders, so installs don't ship them. `scripts/skill-eval/skill_eval.py` runs each case with and without the skill on several agent harnesses and models through [Harbor](https://github.com/harbor-framework/harbor), one fresh Docker container per run, and grades the results on the host. Every run is a real, billed agent session.

```bash
python3 scripts/skill-eval/skill_eval.py run write-agent-instructions --case add-one-rule --probe
python3 scripts/skill-eval/skill_eval.py grade evals/write-agent-instructions/results/<run-id>
python3 scripts/skill-eval/skill_eval.py rules write-agent-instructions
python3 scripts/skill-eval/skill_eval.py run write-agent-instructions --minus <rule> --config claude-haiku
```

It needs Docker, `uv`, and these credentials in the environment or the repository's `.env`: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` for an Anthropic-compatible endpoint that also serves OpenAI's Responses API at `/v1` (Claude Code, Codex and the judges use it), and `OPENROUTER_API_KEY` for OpenClaw. The first run builds a base image with the pinned agent CLIs, which takes a few minutes.

- **Configurations** are named in `scripts/skill-eval/configs.json`: harness, model, reasoning effort, and for OpenRouter the pinned upstream provider. `openclaw-haiku` runs Claude Haiku in OpenClaw through the same Anthropic-compatible endpoint as Claude Code, so comparing it with `claude-haiku` isolates the harness. The default run uses `claude-haiku` (Claude Code), `codex-luna` (Codex) and `openclaw-deepseek-high` (OpenClaw); pass `--config` to choose others.
- **A case** holds `instruction.md`, the workspace source (`fixture/`, or a `scaffold.sh` run in the empty workspace with `fixture/` beside it), and `graders.json`: whether the skill should load in each arm, and graders of type `regex`, `file_exists`, `unchanged_except`, `no_writes` or `llm`. `evals/<skill>/eval.json` lists skills the skill under test loads, which both arms install.
- **Built-in skills are off.** Each harness ships skills of its own, such as Claude Code's `code-review` and the `skill-creator` in Codex and OpenClaw, which compete with the skill under test or share its name. Set `"builtin_skills": true` on a configuration to keep them.
- **Arms** differ only by the skill under test. Whether it loaded is read from each harness's transcript, so the report shows when a with-skill run never used it, and flags any run that loaded a same-named skill from somewhere else.
- **Arms not under test are reused** from earlier runs when their task (instruction, workspace, installed skills, image), configuration, Harbor version and agent arguments are all unchanged and enough graded runs exist: the without-skill arm in a normal run, the full skill with `--minus`. The report marks reused runs and leaves their cost out. Pass `--fresh-baseline` to rerun them, for example after a provider updates a model behind the same name.
- **Rules** are mapped to the graders that test them in `evals/<skill-name>/rules.json`: each rule's file, its exact text, and its `case/grader` references. `rules <skill>` checks the map and tabulates, per rule and configuration, its graders' pass counts with the skill, without it, and with only that rule removed, over every run of the current skill text. `run <skill> --minus <rule>` builds that copy and runs it against the full skill on the rule's cases, three times each by default, telling both arms to use the skill at its installed path, so the comparison measures its text rather than whether it triggers, and a harness's built-in skill with the same name cannot stand in. The table only lists candidates and evidence; removing a rule stays a skill edit you make.
- **Results** go to `evals/<skill-name>/results/<run-id>/`, which git ignores: `report.md` with pass counts per case, configuration and arm; `grades.jsonl` with each run's evidence; a copy of the cases as run; and Harbor's job folders. Runs that failed for infrastructure reasons, and grades the judge or a cut-off transcript left undecided, are counted apart from failures.
- **Grading** uses the judge named in `configs.json` and the run's own copy of its cases. `grade` reruns it from the saved files without rerunning any agent: `--judge` adds or swaps judges, and `--graders-from-repo` applies edited graders.
- **`--probe`** adds a case asking the agent to list its skills, to check that the skill is visible in the with-skill arm, absent in the without-skill arm, and not shadowed by a same-named built-in skill.

## License

MIT. See [LICENSE](LICENSE).
