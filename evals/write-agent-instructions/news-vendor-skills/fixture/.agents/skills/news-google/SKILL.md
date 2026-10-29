---
name: news-google
description: "Fetches recent news headlines for a company, ticker or topic from Google News. Use when the user asks for news, headlines or recent coverage."
---

# Google News headlines

Run `npx tsx .agents/skills/news-google/scripts/fetch.ts "<query>" [--days N]` (default 1).

## Output

JSON lines `{title, url, source, published_at}` (ISO 8601 UTC), newest first. Drop an item whose URL already appeared.
