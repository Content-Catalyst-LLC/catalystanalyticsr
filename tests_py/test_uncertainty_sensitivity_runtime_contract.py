import json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
def test_manifest_contract_and_versions():
    m=load("catalyst_analytics_r_manifest.json")
    assert m["repository_version"]=="2.3.0" and m["schema_version"]=="3.3.0"
    c=m["contracts"]["uncertainty_sensitivity_runtime"]
    assert c["contract"]=="sc.analytics-r.uncertainty-sensitivity-runtime.v1"
    assert c["core_minimum_release"]=="3.3.0" and c["workspace_validated_release"]=="3.9.1"
def test_runtime_source_has_bounded_methods_and_boundaries():
    s=(ROOT/"R/uncertainty_sensitivity_runtime.R").read_text()
    for token in ["monte_carlo", "latin_hypercube", "morris_sensitivity", "sobol_sensitivity", "maximum_structured_evaluations = 20000L", "arbitrary_function_dispatch = FALSE", "sensitivity_does_not_establish_causality = TRUE", "human_review_required = TRUE"]:
        assert token in s
def test_provider_promotes_registered_methods_only():
    s=(ROOT/"R/core_computational_provider.R").read_text()
    assert 'uncertainty_sensitivity_contract = "sc.analytics-r.uncertainty-sensitivity-runtime.v1"' in s
    assert 'run_uncertainty_sensitivity_runtime' in s and 'morris_sensitivity' in s and 'sobol_sensitivity' in s
    p=load("examples/core_provider_manifest.json")
    assert p["provider_version"]=="2.3.0" and p["uncertainty_sensitivity_contract"]=="sc.analytics-r.uncertainty-sensitivity-runtime.v1"
def test_example_validates_schema():
    import jsonschema
    schema=load("schemas/catalyst_analytics_r_uncertainty_sensitivity_runtime.schema.json")
    jsonschema.Draft202012Validator(schema).validate(load("examples/uncertainty_sensitivity_runtime.json"))
def test_wordpress_maps_contract_without_r_execution():
    php=(ROOT/"wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text()
    js=(ROOT/"wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js").read_text()
    assert "Catalyst Analytics R v2.3.0" in php and "Uncertainty runtime v1" in php
    assert "uncertainty_sensitivity_contract:'sc.analytics-r.uncertainty-sensitivity-runtime.v1'" in js
    assert "core_executes_provider:false" in js
