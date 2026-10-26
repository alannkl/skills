#!/usr/bin/env bash
# Copy the fixture into the workspace as a git repo on main with merged, unmerged and release branches.
set -euo pipefail
cp -R "$(dirname "$0")/fixture/." .
g() { git -c user.name=dev -c user.email=dev@example.com "$@"; }
git init -q -b main
g add -A && g commit -q -m "chore: current state"
for b in feat/login-form fix/null-total chore/bump-eslint; do
  g checkout -q -b "$b" main && echo "$b" > "notes-${b//\//-}.txt" && g add -A && g commit -q -m "$b"
  g checkout -q main && g merge -q --no-ff "$b" -m "merge $b"
done
g checkout -q -b release/1.4 main
g checkout -q -b feat/wip-search main && echo wip > search.txt && g add -A && g commit -q -m "wip search"
g checkout -q main
