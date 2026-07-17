import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_policy_optimization_fixture():
    fixture=json.loads((ROOT/'tests/fixtures/policy_optimization_contract_v1.json').read_text())
    assert fixture['repository_version']=='1.3.0'
    assert fixture['plugin_version']=='2.3.0'
    assert fixture['expected']['selected_candidate_id']=='candidate-25'
    output=json.loads((ROOT/'outputs/example_policy_optimization_export.json').read_text())
    assert output['analysis_type']=='policy_optimization'
    assert output['boundary']['recommendation_not_authorization'] is True
    assert len(output['candidates'])==fixture['expected']['candidate_count']

def test_browser_policy_boundary_is_explicit():
    output=json.loads((ROOT/'outputs/example_browser_policy_pathway_export.json').read_text())
    assert output['contract']['parity_status']=='mapped_policy_optimization_contract_not_r_execution'
    assert output['boundary']['r_not_executed'] is True
    assert output['boundary']['triggers_not_execution'] is True
