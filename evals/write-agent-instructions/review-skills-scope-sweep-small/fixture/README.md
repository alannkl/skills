# Skills

Agent skills for repeatable workflows, project conventions, and domain-specific habits.

Each skill lives in its own directory and follows the [agentskills.io specification](https://agentskills.io/specification). A skill starts with `SKILL.md`, which contains YAML frontmatter and Markdown instructions, and may include supporting `references/`, `scripts/`, or `assets/`.

## Available skills

### Reviewing

| Skill                                               | Description                                                                                                                                                  |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`code-review`](code-review/SKILL.md)               | Produce findings-led code review reports for concrete code changes.                                                                                          |
| [`adversarial-review`](adversarial-review/SKILL.md) | Hunt material failures in a diff, branch, or files. Return structured findings with failure scenarios, but never apply fixes.                                |
| [`review-triage`](review-triage/SKILL.md)           | Triage review findings as the code's owner. Validate each, weigh fix cost against deployed complexity, and return dispositions instead of fixing everything. |
| [`review-panel`](review-panel/SKILL.md)             | Run a parallel panel of reviewer models, then merge findings, triage, fix, and verify. Spawns several agent sessions (cost scales with preset); strongest with multiple harnesses installed. User-invoked. |

`review-panel` is user-invoked (`disable-model-invocation: true`): it loads only when you type `/review-panel`. The other three are model-invoked, so agents reach them on their own when the ask arrives in natural language.

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
