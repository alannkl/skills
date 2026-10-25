#!/usr/bin/env bash
# usage: wait-for-pg.sh HOST PORT
set -euo pipefail
for i in $(seq 1 30); do
  if pg_isready -h "$1" -p "$2" >/dev/null 2>&1; then
    exit 0
  fi
  sleep 1
done
echo "postgres at $1:$2 not ready after 30s" >&2
exit 1
