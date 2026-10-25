#!/usr/bin/env bash
# Build the repository in the run's workspace (the current directory): the last
# commit, then the change staged on top of it, as the user had it.
set -euo pipefail
src="$(dirname "$0")/fixture"
git init -q -b main .
cp -R "$src/base/." .
git add -A
git -c user.name=Eval -c user.email=eval@example.com commit -q -m "Initial commit"
cp -R "$src/staged/." .
git add -A
