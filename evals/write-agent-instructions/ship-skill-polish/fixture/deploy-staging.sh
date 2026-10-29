#!/usr/bin/env bash
# Deploy the API image to staging. Usage: ./deploy-staging.sh <tag>
set -euo pipefail
tag="${1:?usage: ./deploy-staging.sh <tag>}"
kubectl -n staging set image deploy/api api="registry.example.com/api:$tag"
