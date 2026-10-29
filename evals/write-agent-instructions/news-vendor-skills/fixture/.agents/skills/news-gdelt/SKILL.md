---
name: news-gdelt
description: "Fetches recent news headlines for a company, ticker or topic from GDELT. Use when the user asks for news, headlines or recent coverage."
---

# GDELT headlines

Run `npx tsx .agents/skills/news-gdelt/scripts/fetch.ts "<query>" [--days N]` (default 1).

## Output

JSON lines `{title, url, source, publishedAt}` (ISO 8601 UTC), newest first. Drop an item whose URL already appeared.
