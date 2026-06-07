---
name: refine-it
description: Refine an existing artifact into a stronger, ready-to-use version while preserving its intent, scope, and direction. Use when the user asks to refine, tighten, polish, finalize, improve, clean up, sharpen, or revise a written artifact. Default to producing the improved version, not just critique.
---

# Refine It

A refinement pass for an existing artifact, whether it is a rough draft, a near-final version, or the current state of a document. Improve clarity, structure, emphasis, and readiness while preserving the artifact's intent, audience, and operational behavior. Refine the artifact; do not redesign the underlying plan or refine code logic.

## Workflow

1. Identify the artifact and its job.
   - Infer the artifact type, audience, purpose, desired tone, and level of intervention from the prompt and surrounding context.
   - Preserve explicit constraints, factual claims, decisions, and operational semantics. Restructure, merge, reorder, or condense sections when doing so makes the artifact clearer or more useful.
   - Treat routing, eligibility, permissions, configuration, and scope metadata as operational semantics: preserve behavior, but improve wording, grouping, and scanability.
   - If intent is genuinely ambiguous, ask only the smallest necessary question; otherwise choose the level of refinement that best improves the artifact for its apparent job.

2. Evaluate before rewriting.
   - Look for unclear purpose, weak structure, repetition, vague wording, hidden assumptions, missing context, tone mismatch, overclaiming, and unfinished parts.
   - Separate refinement problems from strategy problems. Improve the current direction decisively without changing the artifact's goal, audience, or operational behavior unless the user asks.

3. Refine and polish directly.
   - Produce a stronger version, not just critique, unless the user asks for review notes only.
   - Prefer meaningful improvement over minimal change when the benefit is clear, but keep edits proportional to the artifact's needs. Remove repetition, sharpen hierarchy, normalize terminology, and make implicit decisions explicit when these changes preserve intent.
   - Preserve semantic intent over brevity. Do not remove domain terms, repeated labels, qualifiers, constraints, or intentionally specific phrasing merely to shorten the artifact.
   - Before trimming, identify protected terms and scope-bearing phrases. Keep them unless they are clearly redundant or the user explicitly asks for a shorter version.
   - Tighten language by removing filler, merging duplication, choosing concrete verbs and nouns, and making implicit decisions explicit.
   - Improve structure only as much as clarity, flow, scanability, and readiness require.
   - Polish scope-bearing language without broadening or narrowing it. Preserve triggers, audiences, promises, permissions, requirements, labels, statuses, API names, configuration keys, and eligibility criteria unless the user asks to change scope.
   - If a refinement removes, renames, or compresses key terminology, mention that change in `Notes`.
   - Preserve the user's voice; do not flatten casual, direct, or opinionated writing into generic corporate prose.

4. Finalize the handoff.
   - Put the final version first when the user is likely to use it directly.
   - For short artifacts, return only the refined version unless a note would prevent confusion. For longer artifacts, use `Final Version` followed by optional `Notes`.
   - Keep notes concise and include them only when useful: major changes, assumptions, unresolved ambiguity, or claims that need verification.
   - If editing a repo file, update the file and summarize changed files. This is a text-edit pass only; do not run linters, link checks, builds, or other tooling.

## Example

Before: "In order to be able to leverage this functionality, users will need to first go ahead and configure their settings."
After: "To use this, configure your settings first."
(Removes filler, picks concrete verbs, keeps the meaning and direct tone.)

## Gotchas

- Do not treat "improve" as permission to change the artifact's goal, audience, or scope.
- Do not preserve awkward wording just because it was in the original when the user asked for polish.
- Do not add facts, examples, promises, or requirements unless they follow clearly from the existing artifact.
- Do not over-expand simple artifacts; keep them complete enough for their purpose and no larger than needed.
- Do not turn refinement into research, implementation, or product strategy unless the user explicitly broadens the task.
- Do not change the behavior of operational text such as frontmatter descriptions, issue labels, policy clauses, CLI flags, configuration keys, routing text, or search/matching language just to make the wording sound stronger.
