#!/usr/bin/env bash
# Build a checkout repository whose last commit adds member discounts: the discount is computed in orderTotal
# but never applied, which is what the lint error points at. The tests cover only the discount rates and
# non-member totals, so they pass either way.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
git init -q -b main .
cp -R "$src/base/." .
printf 'node_modules/\n' > .gitignore
git add -A && commit "2026-09-30T10:00:00Z" "Checkout totals with free shipping from 50.00"
cp "$src/change/discounts.js" src/checkout/discounts.js
cp "$src/change/total.js" src/checkout/total.js
cp "$src/change/discounts.test.js" test/discounts.test.js
cp "$src/change/summary.js" src/checkout/summary.js
git add -A && commit "2026-10-28T17:45:00Z" "Member discount at checkout (#212)"
