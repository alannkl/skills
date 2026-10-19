---
type: llm
focus: {source: file, path: skills/deploy-review/SKILL.md}
---

Judge `skills/deploy-review/SKILL.md`. Its description says what the skill does and that it applies when someone asks to review a deploy or release pull request. The file keeps all six checks with their meaning (backward-compatible migrations; new environment variables have a default or are set in all three environments; new feature flags default to off; rollback steps in the pull request description; dashboards and alerts for new endpoints; approval from the on-call engineer for the deploy window), either in the file or in a file under `skills/deploy-review/` that it points to with a clear condition. It does not drop the Kubernetes limits without a way to reach them when a manifest changes.
