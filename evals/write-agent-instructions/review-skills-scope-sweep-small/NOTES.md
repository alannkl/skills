# review-skills-scope-sweep-small

Provenance: reduced from `review-skills-scope-sweep` (exact replay of a Codex session, 2026-08-27, files at `4b05824` with `code-review` from `4b05824^` and `review-panel/SKILL.md` as that session read it). The request is the original wording, unchanged. This is no longer an exact replay.

## What was cut

- `code-review/SKILL.md` 151 -> 124 lines: dropped three of eight risk categories in step 3, three of five overlay pointers in step 4, two test bullets in step 5, step 6 (review size; later steps renumbered and their cross-references updated), the finding-writing paragraph and the good-finding example. Step 1, which asks the agent to state what is reviewed but gives no default scope, is unchanged.
- `code-review/references/`: kept `contract-surfaces.md` and `trust-boundaries.md`, the two overlays step 4 still points to; dropped the other three.
- `review-panel/SKILL.md` 94 -> 93 lines: dropped the worked fable-parent example after the preset table (its first sentence, that verification goes to the first rival, stays) and the rule on members beyond the roster. The description "Review current changes", the author voice running `code-review` "on its own changes" and the "authoring context" rule are unchanged.
- `README.md` 157 -> 32 lines: header, the Reviewing table, a one-line invocation note rewritten for the four skills present, and the layout and license sections.
- Kept as they were: `adversarial-review/SKILL.md` (has a default scope; no issue), `review-triage/SKILL.md` (takes findings, not a scope; the restraint target), `AGENTS.md`.

## Graders

| Original grader | New grader |
| --- | --- |
| finds-code-review | finds-code-review (unchanged) |
| finds-review-panel | finds-review-panel (unchanged; every quoted phrase is still in the file) |
| keeps-code-review | keeps-code-review (overlay list narrowed to the two kept references) |
| keeps-rest | keeps-rest (verification now named as going to the first rival, matching the kept sentence) |
| no-false-positives | no-false-positives (unchanged) |
| others-unchanged | others-unchanged (allow list narrowed to the two kept references) |

Removed `integration: true`.

## Estimated agent work

Read four `SKILL.md` files, two short references and `README.md` (about 490 lines). Edit `review-panel/SKILL.md` and `code-review/SKILL.md`, or report both. About 1.5 minutes.
