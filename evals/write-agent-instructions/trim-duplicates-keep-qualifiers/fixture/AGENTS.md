# Agent instructions

Apply `skills/base/SKILL.md` to every task, except typo fixes, pure prose edits and throwaway prototypes.

- Run the test suite before you commit.
- Never commit secrets; always read them from environment variables.
- Keep each commit to a single logical change.
- Ask before deleting or renaming files you did not create.
- Use pnpm, never npm or yarn.
- Open pull requests against `develop`, not `main`.
- See `docs/architecture.md` for the module layout.
- Write clear commit messages.
