#!/usr/bin/env bash
# The repository at the last commit, then the uncommitted work the session had made since:
# usage.md renamed to panel-mode.md, pair-mode instructions moved to pair-mode.md.
set -euo pipefail
here="$(dirname "$0")/fixture"
cp -R "$here/committed/." .
git init -q
git add -A
git -c user.name=dev -c user.email=dev@example.com commit -qm "panel: trim rules restated across SKILL.md and references"
find . -path ./.git -prune -o -type f -print | sed 's|^\./||' | while read -r f; do
  [ -e "$here/working/$f" ] || rm "$f"
done
cp -R "$here/working/." .
