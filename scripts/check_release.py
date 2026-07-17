#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v1.3.0."""
from __future__ import annotations
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.3.0'; PLUGIN_VERSION='2.3.0'; MANIFEST_VERSION='2.3.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*1\.3\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('policy_optimization','policy_pathway','policy_pathway_export'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/policy_optimization.R','R/export_policy_pathways.R','man/policy_optimization.Rd','man/export_policy_pathway_analysis.Rd','schemas/catalyst_analytics_r_policy_optimization.schema.json','schemas/catalyst_analytics_r_policy_pathway.schema.json','schemas/catalyst_analytics_r_policy_pathway_export.schema.json','schemas/catalyst_analytics_r_policy_pathway_demo_export.schema.json','examples/policy_optimization_input.json','outputs/example_policy_optimization_export.json','outputs/example_browser_policy_pathway_export.json','tests/fixtures/policy_optimization_contract_v1.json','tests/testthat/helper-policy-optimization.R','tests/testthat/test-policy-optimization.R','tests/testthat/test-policy-pathway-export.R','docs/optimization-policy-pathway-design.md','docs/migration-v1.2-to-v1.3.md','docs/releases/v1.3.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v1.3.0 files: {missing}')
    source=read('R/policy_optimization.R')
    for token in ('policy_optimization_specification','pareto_frontier','recommendation_not_authorization','triggers_do_not_execute_actions','normalized_loss','human_review_required','optimized_scenario_not_policy_authorization','constraint_metric_ids','stats::ave'):
        if token not in source: fail(f'Optimization implementation missing: {token}')
    workspace=read('R/workspaces.R')
    for token in ('policy_optimizations = list()','policy_pathways = list()','workspace_add_policy_optimization','workspace_add_policy_pathway','policy-optimizations.csv','policy-pathways.csv'):
        if token not in workspace: fail(f'Workspace policy integration missing: {token}')
    namespace=read('NAMESPACE'); docs=read('man/policy_optimization.Rd')+'\n'+read('man/export_policy_pathway_analysis.Rd')+'\n'+read('man/workspaces.Rd')
    apis=('decision_variable','policy_objective','policy_constraint','policy_optimization_spec','validate_policy_optimization_spec','evaluate_policy_candidates','optimize_policy','policy_pareto_frontier','policy_feasible_region','target_seeking_scenario','cost_effectiveness_analysis','marginal_abatement_curve','adaptive_trigger','policy_stage','policy_pathway','validate_policy_pathway','policy_sequence','evaluate_policy_pathway','robust_pathway_analysis','policy_pathway_analysis','policy_optimization_summary','plot_policy_pareto','plot_marginal_abatement','plot_policy_pathway','export_policy_pathway_analysis','workspace_add_policy_optimization','workspace_get_policy_optimization','workspace_add_policy_pathway','workspace_get_policy_pathway')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'API documentation missing: {name}')
    for method in ('S3method(print,catalyst_policy_optimization)','S3method(print,catalyst_policy_pathway)'):
        if method not in namespace: fail(f'Missing S3 registration: {method}')
    production=read('R/production_readiness.R')
    for token in ('policy_optimization = c(','policy_optimization = "1.0.0"','policy_pathway = "1.0.0"','version = "1.3.0"','version = "2.3.0"'):
        if token not in production: fail(f'Stable API contract missing: {token}')
    tests=read('tests/testthat/test-policy-optimization.R')+read('tests/testthat/test-policy-pathway-export.R')
    for token in ('optimization identifies feasible and Pareto','expect_type(result$recommendation$metrics$jobs, "double")','target-seeking scenarios preserve canonical contracts','adaptive pathways generate review prompts','robust pathway analysis reports normalized regret','manifest$file_count >= 8L'):
        if token not in tests: fail(f'Missing policy regression coverage: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
    validator('schemas/catalyst_analytics_r_policy_optimization.schema.json').validate(load('outputs/example_policy_optimization_export.json'))
    validator('schemas/catalyst_analytics_r_policy_pathway_demo_export.schema.json').validate(load('outputs/example_browser_policy_pathway_export.json'))
    export_example={'schema_version':'1.0.0','export_type':'optimization_and_policy_pathway_bundle','analysis_id':'transition-optimization','package':{'name':'catalystanalyticsr','version':'1.3.0'},'created_at':'2026-07-17T00:00:00Z','file_count':8,'files':[],'integrity':{},'boundary':{'human_review_required':True,'recommendation_not_authorization':True,'triggers_not_execution':True}}
    validator('schemas/catalyst_analytics_r_policy_pathway_export.schema.json').validate(export_example)
    validator('schemas/catalyst_analytics_r_policy_pathway.schema.json').validate(load('examples/policy_optimization_input.json')['pathway'])
    prior=[('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json'),('schemas/catalyst_analytics_r_workspace.schema.json','examples/workspace_input.json'),('schemas/catalyst_analytics_r_regional_portfolio.schema.json','outputs/example_regional_portfolio_export.json')]
    for schema,payload in prior: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.3\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Optimization and policy pathway design','Optimize policy pathway','Pareto frontier','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'1.3.0'",'mapped_policy_optimization_contract_not_r_execution','recommendation_not_authorization','triggers_not_execution','pareto_frontier'):
        if token not in js: fail(f'Browser contract missing: {token}')
    if ':focus-visible' not in css: fail('Focus visibility contract missing')
    with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
        if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
    exports=re.findall(r'^export\(([^)]+)\)$',namespace,re.M); aliases='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'man').glob('*.Rd')); missing_alias=[n for n in exports if f'\\alias{{{n}}}' not in aliases]
    if missing_alias: fail(f'Exported functions missing Rd aliases: {missing_alias}')
    run([sys.executable,'scripts/check_r_structure.py']); run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
    if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
    if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
    debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
    if debris: fail(f'Generated debris remains: {debris}')
    print('Catalyst Analytics R v1.3.0 release contract passed.')
    print(f'Validated {len(list(ROOT.rglob("*.json")))} JSON files, optimization and adaptive pathway contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
