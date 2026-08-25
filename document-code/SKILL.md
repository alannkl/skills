---
name: document-code
description: Improve source-code understanding with useful comments, API docs, or focused docs without changing behavior. Use when the user asks to document code, add comments or docstrings, or run a documentation pass over code or a diff; not for explanation-only requests.
---

# Document Code

Improve code understanding without changing behavior, structure, or public contracts. Add documentation only where it earns its place: enough to explain intent, invariants, and non-obvious tradeoffs without restating clear code.

## Scope

- Use selected or tagged code when the user provides it.
- Use specified files, directories, symbols, or descriptions when the user names a target.
- When the user asks for a general documentation pass with no target, inspect staged source-code changes first; if nothing is staged, inspect unstaged source-code changes.
- Restrict edits to source-code files in the languages present in the target or diff. Infer source files from extensions, project layout, imports, and build configuration; no extension list is exhaustive.
- Exclude docs, JSON, YAML, lockfiles, generated files, images, and other non-code files unless the user explicitly asks to edit them.
- If no source-code files remain after filtering, report that there is nothing to document and make no changes.

## Hard constraints

- Do not edit executable behavior.
- Do not rename symbols, reorder logic, simplify code, extract helpers, restructure files, or change formatting.
- Do not change APIs, types, serialized data, user-visible text, errors, snapshots, analytics events, accessibility semantics, timing, ordering, or persistence.
- Only add or improve these forms of documentation:
  - inline comments
  - language-appropriate API docs, such as docstrings, doc comments, JSDoc, rustdoc, Go doc comments, XML docs, or equivalent project conventions
  - focused documentation files, under the conditions in Step 5
- If the code is unclear because it needs simplification, renaming, or refactoring, do not fix it during this workflow; report that limitation instead.

## Workflow

1. Identify the target.
   - Prefer explicit user selection or tagged files over broader diffs.
   - Avoid unrelated files, even if nearby code could also benefit from documentation.

2. Read enough surrounding context.
   - Inspect callers, exported APIs, tests, types, nearby comments, existing docs, and local conventions when they explain intent, plus commit and PR history — often the only place the why was recorded.
   - Understand the behavior before documenting it: inputs, outputs, side effects, error paths, lifecycle ordering, retries, idempotency, concurrency, persistence, and business rules.
   - Stop when you can state the behavior and the why behind each non-obvious part of the target.
   - When intent remains unclear after reasonable reading, say so instead of inventing rationale: code that makes sense today may have been written for reasons that no longer apply, and a retrofitted rationale written into a comment becomes false documentation.
   - Prefer established project terms over inventing new vocabulary.

3. Document only what helps understanding.
   - Document non-obvious invariants, assumptions, preconditions, and ownership rules, plus the tradeoffs, rejected alternatives, and compatibility or migration constraints behind them.
   - Distinguish deliberate surprise from accidental: behavior forced by an external dependency, platform, or protocol, or chosen for a reason — a constraint, a tradeoff — earns a comment; confusing structure with no rationale behind it is a refactor target — route it to `Needs refactor, but not changed` rather than papering over it with a comment.
   - Clarify concurrency, ordering, cleanup, retry, backoff, and idempotency expectations, and fallback, failure-mode, or boundary behavior that is easy to misread.
   - Capture business or domain rules that are not obvious from syntax alone.
   - Describe private helper intent when a reader would reasonably ask why the helper exists.
   - Use language-appropriate API docs for public APIs, exported APIs, and complex private helpers when parameter meaning, return semantics, side effects, errors, invariants, domain rules, or lifecycle responsibilities are not obvious from the signature.
   - Let simple private functions stand on clear names and signatures; mandatory docstrings for obvious code create noise and stale docs.

4. Leave clear code alone.
   - Add a comment only where a competent reader would otherwise pause to ask "why"; if you cannot name that question, leave the code uncommented.
   - Pin comments to intent and stable behavior so they stay correct when implementation details change.
   - When each edge case would need its own comment, recommend a test in the summary instead of comment-listing them. Likewise for a "must not change" invariant: document it, and recommend the cheapest enforceable check — a type, test, or lint — in the summary, because prose cannot enforce.

5. Write documentation in the right place.
   - Default to a local comment. Use one whenever the rationale fits beside a single branch, helper, or call site.
   - Name an invariant once at the boundary that owns it, not in every consumer: the reader learns it once, and copies cannot drift.
   - Choose a doc file only when all of these hold: the rationale is needed to understand code in two or more files or modules, it cannot sit next to any single one without losing context, and inlining it would repeat the same explanation in more than one place. When undecided, keep it local.
   - Keep one source of truth: put the full rationale in the doc file, then leave a short local comment that points to it only where a nearby reader needs the pointer and immediate rationale.
   - In focused doc files, use a diagram (sequence, state, flow) when cross-module structure, lifecycle, or ordering is easier to grasp visually than in prose. Follow the repo's existing diagram conventions if any; otherwise default to mermaid in markdown files. Never diagram what a sentence covers, and keep diagrams pinned to behavior that is stable, not implementation details that will drift.
   - Place new docs beside existing relevant docs when possible, and keep them narrowly scoped.

6. Match local style.
   - Follow the repository's comment style, language-specific documentation conventions, capitalization, punctuation, and terminology.
   - Keep comments close to the code they explain.
   - Prefer concise comments over block comments unless a public API or multi-step invariant needs structure.
   - Preserve useful existing comments, and update stale or misleading ones only within the target: review existing comments and docstrings in the touched area and fix any that no longer match the implementation, behavior, constraints, or public contract.

7. Validate the result.
   - Re-read the diff and confirm only comments, docstrings, or explicitly needed docs changed.
   - Confirm executable code, formatting-only structure, generated files, and unrelated files were not touched.
   - Check that every added comment explains intent, rationale, constraints, or non-obvious behavior.
   - Run the narrowest relevant validation if available, such as lint or docs checks, when comments or docstrings can affect tooling.
   - If checks are unavailable or unnecessary for a comments-only change, say so.

## Output

Return a concise summary proportional to the change. For small tasks, use a short paragraph or 2-4 concrete bullets that cover what was documented and whether validation ran.

For larger documentation passes, include only the sections that add useful signal:

- `Files reviewed`: list reviewed source files.
- `Comments/docstrings added`: list changed files or nearest symbols.
- `Docs added`: list new or updated documentation files.
- `Needs refactor, but not changed`: list unclear areas where the real fix is simplification, naming, or structure.
- `Validation`: list commands run and results, or state why none were run.

Do not claim behavior changed, bugs were fixed, or code was simplified. The deliverable is better understanding with unchanged behavior.
