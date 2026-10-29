#!/usr/bin/env bash
# Build the repository with auth already moved from JWT bearer tokens to cookie sessions in Redis; the README
# still documents the tokens.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
git init -q -b main .
cp -R "$src/base/." .
printf '{"name":"notes-api","private":true,"main":"src/server.js","scripts":{"start":"node src/server.js"},"dependencies":{"express":"^4.19.2","jsonwebtoken":"^9.0.2","pg":"^8.11.3"}}\n' > package.json
git add -A && commit "2026-07-01T10:00:00Z" "Notes API with JWT auth"
cp "$src/change/server.js" src/server.js
printf '{"name":"notes-api","private":true,"main":"src/server.js","scripts":{"start":"node src/server.js"},"dependencies":{"connect-redis":"^7.1.1","express":"^4.19.2","express-session":"^1.18.0","pg":"^8.11.3","redis":"^4.6.13"}}\n' > package.json
git add -A && commit "2026-10-27T16:30:00Z" "Replace JWT bearer tokens with cookie sessions in Redis"
