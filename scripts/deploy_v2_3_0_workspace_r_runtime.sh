#!/usr/bin/env bash
set -euo pipefail
VERSION="2.3.0"
REPO_DIR="${1:-/opt/sustainable-catalyst/catalystanalyticsr}"
WORKSPACE_BACKEND="${WORKSPACE_BACKEND:-/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.9.1}"
MODE="${2:-validate}"
echo "=== CATALYST ANALYTICS R ${VERSION} - UNCERTAINTY & SENSITIVITY RUNTIME ==="
cd "$REPO_DIR"
rm -rf /tmp/catalyst-r-release-v230-venv
python3 -m venv /tmp/catalyst-r-release-v230-venv
/tmp/catalyst-r-release-v230-venv/bin/pip -q install jsonschema pytest
PYTHONDONTWRITEBYTECODE=1 /tmp/catalyst-r-release-v230-venv/bin/python scripts/check_release.py
rm -rf /tmp/catalyst-r-release-v230-venv
if [[ ! -d "$WORKSPACE_BACKEND/r-runtime" ]]; then echo "Workspace v3.9.1 backend r-runtime not found at $WORKSPACE_BACKEND" >&2; exit 2; fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp -a "$WORKSPACE_BACKEND/r-runtime/." "$TMP/"
rm -rf "$TMP/vendor/catalystanalyticsr"; mkdir -p "$TMP/vendor/catalystanalyticsr"
tar -C "$REPO_DIR" --exclude='.git' --exclude='.pytest_cache' --exclude='__pycache__' --exclude='dist' -cf - . | tar -C "$TMP/vendor/catalystanalyticsr" -xf -
python3 - "$TMP" <<'PYVPS'
from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'Dockerfile'; t=p.read_text().replace('== "2.2.0"','== "2.3.0"'); p.write_text(t)
p=root/'service.py'; t=p.read_text().replace('PROVIDER_VERSION = "2.2.0"','PROVIDER_VERSION = "2.3.0"'); p.write_text(t)
PYVPS
docker build -t catalystanalyticsr-runtime-validation:2.3.0 "$TMP"
docker run --rm --entrypoint Rscript catalystanalyticsr-runtime-validation:2.3.0 --vanilla -e 'library(catalystanalyticsr); stopifnot(as.character(packageVersion("catalystanalyticsr"))=="2.3.0"); m<-uncertainty_sensitivity_runtime_manifest(); stopifnot(m$contract=="sc.analytics-r.uncertainty-sensitivity-runtime.v1", isFALSE(m$boundary$arbitrary_function_dispatch), isTRUE(m$boundary$canonical_scenario_execution_only), isTRUE(m$boundary$human_review_required)); p<-catalyst_core_provider_manifest(); stopifnot(p$provider_version=="2.3.0", p$uncertainty_sensitivity_contract=="sc.analytics-r.uncertainty-sensitivity-runtime.v1"); cat("CATALYST_ANALYTICS_R_V230_RUNTIME=PASS\n")'
if [[ "$MODE" == "install" ]]; then
  echo "STOP: Workspace v3.9.1 pins provider metadata to 2.2.0. Promote v2.3.0 persistently through the next Workspace adapter release rather than mutating tagged v3.9.1 in place." >&2
  exit 3
fi
echo "PASS - Catalyst Analytics R v2.3.0 backend/runtime compatibility validated"
echo "NOTE - production Workspace image remains on provider 2.2.0 until the next Workspace adapter promotion"
