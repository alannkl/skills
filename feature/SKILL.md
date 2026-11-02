---
name: feature
description: "Take a goal from grill to an open, reviewed PR, unattended after the first plan review, then walk through the provisional decisions and verify the deploy after merge."
disable-model-invocation: true
argument-hint: "[goal]"
---

# Feature

Take the goal in the argument, else the conversation, from the grill to an open, reviewed PR; whether to build is settled. The run is unattended from round 1's end to step 7's stop.

## Record

In `session.md`, record each provisional decision as it arises, triage deferrals and rejections included. Keep a Run state block there, updated at each stage boundary and stop: stage, approved plan revision, panel directory and status, PR URL, last reviewed commit, open verification results. Resume from it when the user returns, and after compaction once this skill is reloaded.

## Authority

`/feature` authorizes pushing the branch, opening the PR, fixing accepted findings and PR check failures the change caused, closing a panel this run opened, and reopening the plan consultation for a material design change. Merge stays with the user.

## Workflow

1. **Grill** with `grill-to-plan` in documented mode. `plan.md` lists the **anchor**, the user's own decisions, apart from **provisional** ones, made without their explicit pick. When merge deploys, its acceptance criteria include a **deployed check** against the deployed environment, with target, deploy-completion signal and command.
2. **Confirm the anchor** in one question listing its items, without re-walking the grill; only an explicit yes counts.
3. **Round 1.** Open a consult-mode panel through `panel` unless one is open, to review `plan.md` with the anchor settled. Put all its changes, anchor challenges included, to the user in one batch, recommended options first; anything left undecided is provisional.
4. **Iterate to approval.** Revise and reconsult until **approved**: a round with no new material objection and none unresolved, by your conclusion, never consultant approval; an unavailable consultant is not assent. Stop with the open objections when one persists without new evidence or a viable revision or needs an anchor change, after 3 unattended rounds, or when a consultation fails its retry. A panel reviews only the plan; on approval, close one this run opened, keeping its directory. Build nothing before approval.
5. **Build, then gate.** Build with subagents even where `delegate` would go inline; follow it otherwise. Gate the result yourself: run build and tests, check the diff against the plan's decisions, units, non-goals and acceptance criteria without hunting bugs, and run the deployed check on any local or preview environment. Builders close gaps and the gate reruns; stop if gaps remain after two rounds. A deliberate deviation is provisional if an implementation choice and stops if it changes the anchor; one that materially changes the reviewed design reopens the closed consultation through `panel`'s reopen and step 4 before proceeding. Leave simplify and document passes to the repo's precommit.
6. **Review.** Commit the build. Where the user's per-repo PR rules, such as `~/.claude/<repo>.md`, set a repo PR workflow, open the PR through it; it reviews, triages and fixes. Otherwise run `review-panel review-only` on `<target>...HEAD`, branch, tier and effort by risk: `standard high` by default, `frontier` for contract changes or a large diff, plus `adversarial` for security, stored state, concurrency or money. Then triage with `review-triage` and fix accepted findings. An escalation stops. Each PR gets one of these routes; steps 7 and 8 are its only later checks.
7. **Verify, then stop.** Verify fixes with `review-panel`'s step 7, this session as parent and Authority as auto-fix approval; accepted findings unresolved at its cap block the run: stop. Without a repo PR workflow, then open the PR with `gh`. Fix check failures the change caused, verifying likewise; stop on others. Stop once the PR is open, checks pass and verification is resolved.
8. **Walkthrough.** Go through every provisional decision and open question, code-changing ones first, recording changed decisions in `plan.md`. A code change passes step 5's gate; then re-review the commits since the last review on the open PR, by the per-repo rules' scope-growth rule, never the repo workflow's close-and-reopen, else by step 6's `review-panel` route on that range and step 7.
9. **After merge**, where merge deploys: wait for the deploy, confirm it contains the merged commit, and run the deployed check. On failure, build a repair that reproduces the failed check, against the approved plan under step 5's deviation rule; it passes all of step 5, then enters step 6 as its own PR.
