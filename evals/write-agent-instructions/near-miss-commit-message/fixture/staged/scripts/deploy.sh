#!/usr/bin/env bash
# usage: deploy.sh [--dry-run] <staging|prod>
set -euo pipefail
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi
ENV="${1:?usage: deploy.sh [--dry-run] <staging|prod>}"
if [[ $DRY_RUN -eq 1 ]]; then
  helm diff upgrade shipyard ./chart -f "chart/values-$ENV.yaml" --namespace shipyard
  exit 0
fi
helm upgrade --install shipyard ./chart -f "chart/values-$ENV.yaml" --namespace shipyard --wait
