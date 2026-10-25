# Cases

Each case's request family, where its request and files come from, and whether it is realistic. Families come from the requests that actually led to this skill (or `writing-for-agents`) being used in the owner's Claude Code and Codex sessions from 2026-08-25 to 2026-10-25, about 60 requests:

| Family | Requests | Cases |
| --- | --- | --- |
| 1. Change a behavior in an existing skill or prompt, with the lesson from the session | ~20 | review-panel-gate-fixes, panel-persist-for-chat, explain-code-model-invoked, rename-pair-to-consult-mode, release-script-skill, precommit-error-lesson, skill-too-many-round-trips, rushed-verification-step, deploy-rollback-pointer, app-code-system-prompt, templated-prompt-rule |
| 2. "shd we X?" about an existing artifact, or a proposal with "if agree, implement" | ~17 | delegate-tier-list-question, grill-to-plan-proposal, multi-vendor-skill-plan, noop-dispute, too-many-commands-to-remember |
| 3. Find an issue across several skills | ~5 | review-skills-scope-sweep |
| 4. Add a lesson to AGENTS.md | ~4 | agents-md-lesson-from-session, add-one-rule |
| 5. Remove rules another loaded file covers | ~2 | agents-md-point-to-constitution, trim-duplicates-keep-qualifiers |
| 6. Trim or prune | ~2 | trim-panel-skill, prune-release-notes, prune-unexplained-safeguard, identifier-parenthetical-adds-info, label-then-command, title-then-link-pointer, claude-md-wording-edit |
| 7. Create a skill | ~4 | incident-investigation-skill, design-doc-to-skill, create-skill-from-doc, create-standup-command |
| 8. Review or readiness check | ~2 | staged-skill-ready-to-ship, staged-skill-ready-to-ship-fixed, review-only, evaluate-only |
| none | | agents-md-billing-split, toolless-prompt-pointer (general-user restructures) |
| trigger only | | blog-post-near-miss, commands-doc-near-miss |

Report results by family; family 6 has the most cases and the fewest requests.

## Replays of real episodes

Files are the repository at the commit before the change. The request is the owner's message, typos kept: verbatim (exact), several consecutive turns joined into one (merged), or a question and its answer shortened into one instruction (condensed). What the owner accepted is evidence of one good answer, not the only one; graders accept others.

| Case | Kind | Request | Files | What the owner accepted |
| --- | --- | --- | --- | --- |
| review-panel-gate-fixes | exact | Codex session 2026-08-27 | `4b05824` | `29e2a53` |
| review-skills-scope-sweep | exact | Codex session 2026-08-27 | `4b05824` with `code-review` from `4b05824^` and `review-panel/SKILL.md` as that session read it, before its uncommitted scope fix | an audit naming review-panel and code-review, then "correct them"; graders accept the audit or the fixes |
| grill-to-plan-proposal | exact | Claude Code session 2026-09-23 | `275d6d5^` | `275d6d5` |
| delegate-tier-list-question | exact | Codex session 2026-10-06 | `6f2b907` | a recommendation, then "we shd add the model tier list" in a later turn |
| agents-md-point-to-constitution | exact | Claude Code session 2026-10-09 | `d659b33^` | `d659b33` |
| explain-code-model-invoked | exact | Codex session 2026-08-28 | `27225f3^` | explain-code changed and the others suggested; `27225f3` after "ok update" |
| trim-panel-skill | merged | Claude Code session 2026-10-23: "trim panel skill" and the owner's next turn, "not only main skill.md, all skill instruction files" | `68e5a0d` | `39c2a1f` |
| panel-persist-for-chat | merged | two consecutive Codex turns 2026-09-10, "you say" changed to "i say" | `39b344e` | `0db8425` |
| rename-pair-to-consult-mode | condensed | Claude Code session 2026-10-23: "shd we rename pair mode to consult mode?", then "rename" | `39c2a1f` plus that session's uncommitted load split | `7cec1bd` |
| staged-skill-ready-to-ship | exact | Codex session 2026-09-30 | `ce98b41^` committed, its change staged, `delegate` files as the session read them before fixes | two findings, then "fixed" |
| staged-skill-ready-to-ship-fixed | exact request, later state | the same request | `ce98b41` staged | "I'd ship this version" |

Each replay keeps the repository's `AGENTS.md` (the collaboration constitution at that commit), as in the real session; a rule that changes nothing beside it is a no-op in the owner's environment, not necessarily everywhere.

## Constructed cases

| Case | Realistic? | Note |
| --- | --- | --- |
| add-one-rule | yes | Real requests carry the lesson from the conversation, not a ready-made rule. |
| claude-md-wording-edit | yes | Real polish requests arrive as `$refine-it on changed files`, which loads this skill indirectly. |
| trim-duplicates-keep-qualifiers | yes | Matches "remove duplicated rules [...] already covered by constitution and coding discipline". |
| prune-release-notes | yes | The request's "You may edit files in the workspace" sets the authorization `step-3-consumer` grades. |
| prune-unexplained-safeguard | yes | |
| identifier-parenthetical-adds-info, label-then-command, title-then-link-pointer | yes | "Tighten X" matches "trim panel skill"; the parenthetical and link habits are ones agents write. |
| design-doc-to-skill, create-skill-from-doc, create-standup-command | yes | |
| review-only | yes | |
| evaluate-only | partly | Real reviews ask "is it ready to ship?", not for trigger evaluation. |
| app-code-system-prompt, templated-prompt-rule | yes | |
| agents-md-billing-split | partly | The request spells out which requirements other code needs, which a typical user would not say. |
| toolless-prompt-pointer | yes | |
| blog-post-near-miss, commands-doc-near-miss | n/a | They test the description, not the body; read them with the trigger set, from the with arm. |
| incident-investigation-skill | yes | From a request in a private repo ("check how we investigate alerts [...] create a generic project skill"); general backend with past incident notes; the request names the skill `investigate`. |
| release-script-skill | yes | An existing release skill whose script prompts and floods output. |
| precommit-error-lesson | yes | From "update precommit skill to avoid this error" with the CI error pasted. |
| agents-md-lesson-from-session | yes | The lesson arrives conversationally. |
| multi-vendor-skill-plan | yes | From a planning request in a private repo; discussion only. |
| noop-dispute | yes | A disputed sentence in this repo's `code-review`. |
| skill-too-many-round-trips | yes | From "shd we try best to minimize the back and forth", as a directive. |
| rushed-verification-step | yes | A fuzzy verify step the agent skips. |
| too-many-commands-to-remember | yes | This repo's review skills. |
| deploy-rollback-pointer | yes | A pointer with no load condition that never fires. |

## Gaps

- A skill-directory rename with its inventory and router (this repo's only one, agent-panel to panel, has no recorded request).

## Coverage

`rules.json` maps every rule to graders, except rules marked `untestable` (no realistic output shows them; decide each by naming the failure it prevents). Rules marked `partial` are shown only in part or only through what they protect, so a matching `--minus` run is weaker evidence for them. `read` and `skills_loaded` graders are process checks that run only where the skill is installed; they inform `--minus`, not with-versus-without.
