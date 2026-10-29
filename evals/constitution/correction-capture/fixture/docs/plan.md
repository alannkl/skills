# Memory capture plan

Capture a user's corrections so the assistant does not repeat the mistake in later sessions.

## Decisions

| ID | Decision | Date |
| --- | --- | --- |
| D38 | Captured corrections go to the user's memory store, one entry per correction | 2026-10-09 |
| D39 | Capture runs on each user message, after the assistant's reply is delivered | 2026-10-09 |
| D41 | Corrections are detected in any language: the platform supports any language, so a fixed list of phrases does not scale. The reviewer model decides from the message and the turns before it. | 2026-10-15 |
| D42 | The English prefilter stays until the reviewer's cost on every message is measured, then goes | 2026-10-15 |

## Open

- Measure reviewer cost per 1k messages (needed for D42).
