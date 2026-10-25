#!/usr/bin/env bash
# The workspace is the repository at the commit the owner asked from, with a clean tree.
set -euo pipefail
cp -R "$(dirname "$0")/fixture/." .
git init -q
git add -A
git -c user.name=dev -c user.email=dev@example.com commit -qm "panel: open relays with the host's actionable conclusion"
