---
type: llm
focus: {source: file, path: skills/stock-alert/SKILL.md}
---

Judge the edited `skills/stock-alert/SKILL.md`. The original steps put each tool or command in parentheses after an English label that restates it: "Read the profile (`get_profile`)", "Fetch quotes for the watchlist (`quotes-cli fetch`, ...)", "publish one post (`publish_post`, ...)". Pass only if each of `get_profile`, `quotes-cli fetch` and `publish_post` is now named once, as what its step acts on, and none sits in parentheses after words that restate it. A verb phrase that carries the identifier as its object passes, such as "Get the watchlist with `get_profile`" or "Fetch quotes for the watchlist with `quotes-cli fetch`". Everything the identifiers do not say must survive with its meaning: the profile supplies the watchlist; an empty watchlist ends the run without a post; quotes are fetched for the watchlist; the quotes skill documents the command; the 5% move since the previous close; one post with post_slug `moves` naming each such ticker and its move; otherwise no post; the steps run in order. Fail if any of these is lost or changed, or if a parenthesized label-then-identifier pair remains.
