---
name: refine-it
description: Refine an existing written artifact for clarity, structure, tone, and readiness while preserving intent and scope.
disable-model-invocation: true
---

# Refine It

## Workflow

1. Identify the artifact and its job.
   - Infer the artifact type, audience, purpose, desired tone, and level of intervention from the prompt and surrounding context.
   - A request naming a specific edit — fix, replace, add, remove, correct — scopes the pass to that edit; refine open-endedly only when asked to.
   - Preserve explicit constraints, factual claims, decisions, and operational text. Restructure, merge, reorder, or condense sections when doing so makes the artifact clearer or more useful.
   - Treat operational text — triggers, permissions, labels, statuses, API names, configuration keys, routing and eligibility language — as behavior: polish its wording and grouping, never its meaning.
   - If intent is genuinely ambiguous, ask only the smallest necessary question; otherwise choose the level of refinement that best improves the artifact for its apparent job.

2. Evaluate before rewriting.
   - Look for unclear purpose, weak structure, repetition, vague wording, hidden assumptions, missing context, tone mismatch, overclaiming, and unfinished parts — every section assessed against this list before any rewriting.
   - Separate refinement problems from strategy problems. Improve the current direction decisively without changing the artifact's goal, audience, or operational behavior unless the user asks.
   - If the artifact is already strong for its job, make only light polish or state that no substantive edits are needed; do not invent changes merely to produce a visibly different version.

3. Refine and polish directly.
   - Produce a stronger version, not just critique, unless the user asks for review notes only.
   - Cut filler and duplication, choose concrete verbs and nouns, sharpen hierarchy, make implicit decisions explicit.
   - Before trimming, identify protected terms — domain terms, qualifiers, constraints, intentionally specific phrasing — and keep them unless clearly redundant.
   - Add only content that follows clearly from the existing artifact.
   - In artifacts that instruct an executor — skills, runbooks, policies, agent prompts — cut clauses that change no behavior and add no judgment: pure emphasis, and rationale that only restates the rule it follows. Keep rationale that informs a call the reader has to make unaided.
   - If a refinement removes, renames, or compresses key terminology, mention that change in `Notes`.
   - Preserve the user's voice; keep casual, direct, or opinionated writing in its own register rather than flattening it into generic corporate prose.

4. Finalize the handoff.
   - Put the final version first when the user is likely to use it directly.
   - For short artifacts, return only the refined version unless a note would prevent confusion. For longer artifacts, use `Final Version` followed by optional `Notes`.
   - Keep notes concise and include them only when useful: major changes, assumptions, unresolved ambiguity, or claims that need verification.
   - If editing a repo file, update the file and summarize changed files. This is a text-edit pass only; do not run linters, link checks, builds, or other tooling.

## Example

Before: "In order to be able to leverage this functionality, users will need to first go ahead and configure their settings."
After: "To use this, configure your settings first."
(Removes filler, picks concrete verbs, keeps the meaning and direct tone.)
