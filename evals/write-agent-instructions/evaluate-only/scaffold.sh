#!/usr/bin/env bash
# Copy the fixture project into the run's workspace (the current directory).
set -euo pipefail
cp -R "$(dirname "$0")/fixture/." .
