# Publishing

## House style

- One line per ticker: symbol, move with sign and one decimal place, previous close.
- No emoji, no price targets, no advice.

## Retry

- On a timeout, retry `publish_post` once after 30 seconds.
- On any other error, do not retry; report the error text to the user.
