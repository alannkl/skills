#!/usr/bin/env bash
# Copy the fixture into the workspace as a git repo on main, with .claude/skills linked to .agents/skills and no remote.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
git init -q -b main .
cp -R "$src/." .
mkdir -p .claude
ln -s ../.agents/skills .claude/skills
git add -A && git commit -q -m "Add deploy-status skill and promotion runbook"
