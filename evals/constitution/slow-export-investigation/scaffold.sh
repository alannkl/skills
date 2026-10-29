#!/usr/bin/env bash
# Build the export repository with its history and two weeks of nightly logs: smaller stream batches on 10-20,
# the per-row customer lookup merged on 10-21, and the 10-21 log, the only run between them, cut short.
set -euo pipefail
src="$(dirname "$0")/fixture"
export GIT_AUTHOR_NAME=Dev GIT_AUTHOR_EMAIL=dev@example.com GIT_COMMITTER_NAME=Dev GIT_COMMITTER_EMAIL=dev@example.com
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }
git init -q -b main .
cp -R "$src/base/." .
printf 'logs/\n' > .gitignore
git add -A && commit "2026-08-11T10:00:00Z" "Nightly orders export"
cp "$src/batch/export.js" scripts/export.js
git add -A && commit "2026-10-20T11:20:00Z" "Stream the export in batches of 10 to stay under the memory limit"
cp "$src/change/export.js" scripts/export.js
git add -A && commit "2026-10-21T15:02:00Z" "Include customer tier in export rows"
mkdir -p logs
row=1201344
for d in 14 15 16 17 18 19 20 22 23 24 25 26 27 28; do
  row=$((row + 2100 + d * 37))
  if [ "$d" -le 20 ]; then mins=$((38 + d % 4)); else mins=$((171 + d % 9)); fi
  printf '2026-10-%s 02:00:01 export started\n2026-10-%s 02:00:02 streaming orders\nrows exported %s, duration %sm\n' \
    "$d" "$d" "$row" "$mins" > "logs/export-2026-10-$d.log"
done
printf '2026-10-21 02:00:01 export started\n2026-10-21 02:00:02 streaming orders\n' | gzip > logs/export-2026-10-21.log.gz
truncate -s 30 logs/export-2026-10-21.log.gz
