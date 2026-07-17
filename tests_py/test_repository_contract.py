from __future__ import annotations
import importlib.util, json, math, re
from pathlib import Path
import jsonschema, pytest
ROOT = Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)

def test_description_version(): assert re.search(r"^Version: 0\.7\.0$", (ROOT/"DESCRIPTION").read_text(), re.M)
def test_manifest_version(): assert load("catalyst_analytics_r_manifest.json")["repository_version"] == "0.7.0"
def test_plugin_version(): assert " * Version: 1.6.0" in (ROOT/"wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text()
def test_manifest_compatibility(): assert load("catalyst_analytics_r_manifest.json")["wordpress_demo"]["compatible_repository_version"] == "0.7.0"
@pytest.mark.parametrize("contract", ["wealth","human_development","distribution","composite_score","inclusive_development"])
def test_new_contract_versions(contract): assert load("catalyst_analytics_r_manifest.json")["contracts"][contract]["version"] == "1.0.0"
def test_browser_contract_version(): assert load("catalyst_analytics_r_manifest.json")["contracts"]["browser_export"]["version"] == "1.6.0"

def test_inclusive_export_validates(): validator("schemas/catalyst_analytics_r_inclusive_development.schema.json").validate(load("outputs/example_inclusive_development_export.json"))
def test_wealth_validates(): validator("schemas/catalyst_analytics_r_wealth.schema.json").validate(load("outputs/example_inclusive_development_export.json")["wealth"])
def test_human_development_validates():
    p=load("outputs/example_inclusive_development_export.json"); validator("schemas/catalyst_analytics_r_human_development.schema.json").validate({"adjusted_net_savings":p["adjusted_net_savings"],"human_development":p["human_development"]})
def test_distribution_validates(): validator("schemas/catalyst_analytics_r_distribution.schema.json").validate(load("outputs/example_inclusive_development_export.json")["distribution"])
def test_composite_validates(): validator("schemas/catalyst_analytics_r_composite_score.schema.json").validate(load("outputs/example_inclusive_development_export.json")["composite"])
def test_browser_export_validates(): validator("schemas/catalyst_analytics_r_inclusive_demo_export.schema.json").validate(load("outputs/example_browser_inclusive_export.json"))

def test_capital_accounts_reconcile():
    p=load("outputs/example_inclusive_development_export.json")
    assert all(abs(row["reconciliation_error"]) <= 1e-8 for account in p["wealth"]["capital_accounts"].values() for row in account["data"])
def test_inclusive_wealth_adds_capitals():
    for row in load("outputs/example_inclusive_development_export.json")["wealth"]["data"]:
        assert math.isclose(row["inclusive_wealth"], row["produced_capital_value"]+row["human_capital_value"]+row["natural_capital_value"], rel_tol=0, abs_tol=1e-10)
def test_per_capita_wealth_is_traceable():
    for row in load("outputs/example_inclusive_development_export.json")["wealth"]["data"]:
        assert math.isclose(row["inclusive_wealth_per_capita"], row["inclusive_wealth"]/row["population"], rel_tol=0, abs_tol=1e-10)
def test_ans_decomposition_reconciles():
    for row in load("outputs/example_inclusive_development_export.json")["adjusted_net_savings"]:
        expected=row["gross_savings"]+row["education_investment"]+row["health_investment"]+row["other_adjustments"]-row["produced_capital_depreciation"]-row["natural_resource_depletion"]-row["pollution_damages"]-row["climate_damages"]
        assert math.isclose(row["adjusted_net_savings"],expected,abs_tol=1e-10)
def test_hdi_geometric_mean():
    for row in load("outputs/example_inclusive_development_export.json")["human_development"]:
        expected=(row["life_expectancy_index"]*row["education_index"]*row["income_index"])**(1/3)
        assert math.isclose(row["human_development_index"], expected, abs_tol=1e-10)
def test_distribution_ranges():
    s=load("outputs/example_inclusive_development_export.json")["distribution"]["summary"]
    assert 0 <= s["gini"] <= 1 and 0 <= s["share_below_social_floor"] <= 1
def test_group_shares_sum():
    rows=load("outputs/example_inclusive_development_export.json")["distribution"]["group_summary"]
    assert math.isclose(sum(x["resource_share"] for x in rows),1,abs_tol=1e-10)
    assert math.isclose(sum(x["population_share"] for x in rows),1,abs_tol=1e-10)
def test_intergenerational_signal(): assert load("outputs/example_inclusive_development_export.json")["intergenerational"]["summary"]["non_declining_signal"] is True
def test_composite_weights_sum(): assert math.isclose(sum(x["weight"] for x in load("outputs/example_inclusive_development_export.json")["composite"]["definition"]["components"]),1,abs_tol=1e-12)
def test_composite_contributions_reconcile():
    p=load("outputs/example_inclusive_development_export.json")["composite"]
    for score in p["scores"]:
        rid=p["scores"].index(score)+1
        assert math.isclose(score["composite_score"],sum(x["weighted_contribution"] for x in p["components"] if x["row_id"]==rid),abs_tol=1e-10)
def test_weight_sensitivity_present(): assert len(load("outputs/example_inclusive_development_export.json")["composite"]["sensitivity"]) == 8
def test_review_boundary_complete(): assert all(load("outputs/example_inclusive_development_export.json")["review_boundary"].values())
def test_fixture_summary_matches_output(): assert load("tests/fixtures/inclusive_development_contract_v1.json")["expected_summary"] == load("outputs/example_inclusive_development_export.json")["summary"][0]
def test_csv_fixture_exists(): assert (ROOT/"inst/extdata/inclusive/sample_inclusive_development.csv").read_text().count("\n") == 4
def test_source_fixture_has_license(): assert load("inst/extdata/inclusive/sample_inclusive_development_source.json")["license"] == "CC0-1.0"

def test_namespace_exports():
    text=(ROOT/"NAMESPACE").read_text()
    for name in ("capital_account","inclusive_wealth_account","adjusted_net_savings_decomposition","human_development_indicators","distributional_analysis","intergenerational_analysis","composite_score_definition","calculate_composite_score","composite_weight_sensitivity","inclusive_development_analysis","export_inclusive_development"):
        assert f"export({name})" in text
def test_s3_methods_registered():
    text=(ROOT/"NAMESPACE").read_text()
    for cls in ("catalyst_capital_account","catalyst_inclusive_wealth","catalyst_distribution_analysis","catalyst_intergenerational_analysis","catalyst_composite_definition","catalyst_composite_score","catalyst_inclusive_development"):
        assert f"S3method(print,{cls})" in text
def test_no_non_ascii_r_source():
    for path in (ROOT/"R").glob("*.R"): path.read_bytes().decode("ascii")
def test_no_placeholder_tests(): assert "multiplication works" not in "\n".join(p.read_text() for p in (ROOT/"tests/testthat").glob("*.R"))
def test_plugin_has_inclusive_interface():
    php=(ROOT/"wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text(); assert "Inclusive wealth, human development, and distribution" in php and "Run inclusive analysis" in php
def test_plugin_has_contract_tokens():
    js=(ROOT/"wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js").read_text()
    for token in ("browser_inclusive_development","mapped_inclusive_development_contract","adjusted_net_savings","human_development_index","share_below_social_floor","weight_sensitivity"): assert token in js
def test_python_brief_supports_inclusive_export():
    path=ROOT/"python/catalyst_analytics_brief.py"; spec=importlib.util.spec_from_file_location("brief",path); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    text=module.brief(load("outputs/example_inclusive_development_export.json")); assert "# Catalyst Analytics R Inclusive Development Brief" in text and "Composite score" in text
def test_prior_scenario_contract(): validator("schemas/catalyst_analytics_r_scenario.schema.json").validate(load("examples/scenario_input.json"))
def test_prior_comparison_contract(): validator("schemas/catalyst_analytics_r_comparison.schema.json").validate(load("outputs/example_comparison_export.json"))
def test_prior_uncertainty_contract(): validator("schemas/catalyst_analytics_r_uncertainty.schema.json").validate(load("outputs/example_uncertainty_export.json"))
def test_prior_data_contract(): validator("schemas/catalyst_analytics_r_data_analysis.schema.json").validate(load("outputs/example_data_analysis_export.json"))
def test_prior_climate_contract(): validator("schemas/catalyst_analytics_r_climate_accounting.schema.json").validate(load("outputs/example_climate_accounting_export.json"))
def test_manifest_fixtures_resolve():
    fixtures=load("catalyst_analytics_r_manifest.json")["fixtures"]
    assert all((ROOT/path).exists() for path in fixtures.values())
def test_release_docs_present(): assert "0.7.0" in (ROOT/"docs/releases/v0.7.0.md").read_text()
def test_package_description_mentions_distribution(): assert "distribution" in (ROOT/"DESCRIPTION").read_text().lower()
def test_buildignore_excludes_repository_layers():
    text=(ROOT/".Rbuildignore").read_text(); assert "^wordpress$" in text and "^tests_py$" in text and "^schemas$" in text
