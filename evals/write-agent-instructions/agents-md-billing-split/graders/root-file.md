---
type: llm
focus: {source: file, path: AGENTS.md}
---

Judge the root AGENTS.md. It keeps the push, `make test`, Conventional Commits and both API rules; it no longer carries the billing-only rules (migration notes, refunds, currency codes) in full; it points to `src/billing/AGENTS.md` with a condition that names billing work or `src/billing/`; and it still requires never logging full card numbers (only the last four digits), because `src/api/routes.py` logs card data. If it no longer holds the integer-cents rule, `src/billing/AGENTS.md` must; keeping it in the root is fine.
