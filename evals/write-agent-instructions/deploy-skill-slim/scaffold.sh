#!/usr/bin/env bash
# Copy the repo, commit it, then leave the user's newest rule uncommitted in SKILL.md.
set -euo pipefail
F="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
cp -R "$F/repo/." .
git init -q -b main
git add -A
git commit -q -m "chore: current state"
cp "$F/SKILL.working.md" .agents/skills/deploy/SKILL.md
