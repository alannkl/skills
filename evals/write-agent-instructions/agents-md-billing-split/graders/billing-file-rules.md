---
type: llm
focus: {source: file, path: src/billing/AGENTS.md}
---

Judge `src/billing/AGENTS.md`. It keeps, with their meaning: every change to `src/billing/` needs a migration note in `docs/billing-changes.md`, newest entry first; refunds over 500.00 require the `manual_review` flag set to `True`. The integer-cents, currency-code and card-number logging rules may appear here, in the root AGENTS.md, or both.
