#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -m pip install -q pytest jsonschema
"$PYTHON_BIN" scripts/check_release.py

if command -v Rscript >/dev/null 2>&1; then
  Rscript scripts/check_r_sources.R
else
  echo "NOTICE: Rscript is unavailable; R parsing and R CMD check were not run locally." >&2
fi
