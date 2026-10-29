# Cases

This suite is being rebuilt from `references/suites.md` step 2. Its earlier 65 cases left many graders dictated by the request or workspace, so they could not show the skill's effect; they were removed on 2026-10-29 and remain in git history before that commit. `rules.json` keeps every rule's text with no graders yet, and `rules write-agent-instructions` reports each as untested until new cases map them.

## Real request families

The requests that led to this skill (or `writing-for-agents`) being used in the owner's Claude Code and Codex sessions from 2026-08-25 to 2026-10-25, about 60 in all. Use them for step 3, after written cases cover every rule.

| Family | Requests |
| --- | --- |
| 1. Change a behavior in an existing skill or prompt, with the lesson from the session | ~20 |
| 2. "shd we X?" about an existing artifact, or a proposal with "if agree, implement" | ~17 |
| 3. Find an issue across several skills | ~5 |
| 4. Add a lesson to AGENTS.md | ~4 |
| 5. Remove rules another loaded file covers | ~2 |
| 6. Trim or prune | ~2 |
| 7. Create a skill | ~4 |
| 8. Review or readiness check | ~2 |

Near-miss requests for trigger checks came from blog-post and commands-doc work.

## Gaps from the removed cases

Acceptance graders the current text fails in most runs on Opus or Astra (runs through 2026-10-27). Each was read against saved outputs on 2026-10-27; graders found wrong then were corrected and the runs regraded (`results/drafts/gap-triage/`).

The skill makes it worse (passes without the skill):

- release-skill-gate-small/call-site-args, Opus 0/6 with, 3/3 without. Runs with the skill leave `--dry-run` and the exit codes out of the call site. Widening the skill-mechanics condition to "how its body tells the agent to run a bundled script" made Opus load it and state the exit codes, but it still left out `--dry-run` in 2/3.
- trim-panel-skill/keeps-every-rule and /report, Opus: with the skill 2/3 and 1/3, without 3/3 and 3/3. With the skill Opus cuts about 22% against about 3%; one run drops the conditions on skipping a failed participant and the allowance-pause rule without reporting them, and another reports its cuts only by category.
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
