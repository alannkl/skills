---
name: quotes-yahoo
description: "Fetches price quotes from Yahoo Finance. Use when the user asks for a stock price, quote or day change."
---

# Yahoo Finance quotes

Run `npx tsx .agents/skills/quotes-yahoo/scripts/quote.ts <TICKER>...`.

It prints one JSON line per ticker: `{ticker, close, change, change_pct, currency}`, where `close` is the last close and `change` is against the previous close. A ticker Yahoo does not know prints `{ticker, error}`.
