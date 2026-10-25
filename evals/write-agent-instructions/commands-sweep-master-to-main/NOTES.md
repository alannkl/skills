# commands-sweep-master-to-main

**Family:** 3 (find and fix an issue across several instruction files). **Harness:** Claude Code, `.claude/commands/`. **Domain:** Rails web app. **User:** contributor on a team repo they don't own, so they want the edit kept to the branch references.

**Why realistic:** after a default-branch rename, slash commands with `master` baked into git ranges quietly break or diff against a stale ref. Sweeping them is a common chore.

**Good result:** three files edited (`review-pr.md`, `changelog.md`, `sync-branch.md`), each `master` reference replaced by `main`/`origin/main` (or default-branch detection), nothing else touched. `new-migration.md` has no branch reference and stays as is.

**Plausible bad results:** missing one file; editing `new-migration.md` or improving the commands' other wording despite "keep it to the branch stuff"; touching CLAUDE.md (already says `main`).

**Judgment calls:** the three per-file graders are llm checks that the command no longer assumes `master` is the default branch (uses `main`/`origin/main` or detects the default branch); a note mentioning the old name passes. Reporting which files changed is diagnostic.
