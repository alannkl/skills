#!/usr/bin/env bash
# Build the Ledger API repository with its long CLAUDE.md as one commit, so the original stays retrievable.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
export GIT_AUTHOR_DATE="2026-10-27T10:00:00Z" GIT_COMMITTER_DATE="2026-10-27T10:00:00Z"
git init -q -b main .
cp -R "$src/." .
git add -A && git commit -q -m "Ledger API"
# The team's remote is a GitHub URL the sandbox cannot reach.
git remote add origin git@github.com:acme/ledger-api.git
