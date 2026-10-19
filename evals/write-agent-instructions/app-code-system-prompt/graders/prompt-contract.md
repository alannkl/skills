---
type: llm
focus: {source: file, path: app/prompts.py}
---

Judge `app/prompts.py`. `SYSTEM_PROMPT` still requires a reply that is only a JSON object with keys `summary` (a string of at most three sentences), `actions` (a list of objects with `owner` and `task`, where `owner` is null when nobody owns the item) and `confidence` (a number from 0 to 1), and now states plainly that no text may appear outside the JSON. `MODEL` is still "claude-haiku-4-5" and `MAX_TOKENS` is still 800. The file is still valid Python.
