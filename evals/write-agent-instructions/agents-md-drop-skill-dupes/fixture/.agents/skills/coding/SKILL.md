---
name: coding
description: Coding rules for this repository. Use when writing or changing Python or TypeScript code in `shop/`, `web/` or `tests/`. Not for docs or CI changes.
---

# Coding rules

- Never push directly to `main`; open a pull request.
- Never add a dependency without asking first.
- Run `make test` before committing.
- Keep each commit to one logical change.
- Never commit secrets; read them from environment variables.
- Type-annotate every new Python function.
- Use the `pytest` fixtures in `tests/conftest.py`, never ad-hoc setup.
