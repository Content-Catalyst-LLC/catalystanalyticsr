from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def test_econometrics_contract_files_and_versions():
    assert 'Version: 1.5.0' in (ROOT/'DESCRIPTION').read_text()
    manifest=json.loads((ROOT/'catalyst_analytics_r_manifest.json').read_text())
    assert manifest['repository_version']=='1.5.0'
    assert manifest['wordpress_demo']['version']=='2.5.0'
    assert manifest['contracts']['policy_evaluation']['version']=='1.0.0'
def test_econometric_methods_and_boundaries_present():
    source=(ROOT/'R/econometrics_policy_evaluation.R').read_text()
    for token in ['difference_in_differences','event_study','interrupted_time_series','synthetic_control','causal_claim_requires_design_specific_assumptions','automated_policy_authorization']:
        assert token in source
def test_browser_contract_discloses_non_r_boundary():
    js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text()
    for token in ["compatible_repository_version:'1.5.0'",'mapped_public_api_and_platform_handoff_contract_not_r_execution','credentials_not_collected:true','automated_platform_action:false']:
        assert token in js
