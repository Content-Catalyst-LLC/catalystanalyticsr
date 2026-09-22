#!/usr/bin/env bash
set -euo pipefail

VERSION="2.0.1"
TAG="v${VERSION}"
REPO_URL="${REPO_URL:-https://github.com/Content-Catalyst-LLC/catalystanalyticsr.git}"
REPO_DIR="${1:-/opt/sustainable-catalyst/catalystanalyticsr}"
WORKSPACE_R_CONTAINER="${WORKSPACE_R_CONTAINER:-sc-workspace-r-runtime}"

log(){ printf '\n=== %s ===\n' "$*"; }

log "CATALYST ANALYTICS R ${VERSION} — WORKSPACE R RUNTIME DEPLOY"

if [[ -d "${REPO_DIR}/.git" ]]; then
  log "UPDATING REPOSITORY"
  git -C "${REPO_DIR}" fetch origin --tags --prune
else
  log "CLONING REPOSITORY"
  mkdir -p "$(dirname "${REPO_DIR}")"
  git clone "${REPO_URL}" "${REPO_DIR}"
  git -C "${REPO_DIR}" fetch origin --tags --prune
fi

git -C "${REPO_DIR}" checkout "${TAG}"

ACTUAL_VERSION="$(awk '/^Version:/ {print $2; exit}' "${REPO_DIR}/DESCRIPTION")"
if [[ "${ACTUAL_VERSION}" != "${VERSION}" ]]; then
  echo "Expected DESCRIPTION ${VERSION}; found ${ACTUAL_VERSION}." >&2
  exit 1
fi

log "RELEASE CONTRACT"
(
  cd "${REPO_DIR}"
  PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_release.py
)

if command -v docker >/dev/null 2>&1 && docker inspect "${WORKSPACE_R_CONTAINER}" >/dev/null 2>&1; then
  log "INSTALLING INTO ${WORKSPACE_R_CONTAINER}"
  docker exec "${WORKSPACE_R_CONTAINER}" sh -lc 'rm -rf /tmp/catalystanalyticsr-v2.0.1 && mkdir -p /tmp/catalystanalyticsr-v2.0.1'
  tar -C "${REPO_DIR}" \
    --exclude='.git' --exclude='.pytest_cache' --exclude='__pycache__' \
    -cf - . | docker exec -i "${WORKSPACE_R_CONTAINER}" tar -C /tmp/catalystanalyticsr-v2.0.1 -xf -
  docker exec "${WORKSPACE_R_CONTAINER}" sh -lc 'R CMD INSTALL --preclean /tmp/catalystanalyticsr-v2.0.1'
  docker exec "${WORKSPACE_R_CONTAINER}" Rscript -e \
    'stopifnot(as.character(packageVersion("catalystanalyticsr")) == "2.0.1"); m <- catalystanalyticsr::catalyst_api_manifest(); stopifnot(m$package$version == "2.0.1"); cat("catalystanalyticsr", as.character(packageVersion("catalystanalyticsr")), "\n")'
  log "WORKSPACE R RUNTIME VERIFIED"
  docker exec "${WORKSPACE_R_CONTAINER}" Rscript -e \
    'cat("package=", as.character(packageVersion("catalystanalyticsr")), "\n", sep=""); cat("workspace_handoff_exported=", "workspace_handoff" %in% getNamespaceExports("catalystanalyticsr"), "\n", sep="")'
elif command -v R >/dev/null 2>&1 && command -v Rscript >/dev/null 2>&1; then
  log "WORKSPACE R CONTAINER NOT FOUND — INSTALLING INTO HOST R"
  R CMD INSTALL --preclean "${REPO_DIR}"
  Rscript -e \
    'stopifnot(as.character(packageVersion("catalystanalyticsr")) == "2.0.1"); cat("catalystanalyticsr", as.character(packageVersion("catalystanalyticsr")), "\n"); cat("workspace_handoff_exported=", "workspace_handoff" %in% getNamespaceExports("catalystanalyticsr"), "\n", sep="")'
else
  echo "Neither Docker container ${WORKSPACE_R_CONTAINER} nor a host R installation is available." >&2
  echo "Repository and release-contract verification passed, but runtime installation could not be performed." >&2
  exit 2
fi

log "DEPLOY COMPLETE"
echo "Catalyst Analytics R ${VERSION} is installed as a Workspace-hosted R analytical provider."
echo "No standalone HTTP transport service is created by this release."
