#!/usr/bin/env bash
# Deploy the API image to production. Usage: ./deploy.sh <tag> [--blue-green]
set -euo pipefail
tag="${1:?usage: ./deploy.sh <tag> [--blue-green]}"
strategy=rolling
[[ "${2:-}" == "--blue-green" ]] && strategy=blue-green
kubectl -n production set image deploy/api api="registry.example.com/api:$tag"
kubectl -n production annotate deploy/api "deploy/strategy=$strategy" --overwrite
