#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.4.0."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY_VERSION = "0.4.0"
EXPECTED_PLUGIN_VERSION = "1.3.0"
EXPECTED_SCENARIO_SCHEMA_VERSION = "1.0.0"
EXPECTED_MODEL_VERSION = "1.0.0"
EXPECTED_COMPARISON_VERSION = "1.0.0"
EXPECTED_UNCERTAINTY_VERSION = "1.0.0"
EXPECTED_DEMO_EXPORT_VERSION = "1.3.0"


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str):
    return json.loads(read(path))


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


def validate(schema_path: str, document_path: str) -> None:
    schema = load_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(load_json(document_path))


def check_documented_exports() -> None:
    namespace = read("NAMESPACE")
    exports = re.findall(r"^export\(([^)]+)\)$", namespace, re.MULTILINE)
    aliases = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "man").glob("*.Rd"))
    missing = [name for name in exports if f"\\alias{{{name}}}" not in aliases]
    if missing:
        fail(f"Exported functions missing Rd aliases: {missing}")


def main() -> int:
    manifest = load_json("catalyst_analytics_r_manifest.json")
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
    if manifest["contracts"]["comparison"]["version"] != EXPECTED_COMPARISON_VERSION:
        fail("Comparison contract version mismatch")
    if manifest["contracts"]["uncertainty"]["version"] != EXPECTED_UNCERTAINTY_VERSION:
        fail("Uncertainty contract version mismatch")
    if manifest["contracts"]["browser_export"]["version"] != EXPECTED_DEMO_EXPORT_VERSION:
        fail("Browser export contract version mismatch")

    required = [
        "R/uncertainty_engine.R",
        "R/export_uncertainty_analysis.R",
        "schemas/catalyst_analytics_r_uncertainty.schema.json",
        "schemas/catalyst_analytics_r_uncertainty_input.schema.json",
        "schemas/catalyst_analytics_r_stress_test_input.schema.json",
        "examples/uncertainty_input.json",
        "examples/uncertainty_analysis_input.json",
        "examples/stress_test_input.json",
        "outputs/example_uncertainty_export.json",
        "tests/fixtures/uncertainty_contract_v1.json",
        "tests/testthat/test-uncertainty-engine.R",
        "tests/testthat/test-uncertainty-export.R",
        "docs/releases/v0.4.0.md",
        "docs/uncertainty-sensitivity-stress-testing.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing v0.4.0 release files: {missing}")

    r_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    for path in sorted((ROOT / "R").glob("*.R")):
        if any(byte > 127 for byte in path.read_bytes()):
            fail(f"Non-ASCII character remains in R source: {path.relative_to(ROOT)}")
    for symbol in (
        "uncertainty_spec <- function",
        "sample_uncertainty <- function",
        "run_uncertainty <- function",
        "global_sensitivity <- function",
        "local_sensitivity <- function",
        "stress_case <- function",
        "run_stress_tests <- function",
        "export_uncertainty_analysis <- function",
    ):
        if symbol not in r_source:
            fail(f"Missing v0.4.0 implementation symbol: {symbol}")

    tests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    for expected in ("latin_hypercube", "run_uncertainty", "run_stress_tests", "failure"):
        if expected not in tests:
            fail(f"Uncertainty R tests are incomplete: {expected}")

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    validate("schemas/catalyst_analytics_r_scenario.schema.json", "examples/uncertainty_input.json")
    validate("schemas/catalyst_analytics_r_uncertainty_input.schema.json", "examples/uncertainty_analysis_input.json")
    validate("schemas/catalyst_analytics_r_uncertainty.schema.json", "outputs/example_uncertainty_export.json")
    validate("schemas/catalyst_analytics_r_stress_test_input.schema.json", "examples/stress_test_input.json")
    validate("schemas/catalyst_analytics_r_demo_export.schema.json", "outputs/example_browser_comparison_export.json")

    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    php = read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php")
    for expected in (
        "mapped_uncertainty_contract",
        "compatible_repository_version: '0.4.0'",
        "uncertainty_contract_version: '1.0.0'",
        "latin_hypercube",
        "monte_carlo",
        "budget_probability",
        "canonical_scenarios",
    ):
        if expected not in js:
            fail(f"WordPress uncertainty contract missing: {expected}")
    if "Compare pathways under declared uncertainty" not in php:
        fail("WordPress uncertainty interface is missing")

    check_documented_exports()
    run([sys.executable, "scripts/check_r_structure.py"])
    run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests_py"])
    if subprocess.run(["bash", "-lc", "command -v node >/dev/null"], cwd=ROOT).returncode == 0:
        run(["node", "--check", "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js"])
    if subprocess.run(["bash", "-lc", "command -v php >/dev/null"], cwd=ROOT).returncode == 0:
        run(["php", "-l", "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"])

    print("Catalyst Analytics R v0.4.0 release contract passed.")
    print(
        f"Validated {len(json_files)} JSON files, uncertainty and stress-test contracts, "
        "JavaScript syntax, PHP syntax, documentation aliases, and repository tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
