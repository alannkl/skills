---
name: stock-alert
description: Checks the user's watchlist for large price moves and publishes one alert post. Use when the scheduled stock-alert job runs.
---

# Stock alert

Run these steps in order.

1. Read the profile (`get_profile`) for the watchlist; if it is empty, finish without a post.
2. Fetch quotes for the watchlist (`quotes-cli fetch`, the quotes skill).
3. If any ticker moved more than 5% since the previous close, publish one post (`publish_post`, post_slug `moves`) naming each such ticker and its move.
4. Otherwise, finish without a post.

Make sure that you always follow every one of the steps above carefully and in the correct order.
