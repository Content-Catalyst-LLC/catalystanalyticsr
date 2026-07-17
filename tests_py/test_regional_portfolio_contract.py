import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_regional_portfolio_contract_files():
    fixture=json.loads((ROOT/'tests/fixtures/regional_portfolio_contract_v1.json').read_text())
    assert fixture['repository_version']=='1.2.0'
    assert fixture['expected']['weighted_gdp']==108
    output=json.loads((ROOT/'outputs/example_regional_portfolio_export.json').read_text())
    assert output['analysis_type']=='regional_sector_portfolio_analysis'
    assert output['meta']['human_review_required'] is True

def test_browser_boundary_is_explicit():
    output=json.loads((ROOT/'outputs/example_browser_regional_portfolio_export.json').read_text())
    assert output['contract']['parity_status']=='mapped_regional_portfolio_contract_not_r_execution'
    assert output['boundary']['weights_not_allocation_authority'] is True
