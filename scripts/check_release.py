#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.5.0."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY_VERSION = "0.5.0"
EXPECTED_PLUGIN_VERSION = "1.4.0"
EXPECTED_SCENARIO_VERSION = "1.0.0"
EXPECTED_MODEL_VERSION = "1.0.0"
EXPECTED_COMPARISON_VERSION = "1.0.0"
EXPECTED_UNCERTAINTY_VERSION = "1.0.0"
EXPECTED_DATASET_VERSION = "1.0.0"
EXPECTED_INDICATOR_VERSION = "1.0.0"
EXPECTED_DATA_ANALYSIS_VERSION = "1.0.0"
EXPECTED_BROWSER_EXPORT_VERSION = "1.4.0"


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


def validator(path: str):
    schema = load_json(path)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


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
    expected_contracts = {
        "scenario": EXPECTED_SCENARIO_VERSION,
        "model_manifest": EXPECTED_MODEL_VERSION,
        "comparison": EXPECTED_COMPARISON_VERSION,
        "uncertainty": EXPECTED_UNCERTAINTY_VERSION,
        "dataset": EXPECTED_DATASET_VERSION,
        "indicator_registry": EXPECTED_INDICATOR_VERSION,
        "data_analysis": EXPECTED_DATA_ANALYSIS_VERSION,
        "browser_export": EXPECTED_BROWSER_EXPORT_VERSION,
    }
    for name, version in expected_contracts.items():
        if manifest["contracts"][name]["version"] != version:
            fail(f"{name} contract version mismatch")

    required = [
        "R/data_intake.R",
        "R/indicator_registry.R",
        "R/export_data_analysis.R",
        "schemas/catalyst_analytics_r_dataset.schema.json",
        "schemas/catalyst_analytics_r_indicator.schema.json",
        "schemas/catalyst_analytics_r_data_analysis.schema.json",
        "schemas/catalyst_analytics_r_data_demo_export.schema.json",
        "examples/data_intake_input.json",
        "examples/indicator_registry_input.json",
        "outputs/example_data_analysis_export.json",
        "outputs/example_browser_data_export.json",
        "inst/extdata/data/sample_country_timeseries.csv",
        "inst/extdata/data/sample_country_timeseries.json",
        "inst/extdata/data/sample_country_timeseries_source.json",
        "tests/fixtures/data_indicator_contract_v1.json",
        "tests/testthat/test-data-intake.R",
        "tests/testthat/test-indicator-registry.R",
        "tests/testthat/test-data-analysis-export.R",
        "docs/releases/v0.5.0.md",
        "docs/data-intake-and-indicator-registry.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing v0.5.0 release files: {missing}")

    r_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    for path in sorted((ROOT / "R").glob("*.R")):
        try:
            path.read_bytes().decode("ascii")
        except UnicodeDecodeError as error:
            raise AssertionError(f"Non-ASCII character remains in R source: {path.relative_to(ROOT)}") from error
    for symbol in (
        "dataset_source <- function",
        "as_catalyst_dataset <- function",
        "read_catalyst_data <- function",
        "dataset_fingerprint <- function",
        "register_unit_conversion <- function",
        "new_catalyst_indicator <- function",
        "register_catalyst_indicator <- function",
        "calculate_indicator <- function",
        "calculate_indicators <- function",
        "export_data_analysis <- function",
    ):
        if symbol not in r_source:
            fail(f"Missing v0.5.0 implementation symbol: {symbol}")

    tests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    for expected in ("read_catalyst_data", "duplicate_keys", "carbon_intensity", "cumulative_emissions", "indicator_trace", "export_data_analysis"):
        if expected not in tests:
            fail(f"Data and indicator R tests are incomplete: {expected}")

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    dataset_check = validator("schemas/catalyst_analytics_r_dataset.schema.json")
    indicator_check = validator("schemas/catalyst_analytics_r_indicator.schema.json")
    data_analysis_check = validator("schemas/catalyst_analytics_r_data_analysis.schema.json")
    browser_data_check = validator("schemas/catalyst_analytics_r_data_demo_export.schema.json")
    dataset_check.validate(load_json("examples/data_intake_input.json"))
    for definition in load_json("examples/indicator_registry_input.json"):
        indicator_check.validate(definition)
    data_export = load_json("outputs/example_data_analysis_export.json")
    data_analysis_check.validate(data_export)
    dataset_check.validate(data_export["dataset"])
    for definition in data_export["indicators"]:
        indicator_check.validate(definition)
    browser_data_check.validate(load_json("outputs/example_browser_data_export.json"))

    # Preserve validation of prior public contracts.
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(load_json("examples/scenario_input.json"))
    validator("schemas/catalyst_analytics_r_comparison.schema.json").validate(load_json("outputs/example_comparison_export.json"))
    validator("schemas/catalyst_analytics_r_uncertainty.schema.json").validate(load_json("outputs/example_uncertainty_export.json"))
    validator("schemas/catalyst_analytics_r_demo_export.schema.json").validate(load_json("outputs/example_browser_comparison_export.json"))

    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    php = read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php")
    for expected in (
        "browser_data_intake",
        "mapped_data_indicator_contract",
        "compatible_repository_version: '0.5.0'",
        "dataset_contract_version: '1.0.0'",
        "indicator_contract_version: '1.0.0'",
        "duplicate_keys",
        "required_fields",
        "indicator_registry",
    ):
        if expected not in js:
            fail(f"WordPress data contract missing: {expected}")
    if "Validate data and calculate governed indicators" not in php:
        fail("WordPress data-intake interface is missing")

    check_documented_exports()
    run([sys.executable, "scripts/check_r_structure.py"])
    run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests_py"])
    if subprocess.run(["bash", "-lc", "command -v node >/dev/null"], cwd=ROOT).returncode == 0:
        run(["node", "--check", "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js"])
    if subprocess.run(["bash", "-lc", "command -v php >/dev/null"], cwd=ROOT).returncode == 0:
        run(["php", "-l", "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"])

    debris = [
        path for path in ROOT.rglob("*")
        if path.name in {".pytest_cache", "__pycache__"} or path.name.endswith(".Rcheck")
    ]
    if debris:
        fail(f"Generated cache or check debris remains: {[str(path.relative_to(ROOT)) for path in debris]}")

    print("Catalyst Analytics R v0.5.0 release contract passed.")
    print(
        f"Validated {len(json_files)} JSON files, dataset and indicator contracts, "
        "JavaScript syntax, PHP syntax, documentation aliases, and repository tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
