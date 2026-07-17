from pathlib import Path
import json
import math
import re

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def description_version() -> str:
    text = (ROOT / "DESCRIPTION").read_text(encoding="utf-8")
    match = re.search(r"^Version:\s*(\S+)$", text, re.MULTILINE)
    assert match
    return match.group(1)


def plugin_version() -> str:
    text = (ROOT / "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text(encoding="utf-8")
    match = re.search(r"^ \* Version:\s*(\S+)$", text, re.MULTILINE)
    assert match
    return match.group(1)


def validator(path: str):
    schema = load_json(path)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def test_release_manifest_versions_and_contracts_are_consistent():
    manifest = load_json("catalyst_analytics_r_manifest.json")
    assert manifest["repository"] == "catalystanalyticsr"
    assert manifest["repository_version"] == "0.6.0"
    assert manifest["r_package"]["version"] == description_version() == "0.6.0"
    assert manifest["wordpress_demo"]["version"] == plugin_version() == "1.5.0"
    assert manifest["wordpress_demo"]["compatible_repository_version"] == "0.6.0"
    assert manifest["wordpress_demo"]["shortcode"] == "[catalyst_analytics_r_demo]"
    assert manifest["contracts"]["scenario"]["version"] == "1.0.0"
    assert manifest["contracts"]["model_manifest"]["version"] == "1.0.0"
    assert manifest["contracts"]["browser_export"]["version"] == "1.5.0"
    assert manifest["contracts"]["dataset"]["version"] == "1.0.0"
    assert manifest["contracts"]["indicator_registry"]["version"] == "1.0.0"
    assert manifest["contracts"]["data_analysis"]["version"] == "1.0.0"


def test_canonical_scenario_examples_validate_against_schema():
    check = validator("schemas/catalyst_analytics_r_scenario.schema.json")
    check.validate(load_json("examples/scenario_input.json"))
    check.validate(load_json("inst/extdata/scenarios/canonical_baseline_v1.json"))
    for sample in load_json("inst/extdata/sample_scenarios.json"):
        check.validate(sample)


def test_browser_inputs_validate_against_compatibility_schema():
    check = validator("schemas/catalyst_analytics_r_browser_input.schema.json")
    check.validate(load_json("examples/browser_scenario_input.json"))
    check.validate(load_json("inst/extdata/scenarios/legacy_browser_input_v1.json"))
    for sample in load_json("inst/extdata/browser_sample_scenarios.json"):
        check.validate(sample)


def test_model_manifest_validates_against_schema():
    check = validator("schemas/catalyst_analytics_r_model_manifest.schema.json")
    manifest = load_json("inst/extdata/models/khncpa_model_manifest_v1.json")
    check.validate(manifest)
    assert manifest["id"] == "khncpa"
    assert manifest["version"] == "1.0.0"
    assert set(manifest["required_states"]) == {"K", "H", "N", "C", "P", "A"}


def test_browser_export_and_nested_canonical_scenarios_validate():
    export = load_json("outputs/example_browser_comparison_export.json")
    validator("schemas/catalyst_analytics_r_demo_export.schema.json").validate(export)
    scenario_validator = validator("schemas/catalyst_analytics_r_scenario.schema.json")
    assert len(export["canonical_scenarios"]) == 2
    for scenario in export["canonical_scenarios"]:
        scenario_validator.validate(scenario)
    assert export["engine"]["parity_status"] == "mapped_uncertainty_contract"
    assert export["comparison"]["baseline_id"] != export["comparison"]["policy_id"]


def test_browser_mapping_fixture_is_structurally_exact():
    fixture = load_json("tests/fixtures/browser_contract_mapping_v1.json")
    browser = fixture["browser_input"]
    expected = fixture["expected_canonical_scenario"]
    assert expected["id"] == "policy-pathway"
    assert expected["time"]["end"] == browser["years"]
    assert expected["initial_state"]["K"] == browser["initialCapital"]
    assert expected["initial_state"]["H"] == browser["initialHuman"]
    assert expected["initial_state"]["N"] == browser["initialNatural"]
    assert expected["policy"] == {
        "s": browser["savings"],
        "e": browser["humanInvestment"],
        "a": browser["adaptation"],
    }
    assert expected["parameters"] == {
        "emissions_intensity": browser["emissionsIntensity"],
        "regen": browser["restoration"],
    }
    assert expected["constraints"]["emissions_budget"] == browser["emissionsBudget"]
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(expected)


def test_numerical_reference_fixture_is_complete_and_finite():
    fixture = load_json("tests/fixtures/khncpa_reference_v1.json")
    assert fixture["model"] == {"id": "khncpa", "version": "1.0.0"}
    assert fixture["integration_method"] == "rk4"
    assert 0 < fixture["tolerance"] <= 1e-8
    checkpoints = fixture["checkpoints"]
    assert [row["t"] for row in checkpoints] == [0, 1, 2, 3, 4]
    required = {"K", "H", "N", "C", "P", "A", "gdp", "emissions", "ans"}
    for row in checkpoints:
        assert required.issubset(row)
        assert all(math.isfinite(row[name]) for name in required)


def test_r_contract_implements_registry_scenario_and_migrations():
    namespace = (ROOT / "NAMESPACE").read_text(encoding="utf-8")
    for name in (
        "catalyst_scenario", "run_catalyst_scenario", "scenario_to_json",
        "scenario_from_json", "migrate_catalyst_scenario", "new_catalyst_model",
        "register_catalyst_model", "get_catalyst_model", "list_catalyst_models",
    ):
        assert f"export({name})" in namespace
    scenario_source = (ROOT / "R/catalyst_scenario.R").read_text(encoding="utf-8")
    model_source = (ROOT / "R/catalyst_model.R").read_text(encoding="utf-8")
    migration_source = (ROOT / "R/scenario_migrations.R").read_text(encoding="utf-8")
    assert 'schema_version = .catalyst_scenario_schema_version()' in scenario_source
    assert '.catalyst_model_registry <- new.env' in model_source
    assert 'browser_scenario_to_catalyst' in migration_source
    assert '"0.1.0"' in migration_source and '"1.0.0"' in migration_source


def test_export_contract_preserves_scenario_and_model_provenance():
    text = (ROOT / "R/export_catalyst_bundle.R").read_text(encoding="utf-8")
    assert "results$kaya" not in text
    assert "results$params" not in text
    assert "meta$params" in text
    assert 'scenario_to_json(scenario, path = scenario_path' in text
    assert "scenario_fingerprint_value" in text
    assert "model_version" in text


def test_no_placeholder_tests_course_language_or_non_ascii_r_source_remain():
    test_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    assert "multiplication works" not in test_text
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    assert "CS50R" not in source_text
    for path in sorted((ROOT / "R").glob("*.R")):
        assert all(byte <= 127 for byte in path.read_bytes()), path


def test_theme_and_build_exclusion_contracts_remain_clean():
    text = (ROOT / "R/theme_catalyst.R").read_text(encoding="utf-8")
    assert text.count("theme_catalyst <- function") == 1
    entries = (ROOT / ".Rbuildignore").read_text(encoding="ascii")
    for expected in (r"^\.github$", r"^\.pytest_cache$", r"^wordpress$", r"^tests_py$"):
        assert expected in entries
    data_dir = ROOT / "data"
    assert not data_dir.exists() or not list(data_dir.glob("*.json"))


def test_demo_test_compares_values_without_erasing_scenario_identity():
    text = (ROOT / "tests/testthat/test-demo.R").read_text(encoding="utf-8")
    assert 'setdiff(names(passing$trajectory_wide), "scenario")' in text
    assert 'expect_identical(unique(passing$trajectory_wide$scenario), "demo_pass")' in text
    assert 'expect_identical(unique(failing$trajectory_wide$scenario), "demo_fail")' in text


def test_comparison_input_and_export_contracts_validate():
    validator("schemas/catalyst_analytics_r_comparison_input.schema.json").validate(
        load_json("examples/comparison_input.json")
    )
    export = load_json("outputs/example_comparison_export.json")
    validator("schemas/catalyst_analytics_r_comparison.schema.json").validate(export)
    scenario_validator = validator("schemas/catalyst_analytics_r_scenario.schema.json")
    for scenario in export["scenarios"]:
        scenario_validator.validate(scenario)
    assert export["baseline_id"] == "reference-baseline"
    assert export["pareto"]["front"]


def test_browser_comparison_input_contract_validates():
    validator("schemas/catalyst_analytics_r_browser_comparison_input.schema.json").validate(
        load_json("examples/browser_comparison_input.json")
    )


def test_r_comparative_engine_exports_are_present():
    namespace = (ROOT / "NAMESPACE").read_text(encoding="utf-8")
    for name in (
        "run_scenarios", "compare_scenarios", "scenario_deltas",
        "scenario_rankings", "scenario_scorecard", "pareto_diagnostics",
        "plot_scenario_comparison", "plot_scenario_tradeoffs",
        "export_scenario_comparison",
    ):
        assert f"export({name})" in namespace
    source = (ROOT / "R/comparative_scenarios.R").read_text(encoding="utf-8")
    assert ".build_deltas" in source
    assert ".build_rankings" in source
    assert ".build_pareto" in source
    assert "dominates_baseline" in source
    assert "baseline" in source and "counterfactual" in source


def test_wordpress_demo_performs_climate_and_natural_capital_accounting():
    php = (ROOT / "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text(encoding="utf-8")
    js = (ROOT / "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js").read_text(encoding="utf-8")
    assert "Climate, carbon, and natural-capital accounting" in php
    assert "Run governed accounting" in php and "Boundary assessment" in php
    assert "browser_climate_accounting" in js
    assert "mapped_contract_browser_calculation" in js
    assert "compatible_repository_version: '0.6.0'" in js
    assert "emissions_inventory_contract_version: '1.0.0'" in js
    assert "natural_capital_contract_version: '1.0.0'" in js
    assert "cumulative_net_emissions" in js and "kaya_decomposition" in js


def test_python_brief_supports_comparative_exports(tmp_path):
    import importlib.util
    path = ROOT / "python/catalyst_analytics_brief.py"
    spec = importlib.util.spec_from_file_location("catalyst_analytics_brief", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    text = module.brief(load_json("outputs/example_browser_comparison_export.json"))
    assert "# Catalyst Analytics R Comparative Brief" in text
    assert "Reference baseline" in text
    assert "Transition policy" in text
    assert "Metric deltas" in text


def test_uncertainty_and_stress_contracts_validate():
    scenario = load_json("examples/uncertainty_input.json")
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(scenario)
    wrapper = load_json("examples/uncertainty_analysis_input.json")
    validator("schemas/catalyst_analytics_r_uncertainty_input.schema.json").validate(wrapper)
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(wrapper["scenario"])
    export = load_json("outputs/example_uncertainty_export.json")
    validator("schemas/catalyst_analytics_r_uncertainty.schema.json").validate(export)
    validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(export["scenario"])
    stress = load_json("examples/stress_test_input.json")
    validator("schemas/catalyst_analytics_r_stress_test_input.schema.json").validate(stress)
    assert export["meta"]["sampling"] == "latin_hypercube"
    assert export["meta"]["failed"] == 0
    assert export["probabilities"]
    assert export["sensitivity"]


def test_r_uncertainty_engine_exports_are_present():
    namespace = (ROOT / "NAMESPACE").read_text(encoding="utf-8")
    for name in (
        "uncertainty_spec", "validate_uncertainty_spec", "sample_uncertainty",
        "run_uncertainty", "uncertainty_summary", "uncertainty_probabilities",
        "global_sensitivity", "local_sensitivity", "plot_uncertainty",
        "plot_tornado", "stress_shock", "stress_case", "run_stress_tests",
        "stress_test_summary", "plot_stress_test", "export_uncertainty_analysis",
        "export_stress_test",
    ):
        assert f"export({name})" in namespace
    source = (ROOT / "R/uncertainty_engine.R").read_text(encoding="utf-8")
    for token in (
        "monte_carlo", "latin_hypercube", "triangular", "failure_rate",
        "thresholds", "spearman", "stress_case", "multiply",
    ):
        assert token in source


def test_uncertainty_fixture_documents_reproducibility_invariants():
    fixture = load_json("tests/fixtures/uncertainty_contract_v1.json")
    assert fixture["seed"] == 42
    assert set(fixture["sampling_methods"]) == {"monte_carlo", "latin_hypercube"}
    assert set(fixture["supported_distributions"]) == {"fixed", "uniform", "normal", "lognormal", "triangular", "beta", "discrete"}
    assert fixture["invariants"]["same_seed_is_reproducible"] is True
    assert fixture["invariants"]["failed_runs_are_reported"] is True


def test_browser_uncertainty_export_validates_and_preserves_specs():
    export = load_json("outputs/example_browser_comparison_export.json")
    validator("schemas/catalyst_analytics_r_demo_export.schema.json").validate(export)
    assert export["engine"]["parity_status"] == "mapped_uncertainty_contract"
    assert export["uncertainty"]["sampling"] == "latin_hypercube"
    assert export["uncertainty"]["requested"] == 250
    assert len(export["canonical_scenarios"][1]["uncertainty"]) == 3


def test_python_brief_supports_uncertainty_exports():
    import importlib.util
    path = ROOT / "python/catalyst_analytics_brief.py"
    spec = importlib.util.spec_from_file_location("catalyst_analytics_brief_uncertainty", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    text = module.brief(load_json("outputs/example_uncertainty_export.json"))
    assert "# Catalyst Analytics R Uncertainty Brief" in text
    assert "Latin hypercube" in text or "latin_hypercube" in text
    assert "Uncertainty intervals" in text
    assert "Threshold probabilities" in text
    assert "Strongest sensitivity signals" in text


def test_dataset_indicator_and_data_analysis_contracts_validate():
    dataset = load_json("examples/data_intake_input.json")
    validator("schemas/catalyst_analytics_r_dataset.schema.json").validate(dataset)
    indicator_validator = validator("schemas/catalyst_analytics_r_indicator.schema.json")
    definitions = load_json("examples/indicator_registry_input.json")
    for definition in definitions:
        indicator_validator.validate(definition)
    export = load_json("outputs/example_data_analysis_export.json")
    validator("schemas/catalyst_analytics_r_data_analysis.schema.json").validate(export)
    validator("schemas/catalyst_analytics_r_dataset.schema.json").validate(export["dataset"])
    for definition in export["indicators"]:
        indicator_validator.validate(definition)
    assert export["dataset"]["quality"]["duplicate_keys"] == 0
    assert export["indicator_trace"]


def test_browser_data_export_validates_and_preserves_boundary():
    export = load_json("outputs/example_browser_data_export.json")
    validator("schemas/catalyst_analytics_r_data_demo_export.schema.json").validate(export)
    assert export["engine"]["parity_status"] == "mapped_data_indicator_contract"
    assert export["quality"]["row_count"] == 10
    assert export["indicator_result"]["indicator"]["formula"] == "emissions / gdp"
    assert export["boundary"]["source_verified"] is False
    assert export["boundary"]["unit_compatibility_verified"] is False


def test_r_data_and_indicator_exports_are_present():
    namespace = (ROOT / "NAMESPACE").read_text(encoding="utf-8")
    for name in (
        "dataset_source", "as_catalyst_dataset", "read_catalyst_data",
        "validate_catalyst_dataset", "dataset_fingerprint", "dataset_manifest",
        "data_quality_report", "register_unit_conversion", "convert_dataset_unit",
        "new_catalyst_indicator", "register_catalyst_indicator",
        "list_catalyst_indicators", "get_catalyst_indicator",
        "catalyst_indicator_manifest", "calculate_indicator",
        "calculate_indicators", "indicator_trace", "export_data_analysis",
    ):
        assert f"export({name})" in namespace
    data_source = (ROOT / "R/data_intake.R").read_text(encoding="utf-8")
    indicator_source = (ROOT / "R/indicator_registry.R").read_text(encoding="utf-8")
    export_source = (ROOT / "R/export_data_analysis.R").read_text(encoding="utf-8")
    for token in ("duplicate_keys", "missing_policy", "dataset_fingerprint", "unit_conversion"):
        assert token in data_source
    for token in ("required_fields", "formula", "indicator_version", "calculation"):
        assert token in indicator_source
    assert "indicator_trace" in export_source and "quality_flags" in export_source


def test_data_indicator_fixture_preserves_expected_values():
    fixture = load_json("tests/fixtures/data_indicator_contract_v1.json")
    assert fixture["expected"]["row_count"] == 10
    assert fixture["expected"]["regions"] == ["North", "South"]
    assert math.isclose(fixture["expected"]["carbon_intensity_2024_north"], 32 / 122, rel_tol=0, abs_tol=1e-8)
    assert math.isclose(fixture["expected"]["adjusted_net_savings_2024_north"], 23.5, rel_tol=0, abs_tol=1e-8)
    assert fixture["expected"]["cumulative_emissions_north"] == 190


def test_python_brief_supports_data_analysis_exports():
    import importlib.util
    path = ROOT / "python/catalyst_analytics_brief.py"
    spec = importlib.util.spec_from_file_location("catalyst_analytics_brief_data", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    text = module.brief(load_json("outputs/example_data_analysis_export.json"))
    assert "# Catalyst Analytics R Data and Indicator Brief" in text
    assert "Synthetic regional sustainability time series" in text
    assert "Indicator definitions" in text
    assert "Data-quality flags" in text


def test_climate_accounting_contracts_and_examples_validate():
    inventory_validator = validator("schemas/catalyst_analytics_r_emissions_inventory.schema.json")
    natural_validator = validator("schemas/catalyst_analytics_r_natural_capital.schema.json")
    boundary_validator = validator("schemas/catalyst_analytics_r_boundary.schema.json")
    climate_validator = validator("schemas/catalyst_analytics_r_climate_accounting.schema.json")
    browser_validator = validator("schemas/catalyst_analytics_r_climate_demo_export.schema.json")
    export = load_json("outputs/example_climate_accounting_export.json")
    climate_validator.validate(export)
    inventory_validator.validate(export["inventory"])
    natural_validator.validate(export["natural_capital"])
    for definition in load_json("examples/boundary_definitions.json"):
        boundary_validator.validate(definition)
    browser = load_json("outputs/example_browser_climate_export.json")
    browser_validator.validate(browser)
    assert export["carbon"]["diagnostics"][0]["overshoot_time"] == 2029
    assert export["carbon"]["diagnostics"][0]["stranded_pathway_signal"] is True
    assert abs(export["kaya"]["contributions"][0]["residual"]) < 1e-8
    assert all(abs(row["reconciliation_error"]) < 1e-8 for row in export["natural_capital"]["data"])


def test_r_climate_accounting_exports_are_present():
    namespace = (ROOT / "NAMESPACE").read_text(encoding="utf-8")
    for name in (
        "as_emissions_inventory", "validate_emissions_inventory",
        "emissions_inventory_manifest", "emissions_inventory_summary",
        "carbon_budget_pathway", "carbon_pathway_summary", "kaya_decomposition",
        "natural_capital_account", "natural_capital_from_dataset",
        "validate_natural_capital_account", "natural_capital_summary",
        "boundary_definition", "validate_boundary_definition",
        "evaluate_boundaries", "boundary_summary", "climate_accounting",
        "climate_accounting_summary", "export_climate_accounting",
    ):
        assert f"export({name})" in namespace
    sources = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in (
        "R/emissions_inventory.R", "R/carbon_accounting.R",
        "R/natural_capital_accounting.R", "R/boundary_accounting.R",
        "R/climate_accounting.R", "R/export_climate_accounting.R",
    ))
    for token in (
        "gross_emissions", "cumulative_net_emissions", "overshoot_time",
        "carbon_lock_in_share", "additive_lmdi_kaya_identity",
        "reconciliation_error", "unit_mismatch", "review_boundaries",
    ):
        assert token in sources


def test_climate_fixture_preserves_accounting_invariants():
    fixture = load_json("tests/fixtures/climate_accounting_contract_v1.json")
    inventory = fixture["inventory"]["data"]
    assert all(math.isclose(row["net_emissions"], row["gross_emissions"] - row["removals"], abs_tol=1e-10) for row in inventory)
    pathway = fixture["carbon"]["pathway"]
    assert math.isclose(pathway[-1]["cumulative_net_emissions"], 334.0, abs_tol=1e-10)
    assert math.isclose(pathway[-1]["remaining_budget"], -34.0, abs_tol=1e-10)
    natural = fixture["natural_capital"]["data"]
    assert all(math.isclose(row["closing_stock"], row["expected_closing_stock"], abs_tol=1e-10) for row in natural)


def test_python_brief_supports_climate_accounting_exports():
    import importlib.util
    path = ROOT / "python/catalyst_analytics_brief.py"
    spec = importlib.util.spec_from_file_location("catalyst_analytics_brief_climate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    package_text = module.brief(load_json("outputs/example_climate_accounting_export.json"))
    browser_text = module.brief(load_json("outputs/example_browser_climate_export.json"))
    for text in (package_text, browser_text):
        assert "# Catalyst Analytics R Climate Accounting Brief" in text
        assert "Carbon-budget diagnostics" in text
        assert "Kaya decomposition" in text
        assert "Natural-capital account" in text
        assert "Boundary assessment" in text
