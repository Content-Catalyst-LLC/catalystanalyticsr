import json, re, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def validator(path): return jsonschema.Draft202012Validator(load(path))

def test_versions_and_manifest():
    text=(ROOT/'DESCRIPTION').read_text(); assert re.search(r'^Version:\s*1\.3\.0$',text,re.M)
    m=load('catalyst_analytics_r_manifest.json'); assert m['schema_version']=='2.3.0'; assert m['repository_version']=='1.3.0'; assert m['r_package']['version']=='1.3.0'; assert m['wordpress_demo']['version']=='2.3.0'; assert m['wordpress_demo']['compatible_repository_version']=='1.3.0'
    for contract in ('policy_optimization','policy_pathway','policy_pathway_export'): assert m['contracts'][contract]['version']=='1.0.0'

def test_policy_contracts_validate():
    validator('schemas/catalyst_analytics_r_policy_optimization.schema.json').validate(load('outputs/example_policy_optimization_export.json'))
    validator('schemas/catalyst_analytics_r_policy_pathway_demo_export.schema.json').validate(load('outputs/example_browser_policy_pathway_export.json'))
    fixture=load('tests/fixtures/policy_optimization_contract_v1.json'); assert fixture['repository_version']=='1.3.0'; assert fixture['expected']['candidate_count']==25; assert fixture['expected']['feasible_count']>0

def test_r_apis_and_docs_exist():
    namespace=(ROOT/'NAMESPACE').read_text(); docs=(ROOT/'man/policy_optimization.Rd').read_text()+(ROOT/'man/export_policy_pathway_analysis.Rd').read_text()+(ROOT/'man/workspaces.Rd').read_text(); source=(ROOT/'R/policy_optimization.R').read_text()
    apis=['decision_variable','policy_objective','policy_constraint','policy_optimization_spec','evaluate_policy_candidates','optimize_policy','policy_pareto_frontier','policy_feasible_region','target_seeking_scenario','cost_effectiveness_analysis','marginal_abatement_curve','adaptive_trigger','policy_stage','policy_pathway','evaluate_policy_pathway','robust_pathway_analysis','policy_pathway_analysis','export_policy_pathway_analysis','workspace_add_policy_optimization','workspace_add_policy_pathway']
    for api in apis: assert f'export({api})' in namespace; assert f'\\alias{{{api}}}' in docs
    for token in ['recommendation_not_authorization','triggers_do_not_execute_actions','normalized_loss','pareto_frontier','human_review_required']: assert token in source

def test_plugin_contract_and_zip():
    php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text(); css=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css').read_text()
    assert 'Version: 2.3.0' in php; assert 'Catalyst Analytics R v1.3.0' in php; assert 'Optimization and policy pathway design' in php; assert 'aria-live="polite"' in php
    for token in ["compatible_repository_version:'1.3.0'",'mapped_policy_optimization_contract_not_r_execution','recommendation_not_authorization','triggers_not_execution']: assert token in js
    assert ':focus-visible' in css
    path=ROOT/'dist/catalyst-analytics-r-demo-v2.3.0.zip'; assert path.exists()
    with zipfile.ZipFile(path) as z: assert z.testzip() is None

def test_stable_api_and_docs():
    text=(ROOT/'R/production_readiness.R').read_text(); assert 'policy_optimization = c(' in text; assert 'policy_optimization = "1.0.0"' in text; assert 'version = "1.3.0"' in text; assert 'version = "2.3.0"' in text
    assert (ROOT/'docs/optimization-policy-pathway-design.md').exists(); assert (ROOT/'docs/migration-v1.2-to-v1.3.md').exists(); assert (ROOT/'docs/releases/v1.3.0.md').exists()

def test_prior_contract_examples_remain_json():
    for path in ROOT.rglob('*.json'): json.loads(path.read_text())
