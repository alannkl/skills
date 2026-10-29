#!/usr/bin/env bash
# Build a repository whose main has merged three feature branches, one still open, with every branch also on
# the team's remote, where one merged branch has a teammate's later commit. The remote is a GitHub URL the sandbox cannot reach; its tracking refs show what is there.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
git init -q -b main .
cp -R "$src/." .
git add -A && git commit -q -m "Billing service"
branch() { git checkout -q -b "$1" main; f="src/$(basename "$1").js"; mkdir -p src; echo "// $2" > "$f"; git add "$f"; git commit -qm "$2"; }
branch feature/invoice-pdf "Render invoices as PDF"
branch fix/webhook-retry "Retry failed webhooks"
branch chore/bump-node "Run on Node 22"
branch feature/tax-rates "Per-region tax rates (in progress)"
git checkout -q main
for b in feature/invoice-pdf fix/webhook-retry chore/bump-node; do git merge -q --no-ff -m "Merge $b" "$b"; done
remote="$(mktemp -d)"
git init -q --bare "$remote"
git remote add origin "$remote"
git push -q origin main feature/invoice-pdf fix/webhook-retry chore/bump-node feature/tax-rates
# A teammate pushed a follow-up to fix/webhook-retry after it was merged, so only the remote copy holds it.
mate="$(mktemp -d)"
git clone -q --branch fix/webhook-retry "$remote" "$mate"
echo "// Log each retry attempt" >> "$mate/src/webhook-retry.js"
git -C "$mate" commit -qam "Log webhook retry attempts" --author="Sam Lee <sam@example.com>"
git -C "$mate" push -q origin fix/webhook-retry
rm -rf "$mate"
git fetch -q origin
git branch -q -u origin/main main
git remote set-url origin git@github.com:acme/billing-service.git
rm -rf "$remote"
