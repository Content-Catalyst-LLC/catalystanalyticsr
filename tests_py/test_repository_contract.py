import json, re, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def validator(path): return jsonschema.Draft202012Validator(load(path))

def test_versions_and_manifest():
    text=(ROOT/'DESCRIPTION').read_text(); assert re.search(r'^Version:\s*1\.5\.0$',text,re.M)
    m=load('catalyst_analytics_r_manifest.json'); assert m['schema_version']=='2.5.0'; assert m['repository_version']=='1.5.0'; assert m['r_package']['version']=='1.5.0'; assert m['wordpress_demo']['version']=='2.5.0'; assert m['wordpress_demo']['compatible_repository_version']=='1.5.0'
    for contract in ('econometric_evaluation','policy_evaluation','policy_evaluation_export'): assert m['contracts'][contract]['version']=='1.0.0'

def test_policy_evaluation_contracts_validate():
    validator('schemas/catalyst_analytics_r_policy_evaluation.schema.json').validate(load('outputs/example_policy_evaluation_export.json'))
    validator('schemas/catalyst_analytics_r_policy_evaluation_demo_export.schema.json').validate(load('outputs/example_browser_policy_evaluation_export.json'))
    fixture=load('tests/fixtures/econometrics_policy_evaluation_contract_v1.json'); assert fixture['repository_version']=='1.5.0'; assert 'difference_in_differences' in fixture['methods']['quasi_experimental']

def test_r_apis_and_docs_exist():
    namespace=(ROOT/'NAMESPACE').read_text(); docs=(ROOT/'man/econometrics_policy_evaluation.Rd').read_text()+(ROOT/'man/export_policy_evaluation.Rd').read_text()+(ROOT/'man/workspace_policy_evaluations.Rd').read_text(); source=(ROOT/'R/econometrics_policy_evaluation.R').read_text()
    apis=['causal_assumption','regression_spec','validate_regression_spec','fit_policy_regression','panel_regression','regression_diagnostics','difference_in_differences','event_study','interrupted_time_series','synthetic_control','policy_effect_summary','policy_evaluation_analysis','policy_evaluation_summary','plot_policy_effects','plot_event_study','plot_synthetic_control','export_policy_evaluation','workspace_add_policy_evaluation','workspace_get_policy_evaluation']
    for api in apis: assert f'export({api})' in namespace; assert f'\\alias{{{api}}}' in docs
    for token in ['causal_claim_requires_design_specific_assumptions','automated_policy_authorization','parallel_trends_requires_review','placebo_and_sensitivity_review_required']: assert token in source

def test_plugin_contract_and_zip():
    php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text(); css=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css').read_text()
    assert 'Version: 2.5.0' in php; assert 'Catalyst Analytics R v1.5.0' in php; assert 'Public API and platform handoffs' in php; assert 'aria-live="polite"' in php
    for token in ["compatible_repository_version:'1.5.0'",'mapped_public_api_and_platform_handoff_contract_not_r_execution','credentials_not_collected','automated_platform_action:false']: assert token in js
    assert ':focus-visible' in css
    path=ROOT/'dist/catalyst-analytics-r-demo-v2.5.0.zip'; assert path.exists()
    with zipfile.ZipFile(path) as z: assert z.testzip() is None

def test_stable_api_and_docs():
    text=(ROOT/'R/production_readiness.R').read_text(); assert 'econometrics = c(' in text; assert 'econometric_evaluation = "1.0.0"' in text; assert 'version = "1.5.0"' in text; assert 'version = "2.5.0"' in text
    assert (ROOT/'docs/econometrics-policy-evaluation.md').exists(); assert (ROOT/'docs/migration-v1.3-to-v1.4.md').exists(); assert (ROOT/'docs/releases/v1.5.0.md').exists()

def test_prior_contract_examples_remain_json():
    for path in ROOT.rglob('*.json'): json.loads(path.read_text())
