#!/usr/bin/env bash
# Usage: scripts/rollback.sh --env <staging|production> --revision <sha>
set -euo pipefail
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV="$2"; shift 2 ;;
    --revision) REV="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
rev="$(helm history web -n "$ENV" -o json | jq -r --arg r "$REV" '.[] | select(.description | contains($r)) | .revision')"
helm rollback web "$rev" -n "$ENV"
