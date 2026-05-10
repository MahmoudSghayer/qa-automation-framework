#!/usr/bin/env bash
# Generates and serves the Allure HTML report locally.
#
# Requires: allure CLI (brew install allure / scoop install allure)
set -euo pipefail

RESULTS_DIR=${ALLURE_RESULTS_DIR:-reports/allure-results}
REPORT_DIR=${ALLURE_REPORT_DIR:-reports/allure-report}

if ! command -v allure >/dev/null 2>&1; then
  echo "❌ allure CLI not found. Install: https://allurereport.org/docs/install/"
  exit 1
fi

if [ ! -d "$RESULTS_DIR" ] || [ -z "$(ls -A "$RESULTS_DIR" 2>/dev/null)" ]; then
  echo "❌ No results in $RESULTS_DIR. Run tests first."
  exit 1
fi

echo "▶ Generating report from $RESULTS_DIR"
allure generate "$RESULTS_DIR" --clean -o "$REPORT_DIR"
echo "▶ Opening report (Ctrl+C to stop)"
allure open "$REPORT_DIR"
