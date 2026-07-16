#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY_VERSION = "0.1.4"
EXPECTED_PLUGIN_VERSION = "1.0.1"


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def version_from_description() -> str:
    match = re.search(r"^Version:\s*(\S+)$", read("DESCRIPTION"), re.MULTILINE)
    if not match:
        fail("DESCRIPTION Version not found")
    return match.group(1)


def version_from_plugin() -> str:
    match = re.search(r"^ \* Version:\s*(\S+)$", read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"), re.MULTILINE)
    if not match:
        fail("WordPress plugin Version not found")
    return match.group(1)


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    manifest = json.loads(read("catalyst_analytics_r_manifest.json"))
    if version_from_description() != EXPECTED_REPOSITORY_VERSION:
        fail("R package version mismatch")
    if version_from_plugin() != EXPECTED_PLUGIN_VERSION:
        fail("WordPress demo version mismatch")
    if manifest["repository_version"] != EXPECTED_REPOSITORY_VERSION:
        fail("Manifest repository version mismatch")
    if manifest["wordpress_demo"]["version"] != EXPECTED_PLUGIN_VERSION:
        fail("Manifest plugin version mismatch")

    r_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    if "CS50R" in r_source:
        fail("Course-specific language remains in R source")
    for path in sorted((ROOT / "R").glob("*.R")):
        raw = path.read_bytes()
        if any(byte > 127 for byte in raw):
            fail(f"Non-ASCII character remains in R source: {path.relative_to(ROOT)}")
    if r_source.count("theme_catalyst <- function") != 1:
        fail("theme_catalyst must have exactly one definition")

    tests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    if "multiplication works" in tests:
        fail("Placeholder tests remain")

    if (ROOT / "data/sample_scenarios.json").exists():
        fail("Raw JSON must live under inst/extdata, not data")

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests_py"])
    if subprocess.run(["bash", "-lc", "command -v node >/dev/null"], cwd=ROOT).returncode == 0:
        run(["node", "--check", "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js"])
    if subprocess.run(["bash", "-lc", "command -v php >/dev/null"], cwd=ROOT).returncode == 0:
        run(["php", "-l", "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"])

    print("Catalyst Analytics R v0.1.4 release contract passed.")
    print(f"Validated {len(json_files)} JSON files, JavaScript syntax, PHP syntax, and repository tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
