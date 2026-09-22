import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
def test_release_identity_and_manifest():
    assert re.search(r"^Version: 2\.2\.0$",(ROOT/'DESCRIPTION').read_text(),re.M)
    m=load('catalyst_analytics_r_manifest.json')
    assert m['repository_version']=='2.2.0'
    c=m['contracts']['statistical_diagnostics_validation']
    assert c['contract']=='sc.analytics-r.statistical-diagnostics-validation.v1' and c['core_minimum_release']=='3.2.0'
def test_schema_and_example_boundaries():
    x=load('examples/statistical_diagnostics_validation.json')
    assert x['contract']=='sc.analytics-r.statistical-diagnostics-validation.v1'
    assert all(x['boundary'][k] is True for k in ['evidence_only','no_automatic_scientific_validity_certification','no_automatic_significance_conclusion','no_automatic_model_selection','human_review_required'])
def test_source_contract_boundaries():
    s=(ROOT/'R/statistical_diagnostics_validation.R').read_text()
    for token in ['diagnostics_are_evidence = TRUE','p_values_do_not_certify_validity = TRUE','model_comparison_does_not_select_a_winner = TRUE','no_automatic_scientific_validity_certification = TRUE','statistical_validation_from_model','statistical_validation_from_regression']:
        assert token in s
def test_provider_contract_remains_workspace_hosted():
    s=(ROOT/'R/core_computational_provider.R').read_text()
    assert 'sc.core.analytical-runtime-provider.v1' in s and 'core_minimum_release = "3.2.0"' in s
    assert 'workspace_controls_execution_environment = TRUE' in s and 'core_executes_provider = FALSE' in s
