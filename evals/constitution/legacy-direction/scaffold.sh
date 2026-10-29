#!/usr/bin/env bash
# Build a repository in the run's workspace (the current directory) whose recent history moves SQL out of the
# route handlers into src/repos/, one table at a time; customers.js still queries inline.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
git init -q -b main .
cp -R "$src/base/." .
git add -A && commit "2026-06-02T10:00:00Z" "Shop API: customers, orders, products, carts, users"
mkdir -p src/repos
cp "$src/repos/users.js" src/repos/users.js && cp "$src/repos/users-route.js" src/routes/users.js
git add -A && commit "2026-09-22T09:40:00Z" "Move users queries into src/repos/users.js"
cp "$src/repos/orders.js" src/repos/orders.js && cp "$src/repos/orders-route.js" src/routes/orders.js
git add -A && commit "2026-10-06T14:05:00Z" "Move orders queries into src/repos/orders.js"
