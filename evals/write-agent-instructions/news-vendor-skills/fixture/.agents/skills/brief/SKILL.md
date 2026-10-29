---
name: brief
description: Writes the morning brief for the tickers in watchlist.json.
disable-model-invocation: true
---

# Morning brief

Writes the morning brief for the tickers in `watchlist.json`.

1. For each ticker, load `news-google`, `news-newsapi` and `news-gdelt` and run each one's fetch.
2. Load `quotes-yahoo` for the close and day change.
3. Merge the headlines, newest first.
4. Write `briefs/<date>.md`: per ticker, the price line, then up to five headlines.
