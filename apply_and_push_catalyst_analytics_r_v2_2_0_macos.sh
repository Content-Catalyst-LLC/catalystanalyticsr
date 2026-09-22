#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-$HOME/Downloads/catalystanalyticsr}"
PATCH_ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "=== SYNCHRONIZING MAIN ==="
cd "$TARGET"
git checkout main
git pull --ff-only origin main
if git rev-parse v2.2.0 >/dev/null 2>&1; then echo "STOP: tag v2.2.0 already exists." >&2; exit 1; fi
echo "=== APPLYING v2.2.0 PATCH ==="
rm -f "$TARGET/apply_and_push_catalyst_analytics_r_v2_1_0_macos.sh" "$TARGET/CATALYST_ANALYTICS_R_V210_TERMINAL_COMMANDS.txt"
rsync -a --exclude='.git/' --exclude='.pytest_cache/' --exclude='__pycache__/' "$PATCH_ROOT/" "$TARGET/"
rm -rf /tmp/catalyst-r-v220-release-venv
python3 -m venv /tmp/catalyst-r-v220-release-venv
/tmp/catalyst-r-v220-release-venv/bin/pip -q install jsonschema pytest
PYTHONDONTWRITEBYTECODE=1 /tmp/catalyst-r-v220-release-venv/bin/python scripts/check_release.py
rm -rf /tmp/catalyst-r-v220-release-venv
git add -A
git commit -m "Catalyst Analytics R v2.2.0 - Statistical Diagnostics & Validation Contract"
git push origin main
git tag -a v2.2.0 -m "Catalyst Analytics R v2.2.0 - Statistical Diagnostics & Validation Contract"
git push origin v2.2.0
echo "=== COMPLETE ==="
git --no-pager log -1 --oneline
git tag --points-at HEAD
test -z "$(git status --short)"
