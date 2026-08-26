---
name: review-panel
description: "Panel review of any chosen scope: a review brief, parallel reviewer model voices (presets standard/max/ultra), merged findings, triage, and optionally fixes and verification. Fixes are user-gated by default; an upfront auto-fix option approves them. Spawns several fresh agent sessions, so cost scales with the preset; strongest with multiple harnesses installed (claude, codex, cursor), falls back to one."
disable-model-invocation: true
---

# Review panel

Run the pipeline: scope → brief → panel → merge → triage → findings report → approval gate → fix → verify → final report.

Set the **approval mode** when the run starts. The default is **gated**. `/review-panel auto-fix` sets **auto-fix**, which grants standing approval for findings triaged with a **fix** disposition. Auto-fix never selects an **escalate** fork; escalations always require a later user decision.

## 1. Scope

Resolve one review scope for the whole panel. A user-named scope may be a pull request, commit or range, branch against a base, diff, staged or unstaged work, or named files. Use it exactly and do not add adjacent changes. If the user supplies no scope, use the first non-empty scope below:

1. staged changes
2. unstaged and untracked changes
3. commits ahead of the upstream (`@{upstream}..HEAD`)
4. the current branch against its merge base with the default branch

When staged changes win while unstaged edits exist, name the excluded files in the brief so no voice flags code that is mid-edit.

## 2. Brief

Collect the acceptance criteria from the conversation, ticket, or commit messages. Write the **review brief** to the scratchpad. Include the intent, requirements satisfied, deliberate trade-offs, known limitations, and declared non-goals. Keep it to one page. The brief is done when a stranger could reject an out-of-scope finding by citing it.

## 3. Panel

Assemble the reviewer **voices** from the preset the user named (`/review-panel max`), the exact composition they specified, or the default `standard`. A composition the user spells out overrides every preset. Fresh eyes come from the context, not the model. A fresh context using the parent's model is still a fresh reviewer.

Roster, ranked by capability:

| Rank | Member        |
| ---- | ------------- |
| 1    | fable 5       |
| 2    | codex 5.6 sol |
| 3    | opus 5        |
| 4    | grok 4.6      |

Ranks 3–4 are reserves. They enter only as fallback rivals or as `ultra`'s second rival.

Resolve two roles relative to the **parent**, meaning this session's harness and model:

- **rivals**: the highest-ranked members on harnesses other than the parent's, in rank order. `standard` and `max` use the first rival; `ultra` uses the first two. With no other harness installed, use the next model on the parent's harness (a claude-only environment resolves to opus). With a single-model harness, use a fresh subagent of the parent's model.
- **twin**: the parent's own model in a fresh context.

The parent always runs `code-review` inline on the resolved scope (the **parent voice**), plus the preset's fresh voices:

| Preset               | Fresh voices                                                |
| -------------------- | ----------------------------------------------------------- |
| `standard` (default) | adversarial: rival                                          |
| `max`                | code-review: rival · adversarial: rival, twin               |
| `ultra`              | code-review: both rivals · adversarial: both rivals, twin   |

Step 7 verification always goes to the first rival. With a fable parent in a full environment, the rivals are sol, then grok. `standard` reviews with adversarial sol; `max` adds code-review sol and adversarial fable; `ultra` adds grok in both roles.

Rules:

- Every panel includes at least one `adversarial-review` voice in a fresh context; `adversarial-review` never runs in the parent context. A member named twice runs as two separate fresh contexts.
- **Effort.** Fresh voices default to xhigh reasoning effort; fable defaults to high. The parent voice keeps the session's own effort. The user can override any voice's effort.
- **Missing member.** When a preset or user-named member is unavailable, stop and recommend a composition built from the available members. Proceed only after the user chooses. The prescribed rival fallback chain needs no confirmation.
- Route a voice whose model runs on the parent's own harness through the harness's builtin subagent tool if it has one; route every other voice through `spawn-agent`. Either way, pass the reviewing skill's `SKILL.md` path in the prompt as its charter.
- The user may name members beyond the roster: any harness or model the environment can run. For a harness `spawn-agent` has no reference for, run a headless CLI session by that harness's own conventions (its `--help` is the source of truth); if it cannot be run, treat it as a missing member.
- Before launching, report the resolved scope, the intent from the brief, and the panel composition to the user. Report and continue; do not wait for approval.
- Send every voice the same scope and brief verbatim. Launch the fresh voices in parallel and run the parent pass while they work. Collect every report unedited; do not soften or pre-judge findings.

## 4. Merge

Merge the reports into one findings list. Collapse findings that name the same defect at the same location. Keep the highest severity, the most concrete failure scenario, and a **concurrence** tag (`flagged by 2/3 voices`). Origin carries no weight. The parent voice's findings count like any other, while concurrence signals credibility and feeds triage's confidence. Merging is done when no two findings claim the same defect.

## 5. Triage

Invoke `review-triage` on the merged findings inline in this session. Keeping triage here preserves the conversation, review brief, and any author context recovered during the review.

Present the complete triage report, including every disposition, proposed fix, and escalation fork. In gated mode, stop and ask the user which fixes and escalation options to approve. In auto-fix mode, proceed with every **fix** disposition after presenting the report; if the report contains an **escalate** disposition, stop before any fix work and ask the user to choose its fork. A `/review-panel` invocation without `auto-fix` authorizes review and triage only.

If no finding has a **fix** or **escalate** disposition, the triage report is the final report and the pipeline is complete.

## 6. Fix

In gated mode, resume only after the user explicitly approves named findings or the whole triaged batch. In auto-fix mode, all **fix** dispositions are already approved. Apply the approved fixes as one batch, honoring triage's scope: nothing beyond the approved findings and escalation options. Unapproved findings remain pending.

## 7. Verify the fixes

Verification is a closed check, not a re-review. Send the approved findings and fix diff to one fresh first-rival context, not the whole panel. For each finding, require `resolved` or `unresolved` with concrete evidence, plus any blocking issues introduced by the fixes. Send unresolved and fix-introduced blocking findings through `review-triage`, present its report, and return to step 5's approval gate: gated mode pauses again, while auto-fix mode may take one further **fix** batch automatically. **Two post-fix verification passes is the cap.** Report findings still open at the cap instead of fixing them.

## 8. Report

Report:

- final verdict and fixes applied
- panel composition, with any substitutions
- findings left unapproved
- deferred and rejected findings, each with its evidence
- escalations and how they were decided
- anything left open at the cycle cap

The pipeline is complete when every approved finding is verified resolved or explicitly reported open. Recommend a fresh `/review-panel` run on the new state only when the fix batch resolved several high-or-critical findings or reworked a large share of the scope. The user re-invoking is the outer loop.
