---
name: google-news
description: "Fetches recent news for a stock ticker or company from Google News. Use when the user or the brief needs headlines, recent news, or what happened to a company or ticker."
---

# Google News

1. Build the query: the company name, plus the ticker in quotes, e.g. `"NVDA" Nvidia`.
2. Fetch the RSS feed: `curl -s "https://news.google.com/rss/search?q=<url-encoded query>&hl=en-US&gl=US&ceid=US:en"`.
3. Parse each `<item>`: title, link, pubDate, source.
4. Keep items from the last 48 hours; drop duplicates that share a title.
5. Return at most 10 items, newest first, as a markdown list: `- <title> (<source>, <pubDate>) <link>`.

If the feed returns no items, say so; do not fall back to web search.
