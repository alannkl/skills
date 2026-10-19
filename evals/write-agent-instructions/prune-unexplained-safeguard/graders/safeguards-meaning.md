---
type: llm
focus: {source: file, path: AGENTS.md}
---

Judge AGENTS.md. It still forbids running `npm install` at the repository root and limits it to `packages/web`; it still forbids editing `config/flags.generated.json` by hand; it still says migrations in `db/migrations/` are never edited after they merge; it still requires `make lint` and `make test` before a pull request and forbids pushing directly to `main`. Wording may differ.
