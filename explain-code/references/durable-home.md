# Durable Home

Write the explainer to a destination where future readers will already look.

- Change scope: the destination is the PR description or extended commit-message body, so the explainer persists where reviewers and future readers already look.
- Other scopes: name the concrete destination where the explainer belongs — the relevant README section, an existing docs page, an architecture note — not a vague "this could be documented". Keep it markdown; mermaid renders where docs live.
- Update docs or run git or gh commands only with the user's explicit go-ahead: an explainer is written for one reader at one moment, and silently merging it into shared docs invites rot and duplication. Adapt it to the destination's audience and mode — a how-to section should not absorb explanation-mode prose wholesale — rather than pasting verbatim.
- Keep the explainer's confidence language intact when folding it in: inference labels and hedges are findings, not style, and must survive the merge.
- Write the full explanation, not a summary, unless the user asks for less.
- The final document must read as a single cohesive explanation, not an original plus an appended explainer: where the destination already covers a point the explainer also makes, fold the explainer's treatment into that existing content so nothing is explained twice; content the destination doesn't cover is simply added where it fits the document's flow.
- Carry the explainer's diagrams over with it, placed where they support the surrounding text — unless the destination already has a diagram covering the same thing, in which case keep the existing one.
