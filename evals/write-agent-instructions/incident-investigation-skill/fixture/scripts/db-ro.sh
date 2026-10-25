#!/usr/bin/env bash
# Open psql on the production read replica with the read-only role.
# Usage: scripts/db-ro.sh [-c "SQL"]   (no -c opens an interactive session)
set -euo pipefail
: "${ORDERS_RO_URL:?set ORDERS_RO_URL (from 1Password: orders-api / read-replica)}"
exec psql "$ORDERS_RO_URL" --set=ON_ERROR_STOP=1 -X "$@"
