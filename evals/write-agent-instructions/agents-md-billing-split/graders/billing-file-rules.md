---
type: llm
focus: {source: file, path: src/billing/AGENTS.md}
---

Judge `src/billing/AGENTS.md`. It keeps, with their meaning: every change to `src/billing/` needs a migration note in `docs/billing-changes.md`, newest entry first; refunds over 500.00 require the `manual_review` flag set to `True`; currency codes are uppercase ISO 4217 strings and anything else is rejected with `InvalidCurrency`. The integer-cents rule and the card-number logging rule may appear here, in the root AGENTS.md, or both.
