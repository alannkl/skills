#!/usr/bin/env bash
# Builds a git repo in the current (empty) workspace with staged changes.
set -euo pipefail
FIX="$(cd "$(dirname "$0")" && pwd)/fixture"
cp -R "$FIX/base/." .
chmod +x scripts/deploy.sh
git init -q -b main
git config user.name "Sam Ortiz"
git config user.email "sam@example.com"
git add -A
git commit -qm "chore: initial import"
echo "Deploy with \`./scripts/deploy.sh <env>\` (needs helm and a kube context)." > README.md.tmp
{ echo "# shipyard"; echo; echo "Internal container registry UI."; echo; cat README.md.tmp; } > README.md
rm -f README.md.tmp
git commit -qam "docs(readme): note deploy prerequisites"
sed -i.bak 's/"shipyard")/"shipyard v0.2")/' src/main.go && rm -f src/main.go.bak
git commit -qam "fix(ui): show version in banner"
cp -R "$FIX/staged/." .
git add -A
