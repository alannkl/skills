# Suites

A suite is `evals/<suite>/` in the repository that holds the artifact, outside the artifact's own folder so installs don't ship it.

## eval.json

```json
{
  "artifact": {"type": "skill", "path": "<skill folder>"},
  "dependencies": ["<skill folder>"]
}
```

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
- `graders.json`: `expect_skill_loaded` with `with` and `without` booleans (skills only), optional `agent_timeout_sec`, and `graders`.

Grader types; `path` is relative to the workspace:

| type | passes when | fields |
| --- | --- | --- |
| `regex` | `pattern` is found in the file at `path`, or in the final message when `path` is absent; a missing file passes only when `optional` is true | `pattern`, `path`, `flags` (letters such as `im`), `match` (`contains` or `not_contains`), `optional` |
| `file_exists` | the file's presence matches `exists` | `path`, `exists` (default true) |
| `unchanged_except` | no file changed or appeared outside `allow` | `allow` |
| `no_writes` | the transcript shows no write through an edit tool | |
| `llm` | the judge finds `criteria` met, given the file at `path` before and after, or the final message | `criteria`, `path`, `with_final_message` (also show the final message beside the file) |
| `json` | the file at `path`, or the final message, parses as JSON whole and has every `required` top-level key | `required`, `path` |

A grader with `"variants": ["with"]` runs only in that arm. A read-only case needs both `unchanged_except` and `no_writes`: an agent can write through the shell, which only the end state shows.

Make each case discriminate:

- The baseline should often fail it while the artifact passes, and it should offer a tempting wrong answer.
- Remove hints that give the answer away, and add realistic noise such as unrelated real defects.
- Pair a case where the right result is a change with one where it is restraint.
- Grade the end result, not its wording. Require exact text only where something depends on it, such as identifiers, commands, paths, and formats a tool parses; check everything else by meaning, so any wording with the same effect passes.
- Write an `llm` criterion as the facts the output must state or keep, so a terse correct answer passes.

## Rule map

`rules.json` maps each rule to the graders that would fail without it:

```json
{"rules": {"<rule-name>": {"file": "SKILL.md", "text": "<exact text>", "graders": ["<case>/<grader>"]}}}
```

- `file` is relative to the skill folder, or is the instruction file's own name.
- `text` is whole sentences copied exactly, occurring once in the file, or a list of such passages for a rule stated in several places. Removing it builds the minus copy, so a fragment would leave broken text.
- A grader belongs to a rule only when removing that rule alone would plausibly make it fail. Graders that check general task completion stay unmapped.
- `rules <suite>` checks the map and tabulates every run of the current text.

## Results

`evals/<suite>/results/<run-id>/` holds `report.md`, `grades.jsonl` with each run's evidence, the cases as run, and Harbor's job folders; keep it out of version control.

- Judge calls go in batches: every output graded against the same criterion and original, across runs and setups, goes to the judge in one call, shuffled and unlabelled by arm. An output the same judge already decided under the same criterion and original keeps that verdict, from `results/judge-cache.jsonl`; the report counts these. The cache knows judges by the name requested, so delete it when the proxy starts serving another model under that name.
- `grade <run-dir>` regrades from the saved files without running any agent: `--judge` adds or swaps judges, and `--graders-from-repo` applies edited graders.
- Arms not under test reuse earlier runs when their task, including the sandbox or image it runs on, setup, Harbor version and agent arguments all match; `--fresh-baseline` reruns them, for example after a provider updates a model behind the same name.
- Each harness's built-in skills are off, so they cannot compete with the skill under test or share its name. A setup with `"builtin_skills": true` keeps them.
