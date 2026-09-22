#!/usr/bin/env bash
set -euo pipefail
VERSION="2.1.0"
TAG="v${VERSION}"
REPO_URL="${REPO_URL:-https://github.com/Content-Catalyst-LLC/catalystanalyticsr.git}"
REPO_DIR="${1:-/opt/sustainable-catalyst/catalystanalyticsr}"
WORKSPACE_R_CONTAINER="${WORKSPACE_R_CONTAINER:-sc-workspace-r-runtime}"
VENV="${TMPDIR:-/tmp}/catalyst-r-release-v210-venv"
log(){ printf '\n=== %s ===\n' "$*"; }
log "CATALYST ANALYTICS R ${VERSION} - CORE COMPUTATIONAL PROVIDER DEPLOY"
if [[ -d "${REPO_DIR}/.git" ]]; then git -C "${REPO_DIR}" fetch origin --tags --prune; else mkdir -p "$(dirname "${REPO_DIR}")"; git clone "${REPO_URL}" "${REPO_DIR}"; git -C "${REPO_DIR}" fetch origin --tags --prune; fi
git -C "${REPO_DIR}" checkout "${TAG}"
[[ "$(awk '/^Version:/ {print $2; exit}' "${REPO_DIR}/DESCRIPTION")" == "${VERSION}" ]] || { echo "DESCRIPTION version mismatch" >&2; exit 1; }
log "RELEASE CONTRACT"
rm -rf "${VENV}"; python3 -m venv "${VENV}"; "${VENV}/bin/python" -m pip -q install --upgrade pip; "${VENV}/bin/python" -m pip -q install jsonschema pytest
(cd "${REPO_DIR}" && PYTHONDONTWRITEBYTECODE=1 "${VENV}/bin/python" scripts/check_release.py)
rm -rf "${VENV}"
VERIFY='stopifnot(as.character(packageVersion("catalystanalyticsr")) == "2.1.0"); p <- catalystanalyticsr::catalyst_core_provider_manifest(); stopifnot(p$provider_key == "catalystanalyticsr", p$runtime == "r", p$execution_host == "workspace", identical(p$boundary$core_executes_provider, FALSE)); q <- catalystanalyticsr::core_analytical_request("deploy-check", "uncertainty_analysis", c("scenario:deploy")); e <- catalystanalyticsr::workspace_core_execution_envelope(q); stopifnot(e$boundary$workspace_controls_execution); cat("package=", as.character(packageVersion("catalystanalyticsr")), "\n", sep=""); cat("core_contract=", p$core_contract, "\n", sep=""); cat("execution_host=", p$execution_host, "\n", sep="")'
if command -v docker >/dev/null 2>&1 && docker inspect "${WORKSPACE_R_CONTAINER}" >/dev/null 2>&1; then
  log "INSTALLING INTO ${WORKSPACE_R_CONTAINER}"
  docker exec "${WORKSPACE_R_CONTAINER}" sh -lc 'rm -rf /tmp/catalystanalyticsr-v2.1.0 && mkdir -p /tmp/catalystanalyticsr-v2.1.0'
  tar -C "${REPO_DIR}" --exclude='.git' --exclude='.pytest_cache' --exclude='__pycache__' -cf - . | docker exec -i "${WORKSPACE_R_CONTAINER}" tar -C /tmp/catalystanalyticsr-v2.1.0 -xf -
  docker exec "${WORKSPACE_R_CONTAINER}" sh -lc 'R CMD INSTALL --preclean /tmp/catalystanalyticsr-v2.1.0'
  docker exec "${WORKSPACE_R_CONTAINER}" Rscript -e "${VERIFY}"
elif command -v R >/dev/null 2>&1 && command -v Rscript >/dev/null 2>&1; then
  log "WORKSPACE R CONTAINER NOT FOUND - INSTALLING INTO HOST R"
  R CMD INSTALL --preclean "${REPO_DIR}"
  Rscript -e "${VERIFY}"
else
  echo "Neither Docker container ${WORKSPACE_R_CONTAINER} nor host R is available." >&2; exit 2
fi
log "DEPLOY COMPLETE"
echo "Catalyst Analytics R ${VERSION} is installed as a Workspace-hosted Platform Core analytical provider."
echo "Platform Core itself does not execute R."
