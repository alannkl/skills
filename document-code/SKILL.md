---
name: document-code
description: Improve source-code understanding with useful comments, language-appropriate API docs, or focused docs without changing behavior. Use when the user asks to document code, add comments, add docstrings or doc comments, explain confusing code inline, improve code documentation, or run a documentation pass over selected code or the current git diff. Do not use for explanation-only requests, simplification, refactoring, or broad architecture documentation.
---

# Document Code

Improve code understanding without changing behavior, structure, or public contracts. Add documentation only where it improves understanding: enough to explain relevant intent, invariants, and non-obvious tradeoffs without restating clear code.

## Scope

- Use selected or tagged code when the user provides it.
- Use specified files, directories, symbols, or descriptions when the user names a target.
- When the user asks for a general documentation pass with no target, inspect staged source-code changes first; if nothing is staged, inspect unstaged source-code changes.
- Restrict edits to source-code files in the languages present in the target or diff. Infer source files from extensions, project layout, imports, and build configuration; no extension list is exhaustive.
- Exclude docs, JSON, YAML, lockfiles, generated files, images, and other non-code files unless the user explicitly asks to edit them.
- If no source-code files remain after filtering, report that there is nothing to document and make no changes.

## Hard Constraints

- Do not edit executable behavior.
- Do not rename symbols, reorder logic, simplify code, extract helpers, restructure files, or change formatting.
- Do not change APIs, types, serialized data, user-visible text, errors, snapshots, analytics events, accessibility semantics, timing, ordering, or persistence.
- Only add or improve these forms of documentation:
  - inline comments
  - language-appropriate API docs, such as docstrings, doc comments, JSDoc, rustdoc, Go doc comments, XML docs, or equivalent project conventions
  - focused documentation files only when the rationale is needed across two or more files or modules and inlining it would repeat the same explanation in more than one place
- If the code is unclear because it needs simplification, renaming, or refactoring, do not fix it during this workflow; report that limitation instead.

## Workflow

1. Identify the target.
   - Prefer explicit user selection or tagged files over broader diffs.
   - For diff-based targets, use staged source-code changes when they exist; fall back to unstaged source-code changes only when nothing is staged.
   - Avoid unrelated files, even if nearby code could also benefit from documentation.

2. Read enough surrounding context.
   - Inspect callers, exported APIs, tests, types, nearby comments, existing docs, and local conventions when they explain intent.
   - Understand the behavior before documenting it: inputs, outputs, side effects, error paths, lifecycle ordering, retries, idempotency, concurrency, persistence, and business rules.
   - Prefer established project terms over inventing new vocabulary.

3. Document only what helps understanding.
   - Document non-obvious invariants, assumptions, preconditions, and ownership rules.
   - Explain tradeoffs, rejected alternatives, compatibility constraints, and migration constraints.
   - Clarify race-condition guards, ordering requirements, cleanup requirements, retry behavior, backoff, or idempotency expectations.
   - Explain fallback behavior, failure-mode handling, and boundary conditions that are easy to misread.
   - Capture business or domain rules that are not obvious from syntax alone.
   - Describe private helper intent when a reader would reasonably ask why the helper exists.
   - Use language-appropriate API docs for public APIs, exported APIs, and complex private helpers when parameter meaning, return semantics, side effects, errors, invariants, domain rules, or lifecycle responsibilities are not obvious from the signature.
   - Let simple private functions stand on clear names and signatures; mandatory docstrings for obvious code create noise and stale docs.

4. Leave clear code alone.
   - Do not restate names, types, assignments, loops, conditionals, or syntax.
   - Do not narrate what each line does.
   - Do not compensate for bad naming with comments when a later simplification or rename would be the real fix.
   - Do not add broad architecture essays inline.
   - Do not add comments to satisfy volume; fewer precise comments are better than many obvious ones. As a rule of thumb, add a comment only where a competent reader would otherwise pause to ask "why"; if you cannot name that question, leave the code uncommented.

5. Write documentation in the right place.
   - Default to a local comment. Use one whenever the rationale fits beside a single branch, helper, or call site.
   - Choose a doc file only when all of these hold: the rationale is needed to understand code in two or more files or modules, it cannot sit next to any single one without losing context, and inlining it would repeat the same explanation in more than one place. When undecided, keep it local.
   - Keep one source of truth: put the full rationale in the doc file, then leave a short local comment that points to it only where a nearby reader needs the pointer and immediate rationale.
   - In focused doc files, use a diagram (sequence, state, flow) when cross-module structure, lifecycle, or ordering is easier to grasp visually than in prose. Follow the repo's existing diagram conventions if any; otherwise default to mermaid in markdown files. Never diagram what a sentence covers, and keep diagrams pinned to behavior that is stable, not implementation details that will drift.
   - Place new docs beside existing relevant docs when possible, and keep them narrowly scoped.

6. Match local style.
   - Follow the repository's comment style, language-specific documentation conventions, capitalization, punctuation, and terminology.
   - Keep comments close to the code they explain.
   - Prefer concise comments over block comments unless a public API or multi-step invariant needs structure.
   - Preserve useful existing comments; update stale or misleading comments only when they are within scope.
   - When documenting changed code, review existing comments and docstrings in the touched area and update any that no longer match the implementation, behavior, constraints, or public contract.

7. Validate the result.
   - Re-read the diff and confirm only comments, docstrings, or explicitly needed docs changed.
   - Confirm executable code, formatting-only structure, generated files, and unrelated files were not touched.
   - Check that every added comment explains intent, rationale, constraints, or non-obvious behavior.
   - Run the narrowest relevant validation if available, such as lint or docs checks, when comments or docstrings can affect tooling.
   - If checks are unavailable or unnecessary for a comments-only change, state that clearly.

## Output

Return a concise summary proportional to the change. For small tasks, use a short paragraph or 2-4 concrete bullets that cover what was documented and whether validation ran.

For larger documentation passes, include only the sections that add useful signal:

- `Files reviewed`: list reviewed source files.
- `Comments/docstrings added`: list changed files or nearest symbols.
- `Docs added`: list new or updated documentation files.
- `Needs refactor, but not changed`: list unclear areas where the real fix is simplification, naming, or structure.
- `Validation`: list commands run and results, or state why none were run.

Do not claim behavior changed, bugs were fixed, or code was simplified. The deliverable is better understanding with unchanged behavior.

## Gotchas

- If intent is unclear after reasonable reading, say so instead of inventing rationale.
- Prefer tests or focused docs over a comment on every edge case when examples are more useful.
- Do not add comments that will become wrong as soon as implementation details change.
