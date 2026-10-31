---
name: review-panel
description: Reviews a diff, branch, pull request, or named files with a panel of parallel reviewer models, then merges and triages their findings and optionally applies approved fixes. Use only when the user asks for a panel, multi-model, or multi-agent review, since it spawns several agent sessions; for an ordinary review use code-review.
---

# Review panel

Run the pipeline: scope → brief → panel → merge → triage → findings report → approval gate → fix → verify → final report.

Set the **approval mode** when the run starts. The default is **gated**. `/review-panel auto-fix` sets **auto-fix**, which grants standing approval for findings triaged with a **fix** disposition. Auto-fix never selects an **escalate** fork; escalations always require a later user decision. `/review-panel review-only` sets **review-only**, which ends the run at step 4.

Arguments combine in any order: approval mode, branch, tier, and effort (`/review-panel review-only adversarial frontier xhigh`).

## 1. Scope

Resolve one review scope for the whole panel with `code-review`'s bundled resolver, run by absolute path from inside the repository, with `<code-review-dir>` for that skill's installed directory: `python3 <code-review-dir>/scripts/resolve-scope.py [--scope <spec>]`. Use a user-named scope exactly, without adjacent changes: pass a commit, a range, `staged`, or `worktree` (unstaged and untracked) as `--scope`; a branch as `<base>...<branch>`, since a bare branch name is its tip commit only; and a pull request as `<base>...<head>` after fetching both refs. A supplied diff file or named files are the scope as given. Without `--scope`, the resolver takes the first non-empty of staged changes; unstaged and untracked changes; commits ahead of the upstream; or the current branch against its merge base with the default branch. Exit 1 means nothing to review: stop and say so. Exit 2 means a bad ref, multiple merge bases, an unreadable file, or an unwritable output directory: fix the cause or resolve the scope by hand. Give every voice the printed `scope` and `diff` path, and put the printed `excluded` files in the brief so no voice flags code that is mid-edit.

## 2. Brief

Collect the acceptance criteria from the conversation, ticket, or commit messages. Write the **review brief** to the scratchpad. Include the intent, requirements satisfied, deliberate trade-offs, known limitations, and declared non-goals, stating trade-offs and non-goals as claims with their basis. Keep it to one page. Scope exclusions belong in the brief; verdicts do not: never tell a voice what not to flag or cap a severity — triage decides. The brief is done when a stranger could reject an out-of-scope finding by citing it.

## 3. Panel

The parent, meaning this session's harness and model, always runs `code-review` inline on the resolved scope (the **parent voice**), even under a composition the user spells out. Add the **fresh voices** of the user's **branch** and **tier**, each defaulting independently to `normal standard`. A spelled-out composition replaces both. Fresh eyes come from the context, not the model. A fresh context using the parent's model is still a fresh reviewer.

| Branch             | Each fresh voice runs                                   |
| ------------------ | ------------------------------------------------------- |
| `normal` (default) | `code-review`                                           |
| `adversarial`      | `code-review` and `adversarial-review`, in two contexts |

| Tier                 | Fresh voices                |
| -------------------- | --------------------------- |
| `quick`              | the first strong rival      |
| `standard` (default) | the first two strong rivals |
| `frontier`           | every frontier member       |

Roster, in rank order within each tier:

| Member           | Harness | Tier     | Sibling          |
| ---------------- | ------- | -------- | ---------------- |
| Claude Fable 5.1 | claude  | frontier | Claude Opus 5.5  |
| GPT-6 Astra      | codex   | frontier | GPT-6.1 Sol      |
| GPT-6.1 Sol      | codex   | strong   | GPT-6.1 Terra    |
| Claude Opus 5.5  | claude  | strong   | Claude Fable 5.1 |
| Grok 4.7         | cursor  | strong   | GLM 5.3          |

- **Strong rivals** are the strong members on harnesses other than the parent's, in rank order. With no other harness installed, fill the tier with the parent's sibling, then the **twin**: the parent's own model in a fresh context.
- A frontier member that is the parent's own model runs as its twin.
- An unavailable member's sibling stands in, on the same harness.

With an Opus 5.5 parent in a full environment, `quick` reviews with Sol, `standard` with Sol and Grok, and `frontier` with Fable and Astra; `adversarial` runs each in both roles. Step 7 verification goes to the first strong rival or its stand-in, whatever the tier.

Rules:

- `adversarial-review` runs only in fresh contexts, never in the parent context. A member named twice runs as two separate fresh contexts.
- **Effort.** Every fresh voice runs at one effort per run: high, or the level the user names. The parent voice keeps the session's own effort.
- **Missing member.** When a tier or user-named member is unavailable with no stand-in, stop and recommend a composition built from the available members. Proceed only after the user chooses. Sibling and twin stand-ins need no confirmation.
- Route a voice whose model runs on the parent's own harness through the harness's builtin subagent tool if it has one; route every other voice through `spawn-agent`. Either way, pass the reviewing skill's `SKILL.md` path in the prompt as its charter. Tell the voice to perform the review itself, without spawning agents or invoking `review-panel`.
- The user may name members beyond the roster: any harness or model the environment can run. For a harness `spawn-agent` has no reference for, run a headless CLI session by that harness's own conventions (its `--help` is the source of truth); if it cannot be run, treat it as a missing member.
- Before launching, report the resolved scope, the intent from the brief, and the panel composition to the user. Report and continue; do not wait for approval.
- Send every voice the same scope and brief verbatim. Launch the fresh voices in parallel and run the parent pass while they work. Collect every report unedited; do not soften or pre-judge findings. On a re-run over the same scope, pass the previous run's final report to every voice as prior findings.

## 4. Merge

Merge the reports into one findings list. Collapse findings with the same root cause and remedy into one, listing every affected location; keep independently actionable defects separate. Keep the highest severity, the most concrete failure scenario, and a **concurrence** tag (`flagged by 2/3 voices`). Origin carries no weight. The parent voice's findings count like any other, while concurrence signals credibility and feeds triage's confidence. Merging is done when no two findings share a root cause and remedy.

In review-only mode, present the merged findings with the panel composition and any substitutions; the pipeline ends there.

## 5. Triage

Invoke `review-triage` on the merged findings inline in this session. Keeping triage here preserves the conversation, review brief, and any author context recovered during the review.

Present the complete triage report, including every disposition, proposed fix, and escalation fork.

In gated mode, follow the report with a **decision round** over every **fix** and **escalate** finding — the findings that need a user decision. Deferred and rejected dispositions stand as reported; the user can override one through the same round. Collect the decisions through the harness's multiple-choice question tool, one question per finding, batched up to the tool's limit; with no such tool, ask in prose. Each question carries the finding's case in its own text, so the user decides without scrolling back to the report:

- the problem, in one or two lines
- the proposed fix
- the fix's estimated cost: files and functions touched, rough lines changed, and any risk the fix itself introduces

A **fix** finding offers **approve fix** (marked recommended), **defer**, and **reject**; an **escalate** finding offers its A/B/C fork with triage's recommendation marked. A rejection needs the user's reason — take it from the free-text option or ask — and it travels with the finding into the final report.

In auto-fix mode, proceed with every **fix** disposition after presenting the report; if the report contains an **escalate** disposition, stop before any fix work and put its fork to the user through the same decision-round format. A `/review-panel` invocation without `auto-fix` authorizes review, triage, and the decision round; only the round's answers authorize fixes.

**Record durable decisions in the artifact native to each kind.** A rejection whose reason is local and non-obvious gets a comment at the finding's site stating the code's rationale — the confusion that produced the finding is itself a defect, and the comment is its fix. For a deferral, follow triage's planned comment or ticket; evidence-pending deferrals stay in the report only. A decided escalation gets an ADR when the repo keeps an ADR log. Scope rejections live in the final report only. Write each comment as the code's own voice ("validated at the parse boundary"), not as review history. Report the proposed recording edits and continue. Apply them only when the user's authorization covers those specific edits; approval of an unrelated fix does not authorize them. Otherwise leave them proposed in the report. They need no step 7 ruling.

If no finding has a **fix** or **escalate** disposition, the triage report and any recording edits the user approved complete the pipeline.

## 6. Fix

In gated mode, the decision round's answers define the approved set. In auto-fix mode, all **fix** dispositions are already approved. Apply the approved fixes as one batch, honoring triage's scope: nothing beyond the approved findings and escalation options. Unapproved findings remain pending.

Parallel fixers need isolation chosen by file overlap. Partition the batch into disjoint file-ownership lists before launching; only a clean partition may share the working tree, and each fixer edits only the files it owns. Overlapping files, or a fixer that needs destructive git operations (a mutation check that reverts a file), get sequential waves or per-fixer worktrees instead. On a shared tree, treat mid-flight full-suite results as noise — neighbors' half-edited files fail tests that are not failures; the gate that counts is one full-suite run on the assembled tree after every fixer lands.

## 7. Verify the fixes

Verification is a closed check, not a re-review. Send it to one fresh first-rival context, not the whole panel, and never to the parent: by this step the parent authored the fix batch, and an author's own `resolved` ruling is the one check that always passes.

Assemble the evidence in the parent so the verifier reads instead of re-derives:

- the approved findings, each mapped to the diff hunks that claim to fix it
- the fix diff
- the full-suite result on the assembled tree, which the parent runs before handing off

For each finding, require `resolved` or `unresolved` with concrete evidence, plus any blocking issues introduced by the fixes. Send unresolved and fix-introduced blocking findings through `review-triage`, present its report, and return to step 5's approval gate: gated mode runs another decision round, while auto-fix mode may take one further **fix** batch automatically. **Two post-fix verification passes is the cap.** Report findings still open at the cap instead of fixing them.

## 8. Report

Report:

- final verdict and fixes applied
- panel composition, with any substitutions
- findings left unapproved
- deferred and rejected findings, each with its evidence
- escalations and how they were decided
- anything left open at the cycle cap

The pipeline is complete when every approved finding is verified resolved or explicitly reported open. Recommend a fresh `/review-panel` run on the new state only when the fix batch resolved several high-or-critical findings or reworked a large share of the scope. The user re-invoking is the outer loop.
