# near-miss-readme-running-locally

**Near miss:** a human-facing README edit, not agent instructions. `trigger_only`.

**User:** ML tooling maintainer who dropped Docker for local dev.

**Good result:** Running locally says `make setup` once, then `make dev`, open http://localhost:8080 (the Makefile changed the port from 8000). The ~200 MB download note can move to `make setup`. Nothing else changes.

**Plausible bad results:** only swapping the command and keeping port 8000; omitting `make setup` (without it `make dev` fails, no venv); editing other sections.
