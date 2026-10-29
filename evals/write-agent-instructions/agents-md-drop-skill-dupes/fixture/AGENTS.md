# Agent instructions

Shop is a Django 5 storefront; the frontend lives in `web/` (React, Vite).

- Use `uv` for Python dependencies and `pnpm` for `web/`; never pip or npm.
- Never push directly to `main` or `release/*`; open a pull request.
- Never add a dependency without asking first.
- Run `make test` before committing.
- Keep each commit to one logical change.
- Write commit messages in Conventional Commits format.
- Never commit secrets; read them from environment variables.
- Docs live in `docs/` and build with `mkdocs`; run `make docs` to check they build.
