import json, re, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def validator(path): return jsonschema.Draft202012Validator(load(path))

def test_versions_and_manifest():
    text=(ROOT/'DESCRIPTION').read_text(); assert re.search(r'^Version:\s*1\.2\.0$',text,re.M)
    m=load('catalyst_analytics_r_manifest.json'); assert m['schema_version']=='2.2.0'; assert m['repository_version']=='1.2.0'; assert m['r_package']['version']=='1.2.0'; assert m['wordpress_demo']['version']=='2.2.0'; assert m['wordpress_demo']['compatible_repository_version']=='1.2.0'
    assert m['contracts']['regional_portfolio']['version']=='1.0.0'; assert m['contracts']['regional_portfolio_export']['version']=='1.0.0'

def test_regional_contracts_validate():
    validator('schemas/catalyst_analytics_r_regional_portfolio.schema.json').validate(load('outputs/example_regional_portfolio_export.json'))
    validator('schemas/catalyst_analytics_r_regional_portfolio_demo_export.schema.json').validate(load('outputs/example_browser_regional_portfolio_export.json'))
    fixture=load('tests/fixtures/regional_portfolio_contract_v1.json'); assert fixture['repository_version']=='1.2.0'; assert fixture['expected']['weighted_gdp']==108

def test_r_apis_and_docs_exist():
    namespace=(ROOT/'NAMESPACE').read_text(); docs=(ROOT/'man/regional_portfolio.Rd').read_text(); source=(ROOT/'R/regional_portfolio.R').read_text()
    apis=['geography_scope','sector_scope','scope_scenario','portfolio_member','regional_portfolio','portfolio_aggregate','portfolio_compare_regions','regional_carbon_budgets','sector_transition_pathways','regional_portfolio_analysis','export_regional_portfolio_analysis','workspace_add_regional_portfolio']
    for api in apis: assert f'export({api})' in namespace; assert f'\\alias{{{api}}}' in (docs+(ROOT/'man/workspaces.Rd').read_text())
    for token in ['regional_sector_portfolio','absolute_decoupling','remaining_budget','human_review_required']: assert token in source

def test_plugin_contract_and_zip():
    php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text(); css=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css').read_text()
    assert 'Version: 2.2.0' in php; assert 'Catalyst Analytics R v1.2.0' in php; assert 'Regional, sector, and portfolio analytics' in php; assert 'aria-live="polite"' in php
    for token in ["compatible_repository_version:'1.2.0'",'mapped_regional_portfolio_contract_not_r_execution','weights_not_allocation_authority','sector_pathways']: assert token in js
    assert ':focus-visible' in css
    path=ROOT/'dist/catalyst-analytics-r-demo-v2.2.0.zip'; assert path.exists()
    with zipfile.ZipFile(path) as z: assert z.testzip() is None

def test_stable_api_and_docs():
    text=(ROOT/'R/production_readiness.R').read_text(); assert 'regional_portfolios = c(' in text; assert 'regional_portfolio = "1.0.0"' in text; assert 'version = "1.2.0"' in text; assert 'version = "2.2.0"' in text
    assert (ROOT/'docs/regional-sector-portfolio-analytics.md').exists(); assert (ROOT/'docs/migration-v1.1-to-v1.2.md').exists(); assert (ROOT/'docs/releases/v1.2.0.md').exists()

def test_prior_contract_examples_remain_json():
    for path in ROOT.rglob('*.json'): json.loads(path.read_text())
