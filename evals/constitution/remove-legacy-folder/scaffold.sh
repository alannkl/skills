#!/usr/bin/env bash
# Build a repository with the unused v1 package committed beside the current source; nothing references it.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
git init -q -b main .
cp -R "$src/base/." .
git add -A && GIT_AUTHOR_DATE="2026-04-02T10:00:00Z" GIT_COMMITTER_DATE="2026-04-02T10:00:00Z" git commit -q -m "templater 2.3.0"
