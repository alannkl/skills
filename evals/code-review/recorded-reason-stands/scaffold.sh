#!/usr/bin/env bash
# Build a repository in the run's workspace (the current directory): the base
# project on main, then the change committed on the feature branch. Write the
# pull request's description and diff to files, since the run has no shell.
set -euo pipefail
src="$(dirname "$0")/fixture"
git init -q -b main .
cp -R "$src/base/." .
git add -A
git -c user.name=Eval -c user.email=eval@example.com commit -q -m "Initial project"
git checkout -q -b feature
cp -R "$src/change/." .
git add -A
git -c user.name=Eval -c user.email=eval@example.com commit -q -F "$src/commit-message.txt"
cp "$src/commit-message.txt" PR.md
git diff main...feature > change.patch
printf 'PR.md\nchange.patch\n' >> .git/info/exclude
