#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.7.0."""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_VERSION = "0.7.0"
PLUGIN_VERSION = "1.6.0"
BROWSER_VERSION = "1.6.0"
NEW_CONTRACTS = ("wealth", "human_development", "distribution", "composite_score", "inclusive_development")

def fail(message: str) -> None: raise AssertionError(message)
def read(path: str) -> str: return (ROOT / path).read_text(encoding="utf-8")
def load(path: str): return json.loads(read(path))
def validator(path: str):
    schema = load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command: list[str]) -> None:
    env = dict(os.environ); env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(command, cwd=ROOT, check=True, env=env)

def documented_exports() -> None:
    exports = re.findall(r"^export\(([^)]+)\)$", read("NAMESPACE"), re.MULTILINE)
    aliases = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "man").glob("*.Rd"))
    missing = [name for name in exports if f"\\alias{{{name}}}" not in aliases]
    if missing: fail(f"Exported functions missing Rd aliases: {missing}")

def main() -> int:
    description = read("DESCRIPTION")
    match = re.search(r"^Version:\s*(\S+)$", description, re.MULTILINE)
    if not match or match.group(1) != REPOSITORY_VERSION: fail("DESCRIPTION version mismatch")
    manifest = load("catalyst_analytics_r_manifest.json")
    if manifest["schema_version"] != "1.6.0": fail("Manifest schema version mismatch")
    if manifest["repository_version"] != REPOSITORY_VERSION or manifest["r_package"]["version"] != REPOSITORY_VERSION: fail("Repository version mismatch")
    if manifest["wordpress_demo"]["version"] != PLUGIN_VERSION or manifest["wordpress_demo"]["compatible_repository_version"] != REPOSITORY_VERSION: fail("WordPress compatibility mismatch")
    if manifest["contracts"]["browser_export"]["version"] != BROWSER_VERSION: fail("Browser export version mismatch")
    for name in NEW_CONTRACTS:
        if manifest["contracts"][name]["version"] != "1.0.0": fail(f"{name} contract mismatch")

    required = [
        "R/inclusive_wealth.R", "R/human_development_distribution.R", "R/composite_scores.R",
        "R/inclusive_development.R", "R/export_inclusive_development.R",
        "man/inclusive_wealth.Rd", "man/human_development.Rd", "man/distribution_analysis.Rd",
        "man/composite_scores.Rd", "man/inclusive_development.Rd", "man/export_inclusive_development.Rd",
        "schemas/catalyst_analytics_r_wealth.schema.json", "schemas/catalyst_analytics_r_human_development.schema.json",
        "schemas/catalyst_analytics_r_distribution.schema.json", "schemas/catalyst_analytics_r_composite_score.schema.json",
        "schemas/catalyst_analytics_r_inclusive_development.schema.json", "schemas/catalyst_analytics_r_inclusive_demo_export.schema.json",
        "examples/inclusive_development_input.json", "examples/composite_score_definition.json",
        "outputs/example_inclusive_development_export.json", "outputs/example_browser_inclusive_export.json",
        "inst/extdata/inclusive/sample_inclusive_development.csv", "inst/extdata/inclusive/sample_inclusive_development_source.json",
        "tests/fixtures/inclusive_development_contract_v1.json", "tests/testthat/helper-inclusive-development.R",
        "tests/testthat/test-inclusive-wealth.R", "tests/testthat/test-human-development-distribution.R",
        "tests/testthat/test-composite-scores.R", "tests/testthat/test-inclusive-development-export.R",
        "docs/releases/v0.7.0.md", "docs/inclusive-wealth-human-development-distribution.md",
        "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php",
        "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing: fail(f"Missing v0.7.0 release files: {missing}")

    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    symbols = (
        "capital_account <- function", "validate_capital_account <- function", "inclusive_wealth_account <- function",
        "adjusted_net_savings_decomposition <- function", "human_development_indicators <- function",
        "distributional_analysis <- function", "intergenerational_analysis <- function",
        "composite_score_definition <- function", "calculate_composite_score <- function",
        "composite_weight_sensitivity <- function", "inclusive_development_analysis <- function",
        "export_inclusive_development <- function",
    )
    for symbol in symbols:
        if symbol not in source: fail(f"Missing implementation symbol: {symbol}")
    for token in ("reconciliation_error", "shadow_price", "inclusive_wealth_per_capita", "adjusted_net_savings_percent_gni", "human_development_index", "share_below_social_floor", "palma_ratio", "non_declining_signal", "weighted_contribution", "weight_sensitivity"):
        if token not in source: fail(f"Inclusive-development implementation incomplete: {token}")
    for path in sorted((ROOT / "R").glob("*.R")):
        try: path.read_bytes().decode("ascii")
        except UnicodeDecodeError as exc: raise AssertionError(f"Non-ASCII R source: {path.relative_to(ROOT)}") from exc

    json_files = sorted(ROOT.rglob("*.json"))
    for path in json_files: json.loads(path.read_text(encoding="utf-8"))
    wealth = load("outputs/example_inclusive_development_export.json")
    validator("schemas/catalyst_analytics_r_inclusive_development.schema.json").validate(wealth)
    validator("schemas/catalyst_analytics_r_wealth.schema.json").validate(wealth["wealth"])
    validator("schemas/catalyst_analytics_r_human_development.schema.json").validate({"adjusted_net_savings": wealth["adjusted_net_savings"], "human_development": wealth["human_development"]})
    validator("schemas/catalyst_analytics_r_distribution.schema.json").validate(wealth["distribution"])
    validator("schemas/catalyst_analytics_r_composite_score.schema.json").validate(wealth["composite"])
    validator("schemas/catalyst_analytics_r_inclusive_demo_export.schema.json").validate(load("outputs/example_browser_inclusive_export.json"))
    fixture = load("tests/fixtures/inclusive_development_contract_v1.json")
    if abs(fixture["composite_weight_sum"] - 1) > 1e-12: fail("Composite fixture weights do not sum to one")
    for account in wealth["wealth"]["capital_accounts"].values():
        if any(abs(row["reconciliation_error"]) > fixture["capital_reconciliation_tolerance"] for row in account["data"]): fail("Capital fixture does not reconcile")
    if abs(sum(row["weight"] for row in wealth["composite"]["definition"]["components"]) - 1) > 1e-12: fail("Composite definition does not sum to one")

    # Preserve prior public contracts.
    prior = [
        ("schemas/catalyst_analytics_r_scenario.schema.json", "examples/scenario_input.json"),
        ("schemas/catalyst_analytics_r_comparison.schema.json", "outputs/example_comparison_export.json"),
        ("schemas/catalyst_analytics_r_uncertainty.schema.json", "outputs/example_uncertainty_export.json"),
        ("schemas/catalyst_analytics_r_dataset.schema.json", "examples/data_intake_input.json"),
        ("schemas/catalyst_analytics_r_data_analysis.schema.json", "outputs/example_data_analysis_export.json"),
        ("schemas/catalyst_analytics_r_climate_accounting.schema.json", "outputs/example_climate_accounting_export.json"),
        ("schemas/catalyst_analytics_r_climate_demo_export.schema.json", "outputs/example_browser_climate_export.json"),
    ]
    for schema, payload in prior: validator(schema).validate(load(payload))

    php = read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php")
    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    if not re.search(r"^ \* Version:\s*1\.6\.0$", php, re.MULTILINE): fail("Plugin version mismatch")
    for token in ("Inclusive wealth, human development, and distribution", "Run inclusive analysis"):
        if token not in php: fail(f"WordPress interface missing: {token}")
    for token in ("browser_inclusive_development", "mapped_inclusive_development_contract", "compatible_repository_version: '0.7.0'", "wealth_contract_version: '1.0.0'", "adjusted_net_savings", "human_development_index", "share_below_social_floor", "weight_sensitivity"):
        if token not in js: fail(f"WordPress contract missing: {token}")

    documented_exports()
    run([sys.executable, "scripts/check_r_structure.py"])
    run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests_py"])
    if subprocess.run(["bash", "-lc", "command -v node >/dev/null"], cwd=ROOT).returncode == 0: run(["node", "--check", "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js"])
    if subprocess.run(["bash", "-lc", "command -v php >/dev/null"], cwd=ROOT).returncode == 0: run(["php", "-l", "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php"])
    debris = [path for path in ROOT.rglob("*") if path.name in {".pytest_cache", "__pycache__"} or path.name.endswith(".Rcheck")]
    if debris: fail(f"Generated debris remains: {[str(path.relative_to(ROOT)) for path in debris]}")
    print("Catalyst Analytics R v0.7.0 release contract passed.")
    print(f"Validated {len(json_files)} JSON files, inclusive-development contracts, JavaScript, PHP, documentation aliases, and repository tests.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
