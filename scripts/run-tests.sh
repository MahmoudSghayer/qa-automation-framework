#!/usr/bin/env bash
# Usage:
#   ./scripts/run-tests.sh                 # smoke, parallel
#   ./scripts/run-tests.sh regression      # full regression
#   ./scripts/run-tests.sh api -v          # api only, verbose
set -euo pipefail

MARKER=${1:-smoke}
shift || true

echo "▶ Running marker='${MARKER}' on env='${TEST_ENV:-staging}'"

pytest -m "${MARKER}" \
       -n "${PYTEST_WORKERS:-auto}" \
       --reruns 2 --reruns-delay 1 \
       --alluredir=reports/allure-results \
       "$@"
