---
name: stock-quote
description: "Gets the latest price, daily change and volume for a stock ticker from Yahoo Finance. Use when the user or the brief needs a quote, price, or how a stock moved today."
---

# Stock quote

1. Fetch: `curl -s "https://query1.finance.yahoo.com/v8/finance/chart/<TICKER>?range=1d&interval=1d" -H "User-Agent: Mozilla/5.0"`.
2. From `chart.result[0].meta`, read `regularMarketPrice`, `chartPreviousClose`, `regularMarketVolume` and `currency`.
3. Compute the change and percent change against `chartPreviousClose`.
4. Reply: `<TICKER> <price> <currency> (<+/-change>, <+/-pct>%) vol <volume>`.

If the request fails or `chart.error` is set, report the error; do not guess a price.
