# Suites

A suite is `evals/<suite>/` in the repository that holds the artifact, outside the artifact's own folder so installs don't ship it.

## eval.json

```json
{
  "artifact": {"type": "skill", "path": "<skill folder>"},
  "dependencies": ["<skill folder>"],
  "setups": {"run": ["<config>"], "full": ["<config>", "<config>"]}
}
```

- `setups` names the setups the artifact must support: `run` for edit rounds, `full` for `--full` and `--minus`. Each entry is a preset name from `scripts/configs.json` or a spec such as `{"harness": "openclaw", "model": "deepseek-v4.1-flash", "effort": "high", "provider": "morph"}`. Either key left out falls back to that file's `defaults`, which `--help` prints.
- `artifact.type` is `skill`, `instruction-file` or `prompt`.
- An instruction file also takes `"as"`, the name it gets in the workspace, such as `AGENTS.md` or `CLAUDE.md`; it defaults to the file's own name. A fixture must not already hold that file.
- A prompt also takes `"role"` and `"runner"`:
  - `"role": "system"` (default) adds the text to the system prompt: Claude Code's appended system prompt, Codex's developer instructions, or the API call's system message. OpenClaw has no such setting; evaluate the text as an AGENTS.md there.
  - `"role": "user"` puts the text before the case's request, as a task prompt arrives.
  - `"runner": "harness"` (default) runs agent setups; `"runner": "api"` runs the `api-*` setups, which call the model once with no tools, as an app does.
  - `{{name}}` placeholders take the case's `vars.json` values.
- Without an `artifact` entry, the suite tests the skill in the repository folder with the suite's name.
- `dependencies` lists skills the artifact loads. Both arms install them, so the arms differ only by the artifact.

## Cases

Each case is a folder in the suite:

- `instruction.md`: the user's request, exactly as the agent receives it.
- The workspace: `fixture/`, copied into it, or `scaffold.sh`, run in the empty workspace with `fixture/` beside it. An API case needs none.
- `vars.json`: values for a prompt's placeholders.
- `graders.json`: `expect_skill_loaded` with `with` and `without` booleans (skills only), optional `agent_timeout_sec`, `trigger_only` (true for a near-miss that only `--trigger` runs), `integration` (true for a case that needs a larger world, which runs only with `--all-cases` or by name), and `graders`.

Grader types; `path` is relative to the workspace:

| type | passes when | fields |
| --- | --- | --- |
| `regex` | `pattern` is found in the file at `path`, or in the final message when `path` is absent; a missing file passes only when `optional` is true | `pattern`, `path`, `flags` (letters such as `im`), `match` (`contains` or `not_contains`), `optional` |
| `file_exists` | the file's presence matches `exists` | `path`, `exists` (default true) |
| `unchanged_except` | no file changed or appeared outside `allow`, whose entries may be globs such as `.agents/skills/*` | `allow` |
| `no_writes` | the transcript shows no write through an edit tool | |
| `skills_loaded` | the transcript shows every skill in `skills` loaded from the installed copies | `skills` |
| `read` | a file read or shell command delivered text containing `marker`, such as the file's first line | `marker`, `match` |
| `ran` | a shell command matching `pattern` ran and succeeded; with `not_contains`, none was tried | `pattern`, `match` |
| `llm` | the judge finds `criteria` met, given the file at `path` (or every file in `paths`, which may hold globs such as `skill/**/*.md`) before and after, or the final message | `criteria`, `path` or `paths`, `with_final_message` (also show the final message beside the files) |
| `json` | the file at `path`, or the final message, parses as JSON whole and has every `required` top-level key | `required`, `path` |

A grader with `"diagnostic": true` is reported but left out of `compare`'s acceptance grades: give it to a reasonable preference the request does not state. `compare` also leaves out `read` and `skills_loaded`, since a draft may reach the same outcome another way. A grader with `"variants": ["with"]` runs only in that arm and in `--minus` copies. Give process checks, such as `read` and `skills_loaded`, that limit: they show what the agent did, not the quality of its output, and the other arm lacks the skill they look for. A read-only case needs both `unchanged_except` and `no_writes`: an agent can write through the shell, which only the end state shows.

Make each case realistic:

- Take the request and its files from work users bring: what a typical user would ask, about files like theirs. Never shape a case so the baseline fails; text that changes nothing on realistic cases is a no-op.
- Keep the cues and noise real work has, such as unrelated real defects.
- Pair a case where the right result is a change with one where it is restraint.
- Grade the end result, not its wording. Require exact text only where something depends on it, such as identifiers, commands, paths, and formats a tool parses; check everything else by meaning, so any wording with the same effect passes.
- Write an `llm` criterion as the facts the output must state or keep, so a terse correct answer passes.
- Give each case one primary behavior, plus a grader for every requirement the user would still expect kept; those catch one rule breaking another.

Keep each case small, so edit rounds stay fast:

- Include the files the task's decisions depend on: the target, its consumers, sibling files that show local conventions, the code that loads a prompt. Leave out the rest, and add no unrelated files by quota.
- Aim for a median, without the artifact, under a minute for a routine edit and under two for creating or reviewing a skill.
- Shrink a case over budget: cut the files and lengths its graders do not depend on, and split a request that bundles several jobs into cases a user would send separately. Time without the artifact shows only that a world is large, not that the behavior needs it. Mark a case `integration` only when its behavior cannot occur in a smaller world, and say why in the suite's notes.
- A reduced case is a new case: run it beside the original on every supported setup before replacing it.
- Before raising `--concurrency`, run one short case at rising levels and stay below the level where time per run or retries climb.

## Rule map

`rules.json` maps each rule to the graders that would fail without it:

```json
{"rules": {"<rule-name>": {"file": "SKILL.md", "text": "<exact text>", "graders": ["<case>/<grader>"]}}}
```

- `file` is relative to the skill folder, or is the instruction file's own name.
- `text` is whole sentences copied exactly, occurring once in the file, or a list of such passages for a rule stated in several places. Removing it builds the minus copy, so a fragment would leave broken text.
- A grader belongs to a rule only when removing that rule alone would plausibly make it fail. Graders that check general task completion stay unmapped.
- A rule no realistic case can show in its output, such as one governing an order of steps the transcript does not record, takes `"untestable": "<why>"` and no graders. Decide it by naming the failure it prevents, not by a run. A rule whose graders show only part of it, or show it only through what it protects, takes `"partial": "<what is not shown>"`, so a removal that matches is read as weaker evidence.
- `rules <suite>` checks the map and tabulates every run of the current text.

## Results

`evals/<suite>/results/<run-id>/` holds `report.md`, `grades.jsonl` with each run's evidence, the cases as run, and Harbor's job folders; keep it out of version control.

- Judge calls go in batches: every output graded against the same criterion and original, across runs and setups, goes to the judge in one call, shuffled and unlabelled by arm. An output the same judge already decided under the same criterion and original keeps that verdict, from `results/judge-cache.jsonl`; the report counts these. The cache knows judges by the name requested, so delete it when the proxy starts serving another model under that name.
- `grade <run-dir>` regrades from the saved files without running any agent: `--judge` adds or swaps judges, and `--graders-from-repo` applies edited graders.
- Every arm reuses earlier runs when its task, including the sandbox or image it runs on, setup, Harbor version and agent arguments all match, so a run spends sessions only on what changed; `--fresh` reruns them, for example after a provider updates a model behind the same name.
- Each harness's built-in skills are off, so they cannot compete with the skill under test or share its name. A setup with `"builtin_skills": true` keeps them.
