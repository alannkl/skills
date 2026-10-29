#!/usr/bin/env bash
# Build the support bot repository as one commit: the loader sends prompts/support_agent.md as the system prompt.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
export GIT_AUTHOR_DATE="2026-10-27T10:00:00Z" GIT_COMMITTER_DATE="2026-10-27T10:00:00Z"
git init -q -b main .
cp -R "$src/." .
git add -A && git commit -q -m "Support bot"
# The team's remote is a GitHub URL the sandbox cannot reach.
git remote add origin git@github.com:acme/invoicely-support.git
