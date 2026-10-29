#!/usr/bin/env bash
# Build the web service repository with its deploy skill and rollback script as one commit.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
export GIT_AUTHOR_DATE="2026-10-27T10:00:00Z" GIT_COMMITTER_DATE="2026-10-27T10:00:00Z"
git init -q -b main .
cp -R "$src/." .
git add -A && git commit -q -m "Web service with deploy skill"
# The team's remote is a GitHub URL the sandbox cannot reach.
git remote add origin git@github.com:acme/web.git
