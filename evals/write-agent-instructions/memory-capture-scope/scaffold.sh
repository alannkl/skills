#!/usr/bin/env bash
# Copy the fixture into the workspace (the current directory) as a git repo on a clean main.
set -euo pipefail
cp -R "$(dirname "$0")/fixture/." .
git init -q -b main
git -c user.name=dev -c user.email=dev@example.com add -A
git -c user.name=dev -c user.email=dev@example.com commit -q -m "chore: current state"
