---
name: refine-it
description: Refine an existing artifact into a stronger ready-to-use version while preserving its intent, scope, and direction. Use when the user asks to refine, tighten, polish, finalize, improve, clean up, sharpen, or revise docs, plans, prompts, specs, messages, skill files, and other written artifacts. Default to producing the improved version, not just critique.
---

# Refine It

A lightweight refinement pass for an existing artifact, whether a rough draft, a near-final version, or the current state of a document. Refine the writing; do not redesign the underlying plan, and do not refine code logic.

## Workflow

1. Identify the artifact and its job.
   - Infer type, audience, purpose, desired tone, and level of intervention from the prompt and surrounding context.
   - Preserve explicit constraints, terminology, structure, factual claims, and decisions unless they are unclear, contradictory, or actively weaken the artifact.
   - If intent is genuinely ambiguous, ask only the smallest necessary question; otherwise make a conservative assumption and proceed.

2. Evaluate before rewriting.
   - Look for unclear purpose, weak structure, repetition, vague wording, hidden assumptions, missing context, tone mismatch, overclaiming, and unfinished parts.
   - Separate refinement problems from strategy problems. Improve the current direction; do not redesign it unless the user asks.

3. Refine and polish directly.
   - Produce a stronger version, not just critique, unless the user asks for review notes only.
   - Tighten language by removing filler, merging duplication, choosing concrete verbs and nouns, and making implicit decisions explicit.
   - Improve structure only as much as needed for clarity, flow, scanability, and readiness.
   - Preserve the user's voice; do not flatten casual, direct, or opinionated writing into generic corporate prose.

4. Finalize the handoff.
   - Put the final version first when the user is likely to use it directly.
   - For short artifacts, return only the refined version unless a note prevents confusion. For longer ones, use `Final Version` then optional `Notes`.
   - Keep notes concise and only when useful: major changes, assumptions, unresolved ambiguity, or claims that need verification.
   - If editing a repo file, update the file and summarize changed files. This is a text-edit pass only; do not run linters, link checks, builds, or other tooling.

## Example

Before: "In order to be able to leverage this functionality, users will need to first go ahead and configure their settings."
After: "To use this, configure your settings first."
(Removes filler, picks concrete verbs, keeps the meaning and direct tone.)

## Gotchas

- Do not treat "improve" as permission to change the artifact's goal, audience, or scope.
- Do not preserve awkward wording just because it was in the original when the user asked for polish.
- Do not add facts, examples, promises, or requirements unless they follow clearly from the existing artifact.
- Do not over-expand lightweight artifacts; tighter and more usable often beats more complete.
- Do not turn refinement into research, implementation, or product strategy unless the user explicitly broadens the task.
