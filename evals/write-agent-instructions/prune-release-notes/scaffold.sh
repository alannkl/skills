#!/usr/bin/env bash
# Copy the fixture project into the workspace as a git repo, then leave one uncommitted edit to the skill.
set -euo pipefail
cp -R "$(dirname "$0")/fixture/." .
git init -q -b main
git -c user.name=dev -c user.email=dev@example.com add -A
git -c user.name=dev -c user.email=dev@example.com commit -q -m "chore: current state"
sed -i 's/^   - Never mention internal ticket IDs/   - End each entry with its pull request number, such as `(#123)`.\n&/' release-notes/SKILL.md
