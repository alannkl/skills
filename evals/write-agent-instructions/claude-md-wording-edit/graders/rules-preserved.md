---
type: llm
focus: {source: file, path: CLAUDE.md}
---

Judge the edited CLAUDE.md. It still requires all of these, with the same conditions: never push directly to main, and open a pull request so a human can review it; commit messages in Conventional Commits format (the release bot parses the prefixes); before changing the billing module in `src/billing/`, read `docs/billing-rules.md`; run `make test` before opening a pull request; format replies to the user in Markdown. Wording may differ.
