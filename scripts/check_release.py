#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.6.0."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY_VERSION = "0.6.0"
EXPECTED_PLUGIN_VERSION = "1.5.0"
EXPECTED_BROWSER_EXPORT_VERSION = "1.5.0"
EXPECTED_CONTRACTS = {
    "scenario": "1.0.0",
    "model_manifest": "1.0.0",
    "comparison": "1.0.0",
    "uncertainty": "1.0.0",
    "stress_test": "1.0.0",
    "dataset": "1.0.0",
    "indicator_registry": "1.0.0",
    "data_analysis": "1.0.0",
    "emissions_inventory": "1.0.0",
    "climate_accounting": "1.0.0",
    "natural_capital": "1.0.0",
    "boundary": "1.0.0",
    "browser_export": EXPECTED_BROWSER_EXPORT_VERSION,
}


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
    match = re.search(
        r"^ \* Version:\s*(\S+)$",
        read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"),
        re.MULTILINE,
    )
    if not match:
        fail("WordPress plugin Version not found")
    return match.group(1)


def run(command: list[str]) -> None:
    import os
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(command, cwd=ROOT, check=True, env=env)


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
    for name, version in EXPECTED_CONTRACTS.items():
        if manifest["contracts"][name]["version"] != version:
            fail(f"{name} contract version mismatch")

    required = [
        "R/emissions_inventory.R",
        "R/carbon_accounting.R",
        "R/natural_capital_accounting.R",
        "R/boundary_accounting.R",
        "R/climate_accounting.R",
        "R/export_climate_accounting.R",
        "man/emissions_inventory.Rd",
        "man/carbon_accounting.Rd",
        "man/natural_capital_accounting.Rd",
        "man/boundary_accounting.Rd",
        "man/climate_accounting.Rd",
        "man/export_climate_accounting.Rd",
        "schemas/catalyst_analytics_r_emissions_inventory.schema.json",
        "schemas/catalyst_analytics_r_climate_accounting.schema.json",
        "schemas/catalyst_analytics_r_natural_capital.schema.json",
        "schemas/catalyst_analytics_r_boundary.schema.json",
        "schemas/catalyst_analytics_r_climate_demo_export.schema.json",
        "examples/climate_accounting_input.json",
        "examples/boundary_definitions.json",
        "outputs/example_climate_accounting_export.json",
        "outputs/example_browser_climate_export.json",
        "inst/extdata/climate/sample_climate_accounting.csv",
        "inst/extdata/climate/sample_climate_accounting_source.json",
        "tests/fixtures/climate_accounting_contract_v1.json",
        "tests/testthat/helper-climate-accounting.R",
        "tests/testthat/test-emissions-inventory.R",
        "tests/testthat/test-carbon-accounting.R",
        "tests/testthat/test-natural-capital-accounting.R",
        "tests/testthat/test-boundary-accounting.R",
        "tests/testthat/test-climate-accounting-export.R",
        "docs/releases/v0.6.0.md",
        "docs/climate-carbon-natural-capital-accounting.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing v0.6.0 release files: {missing}")

    r_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    for path in sorted((ROOT / "R").glob("*.R")):
        try:
            path.read_bytes().decode("ascii")
        except UnicodeDecodeError as error:
            raise AssertionError(f"Non-ASCII character remains in R source: {path.relative_to(ROOT)}") from error
    for symbol in (
        "as_emissions_inventory <- function",
        "validate_emissions_inventory <- function",
        "carbon_budget_pathway <- function",
        "kaya_decomposition <- function",
        "natural_capital_account <- function",
        "natural_capital_from_dataset <- function",
        "boundary_definition <- function",
        "evaluate_boundaries <- function",
        "climate_accounting <- function",
        "export_climate_accounting <- function",
    ):
        if symbol not in r_source:
            fail(f"Missing v0.6.0 implementation symbol: {symbol}")
    for token in (
        "gross_emissions",
        "removals",
        "cumulative_net_emissions",
        "overshoot_time",
        "recovery_time",
        "carbon_lock_in_share",
        "stranded_pathway_signal",
        "additive_lmdi_kaya_identity",
        "reconciliation_error",
        "unit_mismatch",
    ):
        if token not in r_source:
            fail(f"Climate accounting implementation is incomplete: {token}")

    tests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    for expected in (
        "validate_emissions_inventory",
        "cumulative_net_emissions",
        "overshoot_time",
        "kaya_decomposition",
        "reconciliation_error",
        "evaluate_boundaries",
        "export_climate_accounting",
    ):
        if expected not in tests:
            fail(f"Climate accounting R tests are incomplete: {expected}")

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))

    inventory_validator = validator("schemas/catalyst_analytics_r_emissions_inventory.schema.json")
    natural_validator = validator("schemas/catalyst_analytics_r_natural_capital.schema.json")
    boundary_validator = validator("schemas/catalyst_analytics_r_boundary.schema.json")
    climate_validator = validator("schemas/catalyst_analytics_r_climate_accounting.schema.json")
    browser_validator = validator("schemas/catalyst_analytics_r_climate_demo_export.schema.json")
    climate_export = load_json("outputs/example_climate_accounting_export.json")
    climate_validator.validate(climate_export)
    inventory_validator.validate(climate_export["inventory"])
    natural_validator.validate(climate_export["natural_capital"])
    for boundary in load_json("examples/boundary_definitions.json"):
        boundary_validator.validate(boundary)
    browser_validator.validate(load_json("outputs/example_browser_climate_export.json"))
    if abs(climate_export["kaya"]["contributions"][0]["residual"]) > 1e-8:
        fail("Kaya fixture does not reconcile")
    if any(abs(row["reconciliation_error"]) > 1e-8 for row in climate_export["natural_capital"]["data"]):
        fail("Natural-capital fixture does not reconcile")

    # Preserve validation of prior public contracts.
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(load_json("examples/scenario_input.json"))
    validator("schemas/catalyst_analytics_r_comparison.schema.json").validate(load_json("outputs/example_comparison_export.json"))
    validator("schemas/catalyst_analytics_r_uncertainty.schema.json").validate(load_json("outputs/example_uncertainty_export.json"))
    validator("schemas/catalyst_analytics_r_dataset.schema.json").validate(load_json("examples/data_intake_input.json"))
    validator("schemas/catalyst_analytics_r_data_analysis.schema.json").validate(load_json("outputs/example_data_analysis_export.json"))
    validator("schemas/catalyst_analytics_r_data_demo_export.schema.json").validate(load_json("outputs/example_browser_data_export.json"))

    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    php = read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php")
    for expected in (
        "browser_climate_accounting",
        "mapped_contract_browser_calculation",
        "compatible_repository_version: '0.6.0'",
        "emissions_inventory_contract_version: '1.0.0'",
        "climate_accounting_contract_version: '1.0.0'",
        "natural_capital_contract_version: '1.0.0'",
        "boundary_contract_version: '1.0.0'",
        "cumulative_net_emissions",
        "kaya_decomposition",
        "natural_capital_account",
        "boundary_assessment",
    ):
        if expected not in js:
            fail(f"WordPress climate contract missing: {expected}")
    if "Climate, carbon, and natural-capital accounting" not in php or "Run governed accounting" not in php:
        fail("WordPress climate-accounting interface is missing")

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

    print("Catalyst Analytics R v0.6.0 release contract passed.")
    print(
        f"Validated {len(json_files)} JSON files, climate and natural-capital contracts, "
        "JavaScript syntax, PHP syntax, documentation aliases, and repository tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
