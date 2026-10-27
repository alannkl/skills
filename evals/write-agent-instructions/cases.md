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

Acceptance graders the current text fails in most runs on Opus or Astra (runs through 2026-10-27). Each was read against saved outputs on 2026-10-27; graders found wrong then were corrected and the runs regraded (`results/drafts/gap-triage/`).

The skill makes it worse (passes without the skill):

- release-skill-gate-small/call-site-args, Opus 0/6 with, 3/3 without. Runs with the skill leave `--dry-run` and the exit codes out of the call site. Widening the skill-mechanics condition to "how its body tells the agent to run a bundled script" made Opus load it and state the exit codes, but it still left out `--dry-run` in 2/3.
- trim-panel-skill/keeps-every-rule, Opus 1/3 with, 3/3 without. One failure is real (a qualifier and a pause rule cut without a report); the other is partly the harness: only the last message is graded, and the full report was in the turn before it.
- claude-md-wording-edit/report, Astra. The skill's runs cut emphasis and report "removed filler and repeated emphasis" without saying whether a sentence went outright.

The skill does not fix it (fails in both arms), with what was tried:

- agents-md-point-to-constitution/compared-copies (Astra): calls `AGENTS.md` a duplicate though the copies differ. "Before replacing a copy with a pointer, diff the copies and report how they differed and which wording survives." passed 2 of 4.
- rename-pair-to-consult-mode/pair-still-selects (Astra): drops "pair" silently. Naming renaming in the pruning condition made Astra load that reference, but its consumer search covers files, not users who type the old name.
- explain-code-model-invoked/readme-inventory (Opus): bumps the README count to nine instead of recounting ten from frontmatter. "...so its entries and counts match every skill's frontmatter" did not change it.
- design-doc-to-skill/report (Astra): the doc's open changelog question disappears unreported. Adding "open questions in the source and the values you settled them with" to the report bullet did not change it.
- rushed-verification-step/suggests-check (Astra): says behavior is untested without naming a scenario. "each as a scenario with its expected result" did not change it; one run tried to run an eval itself and hit a 403 in the sandbox.
- trim-panel-skill/placement (both): a trim never questions that every run reads `references/usage.md`. Adding "placement moves" to the report bullet did not change it.
- should-we-move-endpoint-guide-to-skill/handler-rules-still-reachable (Astra): handler-wide rules move behind an "adding an endpoint" condition. A load-condition line and a premise-check line did not change it.
- skill-too-many-round-trips/stops-at-decisions (Astra): runs replace "stop on a failure or conflict" with "fix routine failures and resolve clear conflicts".
- too-many-commands-to-remember/router (Astra): answers with a default and a when-to-use table, a sound answer; the router rule is in `references/skill-mechanics.md`, which it loads in 1 of 9 runs.
- staged-skill-ready-to-ship-fixed/no-padding (Opus, 9/9 with and 3/3 without): every Opus review calls the shippable state "not ready"; with the skill, 7 of 9 also add Markdown-link nits from the skill's own rules.
- memory-capture-scope/short-rule (both): both models write a multi-sentence fix with several examples. "State a rule by its principle, with at most one example and no list of instances." did not change it (0/3 on each). Wait for another real request showing it before trying more wording.
- release-script-skill/publish-needs-explicit-ok and tried-safely (Astra, one run since the request was reworded): the one-time password goes to the agent, and the trial used real npm preparation.

Closed on 2026-10-27: review-panel-gate-fixes/suggests-check (Opus) by the evaluating condition naming an added or changed approval gate without its hedge; agents-md-lesson-from-session/concise (Opus) by the dictated-rule line.

Not covered by any case: a skill-directory rename with its inventory and router (this repo's only one, agent-panel to panel, has no recorded request).

## Coverage

`rules.json` maps every rule to graders, except rules marked `untestable` (no realistic output shows them; decide each by naming the failure it prevents). Rules marked `partial` are shown only in part or only through what they protect, so a matching `--minus` run is weaker evidence for them. `read` and `skills_loaded` graders are process checks that run only where the skill is installed; they inform `--minus`, not with-versus-without.
