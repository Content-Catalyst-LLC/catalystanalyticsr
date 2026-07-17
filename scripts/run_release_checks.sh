#!/usr/bin/env bash
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_release.py
if command -v Rscript >/dev/null 2>&1; then
  Rscript scripts/check_r_sources.R
fi
