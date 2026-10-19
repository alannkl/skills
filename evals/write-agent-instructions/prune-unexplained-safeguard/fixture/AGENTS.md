# Agent instructions

- Always write clean, readable, well-structured code.
- Be careful and think things through before making changes.
- Run `make lint` and `make test` before you open a pull request.
- Never push directly to `main`; open a pull request.
- Make sure your code works.
- Run `npm install` only inside `packages/web`, never at the repository root (#412).
- Write helpful commit messages that explain what you did.
- Never edit `config/flags.generated.json` by hand.
- Try your best to follow good engineering practices.
- Keep pull requests focused on one change.
- Remember to double-check your work before you finish.
- Database migrations go in `db/migrations/` and are never edited after they merge.
