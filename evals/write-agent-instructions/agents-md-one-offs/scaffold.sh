#!/usr/bin/env bash
# Build the repo with the history behind the proration note and the stale notes.
set -euo pipefail
F="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dana GIT_AUTHOR_EMAIL=dana@example.com GIT_COMMITTER_NAME=Dana GIT_COMMITTER_EMAIL=dana@example.com
cp -R "$F/repo/." .
git init -q -b main
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2" ${3:+-m "$3"}; }
cp "$F/history/AGENTS.v1.md" AGENTS.md
cp "$F/history/proration.v1.py" app/billing/proration.py
mkdir -p legacy && cp "$F/history/importer.py" legacy/importer.py
git add -A && c 2026-05-12T10:00:00 "chore: initial import"
cp "$F/repo/app/billing/proration.py" app/billing/proration.py
cp "$F/history/AGENTS.v2.md" AGENTS.md
git add -A && c 2026-07-08T16:20:00 "fix(billing): round each line item before summing (#318)" "Rounding only the total disagreed with Stripe's invoices by a cent on multi-line invoices; finance reissued 41 invoices. An agent refactor had simplified the per-line rounding, so AGENTS.md now warns against it."
git rm -rq legacy && c 2026-09-15T09:00:00 "chore: remove legacy importer"
cp "$F/repo/AGENTS.md" AGENTS.md
git add -A && c 2026-09-28T11:30:00 "docs(agents): note staging db outage"
