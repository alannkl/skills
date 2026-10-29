#!/usr/bin/env bash
# Build the acme CLI repository on main: releases v2.3.0 and v2.3.1 with changelog sections, v2.4.0 released
# without one, then two commits after the v2.4.0 tag. Earlier states are derived from the fixture's final files.
# origin is a GitHub URL the sandbox cannot reach, so a push fails.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -am "$2"; }
set_version() { sed -i.bak "s/\"version\": \"[0-9.]*\"/\"version\": \"$1\"/" package.json package-lock.json && rm -f ./*.bak; }

git init -q -b main .
cp -R "$src/." .

# v2.3.0: no logout or whoami, login hangs when the browser closes, refresh waits a minute past expiry.
grep -v -e logout -e whoami bin/acme.js > bin/acme.js.tmp && mv bin/acme.js.tmp bin/acme.js
grep -v 'on("exit"' lib/login.js > lib/login.js.tmp && mv lib/login.js.tmp lib/login.js
sed -e '/function clear/{N;d;}' -e 's/load, clear, needsRefresh/load, needsRefresh/' \
  -e 's/Date.now() >= session.expiresAt/Date.now() > session.expiresAt + 60_000/' lib/session.js > lib/session.js.tmp
mv lib/session.js.tmp lib/session.js
sed '/^## \[2.3.1\]/,/^## \[2.3.0\]/{/^## \[2.3.0\]/!d;}' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
set_version 2.3.0
git add -A
commit "2026-09-15T10:00:00Z" "Release v2.3.0"
git tag v2.3.0

cp "$src/lib/login.js" lib/login.js
commit "2026-09-30T15:20:00Z" "Fix login hang when the browser window is closed"
cp "$src/CHANGELOG.md" CHANGELOG.md
commit "2026-10-02T09:10:00Z" "Changelog for 2.3.1"
set_version 2.3.1
commit "2026-10-02T09:12:00Z" "Release v2.3.1"
git tag v2.3.1

grep -v whoami "$src/bin/acme.js" > bin/acme.js
sed 's/Date.now() >= session.expiresAt/Date.now() > session.expiresAt + 60_000/' "$src/lib/session.js" > lib/session.js
commit "2026-10-20T11:45:00Z" "Add acme logout"
set_version 2.4.0
commit "2026-10-28T21:30:00Z" "Release v2.4.0"
git tag v2.4.0

cp "$src/bin/acme.js" bin/acme.js
commit "2026-10-29T08:50:00Z" "Add acme whoami"
cp "$src/lib/session.js" lib/session.js
commit "2026-10-29T09:40:00Z" "Fix token refresh for expired sessions"

git remote add origin git@github.com:acme/acme-cli.git
