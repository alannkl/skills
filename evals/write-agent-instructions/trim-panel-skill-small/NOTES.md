# trim-panel-skill-small

Provenance: reduced from `trim-panel-skill` (merged replay of a Claude Code session, 2026-10-23, files at `68e5a0d`). The request is the original wording, unchanged. This is no longer an exact replay.

## What was cut

The panel skill's instruction files went from 485 lines (8,437 words) to 357 lines (5,602 words). Only whole sections and paragraphs were removed; every kept sentence keeps its original wording, so the trimmable redundancy (rules restated across `SKILL.md` and the references) is still there. The one edit inside a kept paragraph removes the `usage.md` sentence that cited the dropped Host view section.

- `SKILL.md` 120 -> 106 lines: dropped the model-name labelling paragraph, the `--idle-seconds` note, the `progress.py` relay paragraph, the Host view section, the pair-mode paragraph on what each consultant receives, and the pair-mode failure and retry paragraph. Kept Keep the panel in the chat, Prepare (step 2 still reads `references/usage.md` on every run), Run, Pair mode and Deliver.
- `references/usage.md` 254 -> 173 lines: dropped Checks and tool permissions, the working-copy JSON and worktree detail, the tool-set paragraph, the discussion-allowance, idle and retry paragraphs, the `progress.py` paragraph, the envelope-schema and `flat-peers` nomination paragraphs, Older runs, the consultant lock and replacement paragraphs, and Extending the runner. Kept Default roster, Default drafter, Roster file, Execution boundaries, Run and inspect, Continuing the conversation, Consultant, Human input and recovery and Additional harnesses, so the panel-only and pair-only material the `placement` grader looks for is still behind no condition.
- `references/skill-collaboration.md` 46 -> 34 lines: dropped When the skill needs user input.
- `references/brief-examples.md` 65 -> 45 lines: dropped Compare alternatives, Investigate evidence, Implement behavior, Diagnose a failure and Produce finished writing.
- `README.md` 196 -> 22 lines: header and the Agent workflow table.
- `scripts/progress.py`: removed with the docs that described it; nothing imports it.
- Kept as they were: the other scripts (about 2,000 lines, so they still match every flag the docs name), presets, `agents/openai.yaml`, `AGENTS.md`, `CLAUDE.md`, `constitution/SKILL.md`, `scaffold.sh`.

## Graders

| Original grader | New grader |
| --- | --- |
| cited-sections-resolve | cited-sections-resolve (unchanged; the references still cite Keep the panel in the chat, Prepare, Pair mode, Consultant and Continuing the conversation) |
| keeps-every-rule | keeps-every-rule (unchanged) |
| no-fragmenting | no-fragmenting (unchanged) |
| placement | placement (unchanged; Prepare step 2 still reads `usage.md` on every run) |
| polish-skills-loaded | polish-skills-loaded (unchanged process check) |
| reads-pruning | reads-pruning (unchanged process check) |
| report | report (unchanged) |
| trims-every-instruction-file | trims-every-instruction-file (unchanged) |

Removed `integration: true` and `agent_timeout_sec: 2400`.

## Estimated agent work

Read four instruction files (about 5,600 words); the scripts only if the agent checks flags. Rewrite all four files and report removals. About 1.5 to 2 minutes; the work scales with the prose, which is about two thirds of the original.
