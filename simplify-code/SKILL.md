---
name: simplify-code
description: Simplify source code for clarity, consistency, and maintainability while preserving exact behavior. Use when the user asks to simplify code, clean up logic, reduce complexity, improve readability, refactor without behavior changes, or run a code-simplifier pass on selected files, directories, or the current git diff.
---

# Simplify Code

Improve code clarity, consistency, and maintainability without changing behavior. Follow local project conventions, prefer readable code over clever compactness, and avoid expanding code merely to look more explicit. The result should be easier to read, debug, and maintain, with the same observable behavior and no broader scope than the original.

## Scope

- Use selected or tagged code when the user provides it.
- Use specified files, directories, or descriptions when the user names a target.
- When the user asks for a general simplify pass with no target, inspect staged source-code changes first; if nothing is staged, inspect unstaged source-code changes.
- Restrict edits to source-code files in the languages present in the target or diff; a repository may contain more than one. Infer the languages from target files, nearby code, project layout, and build configuration; do not treat any extension list as exhaustive.
- Exclude docs, JSON, YAML, lockfiles, images, and other non-code files from simplification scope unless the user explicitly asks to edit them.
- If no source-code files remain after filtering, report that there is nothing to simplify and make no changes.

## Workflow

1. Identify the target code.
   - Read the relevant files, local conventions, and nearby patterns before editing.
   - Understand the externally observable behavior: inputs, outputs, side effects, error handling, rendered output, accessibility semantics, persistence, public API shape, serialization, ordering, timing, and user-visible text.
   - Check nearby tests or examples before changing subtle logic; use them to anchor behavior when available.
   - Note any ambiguity that could change behavior; proceed on reasonable assumptions, but stop and ask only when guessing wrong about intent could change observable behavior.

2. Find meaningful simplifications.
   - Reduce unnecessary branching, nesting, duplication, and indirection.
   - Consolidate nearly identical branch bodies when only small payload fields differ.
   - Avoid nested ternaries; use a switch or if/else chain when there are multiple conditions.
   - Prefer concise direct mappings for simple binary or enum mappings when readable, such as `A -> x` and `B -> y`.
   - Keep related logic together when doing so reduces jumping around without mixing separate concerns.
   - Favor compact, DRY implementations when they remain clear and debuggable, but keep small one-off decisions inline when extracting a helper would add naming overhead without reuse.
   - Prefer the simplest readable form; do not expand code only to appear more explicit.
   - Improve unclear variable, function, prop, or type names when the better name reflects established project language.
   - Avoid combining too many concerns into one function, component, module, or abstraction.
   - Do not introduce new helper functions, types, options, wrappers, or layers unless they reduce real complexity, isolate meaningful behavior, improve testability, or are reused.
   - Remove an existing abstraction only when it carries no real domain meaning, reuse, testability, or separation of concerns.
   - Reject a refactor if it increases cognitive load without a clear payoff.
   - Remove comments that explain obvious syntax or control flow, but preserve comments that explain intent, tradeoffs, invariants, or non-obvious behavior.
   - Remove commented-out code only when it is clearly stale noise and local practice supports doing so; otherwise leave it or ask.

3. Preserve behavior and follow standards.
   - Keep all original features, outputs, side effects, errors, ordering, and edge-case behavior intact.
   - Preserve externally visible contracts such as public APIs, exported names, type contracts, wire formats, storage keys, analytics events, error text, DOM shape, ARIA labels, and snapshot-sensitive output unless the user explicitly wants them changed or local tests and conventions show they are internal and safe to update.
   - Follow project standards for language conventions, modules and imports, types or interfaces, components, error handling, and naming.
   - Apply framework-specific standards when relevant, such as import ordering, explicit public or top-level types, component prop patterns, and file extension conventions.

4. Avoid cosmetic-only churn.
   - Do not reformat code merely by changing line breaks, wrapping, indentation, function signatures, argument lists, or multi-line expression shape.
   - Let the formatter handle formatting.
   - Touch formatting only as a side effect of a meaningful simplification.
   - If before and after are equally readable, prefer the version with fewer moving parts and less diff.

5. Validate the result.
   - Re-read the changed code and compare business logic and externally observable behavior against the original, including subtle edge-case differences.
   - Verify the refined code is simpler and more maintainable, not just shorter.
   - Run the narrowest relevant checks available, such as targeted tests, typecheck, lint, or build.
   - If checks are unavailable or too broad for the task, state the gap.
   - Review the diff and remove unrelated churn.

## Output

Keep the final summary proportional to the change. For small tasks, use 1-3 concrete bullets or a short paragraph covering what changed and how it was validated.

For larger passes, use this structure:

- `Files examined`: list reviewed source files.
- `Files already good (no changes needed)`: list reviewed files that needed no changes.
- `Files simplified`: use one point per changed file, with sub-points for each meaningful simplification:
  - before: the old shape or source of complexity
  - after: the new shape
  - what changed: the concrete simplification
  - why better: readability, maintainability, lower duplication, or reduced cognitive load
- `Validation`: list commands run and results, or state what was not run.

Keep the summary concrete and include only significant changes that affect understanding. Do not claim behavior changed, performance improved, or bugs were fixed unless the simplification actually did that and validation supports it.

## Gotchas

- Do not turn simplification into broad refactoring or architecture redesign.
- Do not prioritize fewer lines over readability.
- Do not create dense one-liners, nested ternaries, or clever abstractions.
- Do not make the code harder to debug or extend.
- Do not duplicate nearly identical code when a compact shared path is clearer.
- Do not delete useful abstractions that preserve boundaries or domain meaning.
- Do not edit unrelated files just because they are nearby.
