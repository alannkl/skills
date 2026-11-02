---
name: feature
description: "Take a goal from grill to an open, reviewed PR, unattended after the first plan review, then walk through the provisional decisions and verify the deploy after merge."
disable-model-invocation: true
argument-hint: "[goal]"
---

# Feature

Take the goal in the argument, else from the conversation so far, through plan, build and review to an open PR, then wait for the user. Start at the grill: whether to build is already settled. The unattended run ends at step 7's stop or an earlier one; the user's return resumes at the stage the Run state records.

## Record

- The **anchor** is the user's own decisions from the grill. A **provisional decision** is one made without the user's explicit pick, held for the walkthrough.
- Record each provisional decision in `session.md` as it arises: grill open questions, panel rounds, gate deviations, triage deferrals and rejections.
- Keep a compact Run state block in `session.md`, updated at each stage boundary: current stage, approved plan revision, panel directory and status, PR URL, last reviewed commit, and unresolved verification results. After context compaction, reload this skill and resume from it.
- A **stop** updates the Run state and waits for the user, naming what it needs from them.

## Authority

Invoking `/feature` authorizes pushing the branch, opening the PR, choosing the review tier by risk, fixing accepted review findings and PR check failures the change caused, closing a panel this run opened, and reopening the plan consultation for a material design change, bounded by step 4's stops and closed again once resolved. Merge stays with the user.

## Workflow

1. **Grill.** Run `grill-to-plan` in documented mode. `plan.md` lists the anchor apart from provisional decisions. When merge deploys, the acceptance criteria include at least one check runnable against the deployed environment, with its target, deploy-completion signal and command: the **deployed check**.

2. **Confirm the anchor.** Ask one question listing the anchor items, without re-walking the grill's decisions. Only an explicit confirmation counts; a reply that edits or asks about the anchor is not one, so settle it and ask again.

3. **Round 1, with the user.** After confirmation, open a panel through `panel` in consult mode unless one is open, and have it review `plan.md` with the anchor as settled context. Put all of round 1 to the user in one batch, recommended options first: challenges to the anchor and every other change. Whatever they leave undecided becomes provisional. Then ask, in one batch, for whatever the unattended run needs beyond the Authority section. The run is unattended from here.

4. **Iterate to approval.** Revise the plan and reconsult until it is **approved**: a round whose replies raise no new material objection and leave none unresolved, recorded as your conclusion, never as consultant approval, whatever the panel's mode. An unavailable consultant is not assent. Stop, listing the open objections, when a material objection persists with no new evidence or viable next revision; when resolving one needs an anchor change; after 3 unattended rounds; or when a consultation fails after its one retry. Whatever the panel, its deliverable is the plan; code review goes only through step 6. Once approved, close a panel this run opened, keeping its directory. Build nothing before approval.

5. **Build, then gate.** Build with subagents, even where `delegate` would judge inline cheaper; `delegate` governs work orders, builder models and parallelism. Then gate the result yourself before any review:
   - Run the build and tests, and check the diff against the plan's decisions, units, non-goals and acceptance criteria, without hunting bugs. Run the deployed check against a local or preview environment when one exists.
   - Builders close the gaps and the gate reruns; stop when gaps remain after two such rounds.
   - A deliberate deviation that is an implementation choice becomes provisional; one that changes the anchor stops; one that materially changes the reviewed design reopens the closed plan consultation through `panel`'s reopen before proceeding.
   - Leave simplify and document passes to the repo's precommit.

6. **Review.** Each PR gets one initial review route; step 7's verification and step 8's re-review are its only later checks.
   - Commit the build first.
   - Where the repo has its own PR workflow, configured by the user's per-repo PR rules such as `~/.claude/<repo>.md`, open the PR through it; it runs the review, triage and fixes.
   - Otherwise run `review-panel review-only` on `<target>...HEAD` with branch, tier and effort by risk: `standard high` by default; `frontier` for cross-service, schema or contract changes or a large diff; add `adversarial` for secrets, permissions, migrations, stored state, concurrency or money paths. Triage the findings yourself with `review-triage` and fix the accepted ones.
   - An escalation stops.

7. **Verify, then stop.** Verify any review fixes with `review-panel`'s step 7, with this session as its parent and the Authority section as auto-fix approval. Accepted findings still unresolved at its cap make the run blocked, not ready: stop. Without a repo PR workflow, open the PR with `gh` once verification resolves. Fix PR check failures the change caused and verify them the same way; stop on any other failure. Stop when the PR is open, its checks pass and verification is resolved.

8. **Walkthrough.** When the user returns, walk through every provisional decision and open question, code-changing ones first. When answers change a decision, record it in `plan.md`; when they change code, the change passes step 5's gate, then the commits since the last review are re-reviewed on the open PR before merge: by the scope-growth rule in the user's per-repo PR rules, never a close-and-reopen rule in the repo's PR workflow; without per-repo rules, by `review-panel review-only` on that range, triage and step 7's verification. Merge only on the user's word.

9. **After merge.** Where merge deploys, wait for the deploy, confirm the deployed version contains the merged commit, then run the deployed check. On failure, build a repair that reproduces the failed check, against the approved plan; a plan change follows step 5's deviation rule. The repair goes through step 5, then enters step 6 as its own PR, whose merge the user decides. Report missing access or an unfinished deploy as unverified.
