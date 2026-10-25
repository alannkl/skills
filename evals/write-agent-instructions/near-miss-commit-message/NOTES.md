# near-miss-commit-message

**Near miss:** writing a commit message, though one of the staged files is a `.claude/commands/` file. `trigger_only`.

**Setup:** `scaffold.sh` copies `fixture/base`, makes three conventional commits, then overlays `fixture/staged` and stages it. It locates `fixture/` next to itself.

**Good result:** e.g. `feat(deploy): add --dry-run and confirm before deploying` with a short body covering both files. Not committed (the user asked for the message).

**Plausible bad results:** describing only the script or only the command; editing the command file; running `git commit`.

**Judgment calls:** `no-commit-made` (anchored `^git commit\b`, failed attempts count) treats committing as outside the request; a user who wanted it committed would usually say so. The task is read-only, so `no-files-changed` and `no-writes` also apply. A scope-less Conventional Commit subject passes.
