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
| near-miss (`trigger_only`) | | blog-post-near-miss, commands-doc-near-miss |

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
| blog-post-near-miss, commands-doc-near-miss | n/a | They test the description, not the body, so only `--trigger` runs them. |
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

## Constructed blind, for finding gaps

Written by an agent that never saw this skill, its cases, graders or rules, from the request families above and what a careful reviewer would accept; reviewed by two models before running. They test what users want, not the skill's rules, so `rules.json` does not map them. A gap they find is weaker evidence than one from a real episode. Graders marked `diagnostic` record a reasonable preference the request does not state.

| Case | Family | Right outcome |
| --- | --- | --- |
| claude-md-db-reset-lesson | 4 | a short guardrail against destructive database commands |
| agents-md-integration-db-lesson | 4 | a one-line prerequisite for integration tests |
| support-bot-refund-window | 1 | fix a prompt in TypeScript and its tool description |
| ticket-classifier-prompt-trim | 6 | trim a classifier prompt, labels and routing unchanged |
| expo-release-command | 7 | a `/release` command from a runbook, no release run |
| rotate-db-creds-skill | 7 | a Codex skill from a runbook, no rotation run |
| should-we-split-claude-md | 2 | a grounded recommendation; any split keeps shared rules reachable |
| should-we-move-endpoint-guide-to-skill | 2 | a grounded recommendation; a move keeps handler rules reachable |
| pr-skill-drop-file-list | 1 | remove a section in two places |
| launch-experiment-skill-review | 8 | advice only: the skill's real defects |
| commands-sweep-master-to-main | 3 | fix three commands, leave the fourth |
| package-claude-md-dedupe | 5 | remove duplicates, keep the one that adds a qualifier |
| ui-string-skill-ready-review | 8 | "ship it", no edits |
| agreed-plan-claude-md-import | 2 | implement exactly the agreed plan; the earlier turns are supplied history |
| near-miss-* (six) | near-miss | ordinary work on human-facing text or code; the skill should not load |

## Written for rule coverage

Small worlds for rules that only integration cases tested (see each NOTES.md for the rules).

| Case | Behavior | Right outcome |
| --- | --- | --- |
| skill-long-main-file | tighten a long skill | branch-only sections move behind pointers with load conditions; every-run rules stay inline; no rule lost |
| review-council-compaction | fix lost review state and an obeyed reviewer reply | state kept in a named file and restored; replies treated as evidence; merging only on the user's request |
| prune-branches-script | script the mechanical steps of a skill | non-interactive script with dry run, quiet output, `--help`; tried safely; approval stays in the chat |

## Split from a large replay

| Case | From | Change |
| --- | --- | --- |
| release-skill-gate-small | release-script-skill | the script already fixed; updating the skill is the job; the request's first sentence names the changed interface. NOTES.md maps each original grader to its new one. |

## Reserve cases

Marked `reserve` because the regular set already tests every rule they test (`rules write-agent-instructions --min-set`); they run with `--all-cases` or by name. Cases that show a gap are here too: run one by name when a draft targets its gap. `label-then-command` absorbed `title-then-link-pointer`'s pointer and tight-line checks, and `prune-release-notes` absorbed the uncommitted-work check of `rename-pair-to-consult-mode`.

add-one-rule, agents-md-billing-split, agents-md-integration-db-lesson, agents-md-point-to-constitution, agreed-plan-claude-md-import, app-code-system-prompt, claude-md-db-reset-lesson, commands-sweep-master-to-main, create-skill-from-doc, delegate-tier-list-question, design-doc-to-skill, expo-release-command, grill-to-plan-proposal, identifier-parenthetical-adds-info, launch-experiment-skill-review, package-claude-md-dedupe, pr-skill-drop-file-list, release-skill-gate-small, rename-pair-to-consult-mode, review-only, rotate-db-creds-skill, should-we-move-endpoint-guide-to-skill, should-we-split-claude-md, staged-skill-ready-to-ship, staged-skill-ready-to-ship-fixed, support-bot-refund-window, ticket-classifier-prompt-trim, title-then-link-pointer, ui-string-skill-ready-review.

## Integration cases

These run only with `--all-cases` or by name. Smaller worlds for trim-panel-skill, review-skills-scope-sweep, release-script-skill and the staged-skill reviews kept every failure but took as long, so their time is the work the request asks for. Medians without the skill, Opus / Astra:

| Case | Without the skill | Why it stays large |
| --- | --- | --- |
| panel-persist-for-chat | 378 s / 431 s | Two merged turns over the whole panel skill and its scripts. |
| release-script-skill | 227 s / 111 s | Writing and trying a release script is the task. |
| trim-panel-skill | 118 s / 162 s | The request covers every instruction file of the panel skill. |
| review-skills-scope-sweep | 135 s / 172 s | A sweep across several skills is the behavior under test. |

The two staged-skill readiness reviews take 86-126 s without the skill in few tool calls, almost all of it writing the review; they stay in the quick set.

## Gaps

- memory-capture-scope/short-rule: with or without the skill, both models write a multi-sentence fix with several examples or a list (the user's correction in the source session). Adding "State a rule by its principle, with at most one example and no list of instances." did not change it (0/3 on each model). Wait for another real request showing it before trying more wording.
- A skill-directory rename with its inventory and router (this repo's only one, agent-panel to panel, has no recorded request).

## Coverage

`rules.json` maps every rule to graders, except rules marked `untestable` (no realistic output shows them; decide each by naming the failure it prevents). Rules marked `partial` are shown only in part or only through what they protect, so a matching `--minus` run is weaker evidence for them. `read` and `skills_loaded` graders are process checks that run only where the skill is installed; they inform `--minus`, not with-versus-without.
