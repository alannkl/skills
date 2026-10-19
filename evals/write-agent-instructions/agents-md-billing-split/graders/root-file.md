---
type: llm
focus: {source: file, path: AGENTS.md}
---

Judge the root AGENTS.md. It keeps the push, `make test`, Conventional Commits and both API rules; it no longer carries the migration-note and refund rules in full; it points to `src/billing/AGENTS.md` with a condition that names billing work or `src/billing/`; and it still requires never logging full card numbers (only the last four digits), because `src/api/routes.py` logs card data. The integer-cents and currency-code rules may stay here or move to the billing file.
