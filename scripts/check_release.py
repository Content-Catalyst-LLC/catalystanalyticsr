#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.2.0."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY_VERSION = "0.2.0"
EXPECTED_PLUGIN_VERSION = "1.1.0"
EXPECTED_SCENARIO_SCHEMA_VERSION = "1.0.0"
EXPECTED_MODEL_VERSION = "1.0.0"
EXPECTED_DEMO_EXPORT_VERSION = "1.1.0"


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
    match = re.search(
        r"^ \* Version:\s*(\S+)$",
        read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"),
        re.MULTILINE,
    )
    if not match:
        fail("WordPress plugin Version not found")
    return match.group(1)


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def check_documented_exports() -> None:
    namespace = read("NAMESPACE")
    exports = re.findall(r"^export\(([^)]+)\)$", namespace, re.MULTILINE)
    aliases = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "man").glob("*.Rd"))
    missing = [name for name in exports if f"\\alias{{{name}}}" not in aliases]
    if missing:
        fail(f"Exported functions missing Rd aliases: {missing}")


def main() -> int:
    manifest = json.loads(read("catalyst_analytics_r_manifest.json"))
    if version_from_description() != EXPECTED_REPOSITORY_VERSION:
        fail("R package version mismatch")
    if version_from_plugin() != EXPECTED_PLUGIN_VERSION:
        fail("WordPress demo version mismatch")
    if manifest["repository_version"] != EXPECTED_REPOSITORY_VERSION:
        fail("Manifest repository version mismatch")
    if manifest["r_package"]["version"] != EXPECTED_REPOSITORY_VERSION:
        fail("Manifest R package version mismatch")
    if manifest["wordpress_demo"]["version"] != EXPECTED_PLUGIN_VERSION:
        fail("Manifest plugin version mismatch")
    if manifest["wordpress_demo"]["compatible_repository_version"] != EXPECTED_REPOSITORY_VERSION:
        fail("WordPress compatibility version mismatch")
    if manifest["contracts"]["scenario"]["version"] != EXPECTED_SCENARIO_SCHEMA_VERSION:
        fail("Scenario contract version mismatch")
    if manifest["contracts"]["model_manifest"]["version"] != EXPECTED_MODEL_VERSION:
        fail("Model contract version mismatch")
    if manifest["contracts"]["browser_export"]["version"] != EXPECTED_DEMO_EXPORT_VERSION:
        fail("Browser export contract version mismatch")

    required = [
        "R/catalyst_model.R",
        "R/model_khncpa_registry.R",
        "R/catalyst_scenario.R",
        "R/scenario_migrations.R",
        "schemas/catalyst_analytics_r_scenario.schema.json",
        "schemas/catalyst_analytics_r_model_manifest.schema.json",
        "schemas/catalyst_analytics_r_browser_input.schema.json",
        "tests/fixtures/khncpa_reference_v1.json",
        "tests/fixtures/browser_contract_mapping_v1.json",
        "docs/releases/v0.2.0.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing v0.2.0 release files: {missing}")

    r_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    if "CS50R" in r_source:
        fail("Course-specific language remains in R source")
    for path in sorted((ROOT / "R").glob("*.R")):
        if any(byte > 127 for byte in path.read_bytes()):
            fail(f"Non-ASCII character remains in R source: {path.relative_to(ROOT)}")
    if r_source.count("theme_catalyst <- function") != 1:
        fail("theme_catalyst must have exactly one definition")
    for symbol in (
        ".catalyst_model_registry <- new.env",
        "catalyst_scenario <- function",
        "run_catalyst_scenario <- function",
        "migrate_catalyst_scenario <- function",
        "browser_scenario_to_catalyst <- function",
    ):
        if symbol not in r_source:
            fail(f"Missing v0.2.0 implementation symbol: {symbol}")

    tests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    if "multiplication works" in tests:
        fail("Placeholder tests remain")
    if "khncpa_reference_v1.json" not in tests:
        fail("Numerical reference fixture is not exercised by R tests")

    if (ROOT / "data/sample_scenarios.json").exists():
        fail("Raw JSON must live under inst/extdata, not data")

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    for expected in (
        "canonicalScenario(run.inputs, generatedAt)",
        "schema_version: '1.1.0'",
        "compatible_repository_version: '0.2.0'",
        "parity_status: 'mapped_contract'",
    ):
        if expected not in js:
            fail(f"WordPress demo contract missing: {expected}")

    check_documented_exports()
    run([sys.executable, "scripts/check_r_structure.py"])
    run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests_py"])
    if subprocess.run(["bash", "-lc", "command -v node >/dev/null"], cwd=ROOT).returncode == 0:
        run(["node", "--check", "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js"])
    if subprocess.run(["bash", "-lc", "command -v php >/dev/null"], cwd=ROOT).returncode == 0:
        run(["php", "-l", "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"])

    print("Catalyst Analytics R v0.2.0 release contract passed.")
    print(
        f"Validated {len(json_files)} JSON files, canonical scenario/model contracts, "
        "JavaScript syntax, PHP syntax, documentation aliases, and repository tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
