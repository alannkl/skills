#!/usr/bin/env bash
# Build a repository in the run's workspace (the current directory) whose plan holds an open
# decision, with a remote the team pushes to. Reflogs start empty, so any commit the agent makes shows.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
git init -q -b main .
cp -R "$src/." .
git add -A
git commit -q -m "Plan the eval runner and record D9-D11"
git remote add origin git@github.com:acme/eval-runner.git
rm -rf .git/logs
