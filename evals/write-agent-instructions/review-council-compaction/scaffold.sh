#!/usr/bin/env bash
# Copy the fixture into the workspace (the current directory) as a git repo on a clean main.
set -euo pipefail
export GIT_AUTHOR_NAME=dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=dev GIT_COMMITTER_EMAIL=dev@example.com
cp -R "$(dirname "$0")/fixture/." .
git init -q -b main
git add -A
git commit -q -m "chore: current state"
