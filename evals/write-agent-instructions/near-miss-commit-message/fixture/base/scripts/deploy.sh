#!/usr/bin/env bash
# usage: deploy.sh <staging|prod>
set -euo pipefail
ENV="${1:?usage: deploy.sh <staging|prod>}"
helm upgrade --install shipyard ./chart -f "chart/values-$ENV.yaml" --namespace shipyard --wait
