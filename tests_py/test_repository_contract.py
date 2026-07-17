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
    assert manifest["repository_version"] == "0.3.0"
    assert manifest["r_package"]["version"] == description_version() == "0.3.0"
    assert manifest["wordpress_demo"]["version"] == plugin_version() == "1.2.0"
    assert manifest["wordpress_demo"]["compatible_repository_version"] == "0.3.0"
    assert manifest["wordpress_demo"]["shortcode"] == "[catalyst_analytics_r_demo]"
    assert manifest["contracts"]["scenario"]["version"] == "1.0.0"
    assert manifest["contracts"]["model_manifest"]["version"] == "1.0.0"
    assert manifest["contracts"]["browser_export"]["version"] == "1.2.0"


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
    assert export["engine"]["parity_status"] == "mapped_comparison_contract"
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


def test_wordpress_demo_performs_real_two_scenario_comparison():
    php = (ROOT / "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text(encoding="utf-8")
    js = (ROOT / "wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js").read_text(encoding="utf-8")
    assert "Compare a baseline with a policy pathway" in php
    assert "canonical_scenarios" in js
    assert "mapped_comparison_contract" in js
    assert "compatible_repository_version: '0.3.0'" in js
    assert "comparison_contract_version: '1.0.0'" in js
    assert "baseline_non_dominated" in js and "policy_non_dominated" in js


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
