---
name: commit-message
description: Draft accurate commit-message text from real git changes, defaulting to Conventional Commits. Use when the user asks for a commit message or is committing work that needs one drafted.
---

# Commit Message

Draft commit-message text from the real git state. Default to Conventional Commits. Prefer concise bodies that explain behavior, impact, and required follow-up. This skill only drafts the message; staging, committing, amending, and pushing belong to the surrounding workflow.

## Workflow

1. Determine scope.
   - If the user explicitly narrowed the scope, honor that boundary and ignore unrelated changes.
   - If staged changes exist, default to staged changes unless the user asks to summarize all changes.
   - If no staged changes exist, use the relevant unstaged, untracked, or provided changes.
   - Inspect in-scope untracked files before summarizing them; `git diff` will not show their contents.
   - If there are no relevant changes, say so instead of inventing a message.
   - If unrelated changes would distort a single summary, separate them clearly or ask before mixing them into one message.

2. Inspect the diff and context.
   - Use available git status and diff information to identify staged, unstaged, and untracked changes in the chosen scope.
   - If git data is unavailable or the repo has no commits, say so and draft only from provided context.
   - Check recent commit messages when available. Follow repo-specific format, scope, and body conventions unless the user asks otherwise.
   - For code changes, inspect surrounding context until every header and bullet claim you will make traces to a specific hunk.
   - For docs, config, workflows, assets, lockfiles, or generated files, describe the operational effect instead of only naming files.
   - For binary, generated, or very large files, summarize from filenames, metadata, manifests, or nearby source changes rather than dumping content.
   - Surface migrations, environment variables, config changes, API or schema changes, data rewrites, dependency changes, and manual actions; mention sensitive keys without exposing secret values.

3. Choose the Conventional Commit header.
   - Use `type(scope): summary` when there is a meaningful scope.
   - Use `type: summary` when there is no meaningful scope.
   - Use `type(scope)!: summary` or `type!: summary` for breaking changes.
   - Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`, `style`, `revert`.
   - Pick a scope that reflects the affected product area, package, module, command, or workflow, not the file extension; omit the scope rather than force an inaccurate one.
   - Pick the type from the behavioral intent of the change, not the file type; user-visible fixes and features are never `chore`. Instruction-bearing text changes are `feat` when they add or meaningfully change capabilities, `fix` when they correct broken or misleading behavior, and `docs` only when they are explanatory-only.
   - Keep the first line concise. Reflect the main change and, when clear from the diff, the reason.
   - Use imperative present tense: `fix auth refresh handling`, not `fixed` or `fixes`.
   - If the user asks for a subject-only, short, or one-line message, return only this header.

4. Write the body.
   - Omit the body when the header alone covers the change, as it usually does for tiny single-purpose diffs.
   - For multi-part diffs, default to this base format:

     ```md
     type(scope): <brief summary of main changes>

     - <key behavior, feature, fix, or implementation change, including impact when meaningful>
     - <key behavior, feature, fix, or implementation change, including impact when meaningful>
     ```

   - Prefer behavior-oriented bullets over file-by-file summaries.
   - Include code-level or business-logic impact when it clarifies why the change matters. Do not speculate beyond the diff and nearby context.
   - Include issue references only when they are present in the request, branch name, diff, or repo convention.
   - Add `Required actions:` only for migrations, environment variables, manual steps, or operator follow-ups.
   - Add `BREAKING CHANGE:` footer lines for breaking changes so Conventional Commit tooling can detect them.

5. Validate before finalizing.
   - Confirm the header type matches the dominant intent of the change.
   - Confirm each bullet is supported by the diff.
   - Confirm code-impacting bullets describe user-visible behavior, system behavior, contracts, or meaningful implementation impact.
   - Confirm breaking changes and required actions are surfaced separately, not buried in normal change bullets.
   - Claim tests passed only when they were actually run.
   - Return the commit-message text and, if useful, briefly offer to commit with it.

## Example

Body with both footers:

```md
feat(api)!: require cursor pagination for users

- Replace offset pagination with cursor pagination on the users endpoint
- Add queue configuration for the cursor backfill worker

Required actions:

- Set `CURSOR_BACKFILL_QUEUE` before enabling the worker

BREAKING CHANGE: `GET /users` no longer accepts `page` or `per_page`; clients must send `cursor` and `limit`.
```
