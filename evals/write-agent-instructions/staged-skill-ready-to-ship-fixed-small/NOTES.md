# staged-skill-ready-to-ship-fixed-small

Provenance: reduced from `staged-skill-ready-to-ship-fixed` (exact request, later state: `ce98b41` staged, the version the owner would ship). The request is the original, unchanged, and the staged change's changed lines are preserved. This is no longer an exact replay.

## What was cut

Only the committed base shrank. Every staged file (`delegate/SKILL.md`, `delegate/references/dispatch.md`, `constitution/SKILL.md`, `AGENTS.md`, `README.md`) keeps its changed lines; only the README's context lines differ, because sections around them were cut.

- `panel/` (about 2,300 lines of skill and runner) and `handoff/`: removed. Neither refers to delegation, and the README rows that name them stay, like the rows for the other skills this repository lists but the fixture never held.
- `spawn-agent/`: kept, since `dispatch.md` tells the agent to load it and request lean mode. `SKILL.md` is unchanged; each of its four harness references lost only its Templates section (example commands). Every Lean start line is kept.
- `README.md` 180 -> 88 lines (181 -> 89 staged): kept the skill tables and the model-invoked count and list the staged change edits, the AGENTS.md section through Using it yourself's install commands, and the layout and license; dropped Installation, Recommended skills, the project-section template and Docs. The same lines were cut from the base and staged copies, so the README's changed lines (the `delegate` row and the count and list) are preserved.
- Kept as they were: `AGENTS.md`, `CLAUDE.md`, `constitution/SKILL.md`, `scaffold.sh`, `instruction.md`.

## Graders

| Original grader | New grader |
| --- | --- |
| consumers-consistent | consumers-consistent (unchanged) |
| no-edit | no-edit (unchanged) |
| no-padding | no-padding (unchanged) |
| no-writes | no-writes (unchanged) |
| ship-verdict | ship-verdict (unchanged; its paths are all kept) |

## Estimated agent work

Run `git diff --cached` (five files, about 140 added lines), read `delegate/` and probably `spawn-agent/SKILL.md` and one harness reference; no edits. About 1 to 1.5 minutes, nearly all of it writing the review.
