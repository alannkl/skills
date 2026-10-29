---
name: news-newsapi
description: "Fetches recent news headlines for a company, ticker or topic from NewsAPI. Use when the user asks for news, headlines or recent coverage."
---

# NewsAPI headlines

Needs `NEWSAPI_KEY` in the environment.

Run `npx tsx .agents/skills/news-newsapi/scripts/fetch.ts "<query>" [--days N]` (default 1).

## Output

JSON lines `{title, url, source, published_at}` (ISO 8601 UTC), newest first. Drop an item whose title already appeared.
