#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.4.0'; PLUGIN_VERSION='2.4.0'; MANIFEST_VERSION='2.4.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*1\.4\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('econometric_evaluation','policy_evaluation','policy_evaluation_export'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/econometrics_policy_evaluation.R','R/export_policy_evaluation.R','man/econometrics_policy_evaluation.Rd','man/export_policy_evaluation.Rd','man/workspace_policy_evaluations.Rd','schemas/catalyst_analytics_r_econometric_evaluation.schema.json','schemas/catalyst_analytics_r_policy_evaluation.schema.json','schemas/catalyst_analytics_r_policy_evaluation_export.schema.json','schemas/catalyst_analytics_r_policy_evaluation_demo_export.schema.json','examples/policy_evaluation_input.json','outputs/example_policy_evaluation_export.json','outputs/example_browser_policy_evaluation_export.json','tests/fixtures/econometrics_policy_evaluation_contract_v1.json','tests/testthat/helper-econometrics.R','tests/testthat/test-econometrics-policy-evaluation.R','docs/econometrics-policy-evaluation.md','docs/migration-v1.3-to-v1.4.md','docs/releases/v1.4.0.md','docs/releases/v1.4.0-rd-repair.md','docs/releases/v1.4.0-rd-repair-v2.md','tests_py/test_rd_usage_contract.py','tests_py/test_all_rd_integrity.py',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v1.4.0 files: {missing}')
    source=read('R/econometrics_policy_evaluation.R')
    for token in ('difference_in_differences','event_study','interrupted_time_series','synthetic_control','parallel_trends_requires_review','placebo_and_sensitivity_review_required','causal_claim_requires_design_specific_assumptions','automated_policy_authorization','stats::optim','stats::model.matrix'):
        if token not in source: fail(f'Econometrics implementation missing: {token}')
    workspace=read('R/workspaces.R')
    for token in ('policy_evaluations = list()','workspace_add_policy_evaluation','workspace_get_policy_evaluation','policy-evaluations.csv'):
        if token not in workspace: fail(f'Workspace policy-evaluation integration missing: {token}')
    namespace=read('NAMESPACE'); docs=read('man/econometrics_policy_evaluation.Rd')+'\n'+read('man/export_policy_evaluation.Rd')+'\n'+read('man/workspace_policy_evaluations.Rd')
    for rd_name in ('man/econometrics_policy_evaluation.Rd','man/workspace_policy_evaluations.Rd'):
        rd_text=read(rd_name)
        usage_start=rd_text.find('\\usage{')
        if usage_start < 0: fail(f'Missing usage section: {rd_name}')
        usage_end=rd_text.find('\n}\n\\arguments{', usage_start)
        if usage_end < 0: fail(f'Usage section is not formatted as a standalone multiline block: {rd_name}')
        usage=rd_text[usage_start:usage_end]
        if r'\n' in usage: fail(f'Escaped newline found inside Rd usage section: {rd_name}')
        if usage.count('\n') < 2: fail(f'Rd usage section must use real line breaks: {rd_name}')
    apis=('causal_assumption','regression_spec','validate_regression_spec','fit_policy_regression','panel_regression','regression_diagnostics','difference_in_differences','event_study','interrupted_time_series','synthetic_control','policy_effect_summary','policy_evaluation_analysis','policy_evaluation_summary','plot_policy_effects','plot_event_study','plot_synthetic_control','export_policy_evaluation','workspace_add_policy_evaluation','workspace_get_policy_evaluation')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'API documentation missing: {name}')
    for method in ('S3method(print,catalyst_policy_regression)','S3method(print,catalyst_policy_evaluation_analysis)'):
        if method not in namespace: fail(f'Missing S3 registration: {method}')
    production=read('R/production_readiness.R')
    for token in ('econometrics = c(','econometric_evaluation = "1.0.0"','policy_evaluation_analysis = "1.0.0"','version = "1.4.0"','version = "2.4.0"'):
        if token not in production: fail(f'Stable API contract missing: {token}')
    tests=read('tests/testthat/test-econometrics-policy-evaluation.R')
    for token in ('difference in differences recovers the policy effect','event study preserves dynamic effects','interrupted time series estimates level and slope changes','synthetic control reconstructs the untreated pathway','workspaces retain reusable policy evaluations','manifest$file_count >= 5L'):
        if token not in tests: fail(f'Missing econometrics regression coverage: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    validator('schemas/catalyst_analytics_r_policy_evaluation.schema.json').validate(load('outputs/example_policy_evaluation_export.json'))
    validator('schemas/catalyst_analytics_r_policy_evaluation_demo_export.schema.json').validate(load('outputs/example_browser_policy_evaluation_export.json'))
    export_example={'schema_version':'1.0.0','export_type':'econometrics_and_policy_evaluation_bundle','analysis_id':'transition-policy-evaluation','package':{'name':'catalystanalyticsr','version':'1.4.0'},'created_at':'2026-07-17T00:00:00Z','file_count':5,'files':[],'integrity':{},'boundary':{'human_review_required':True,'causal_validity_not_automatic':True,'policy_authorization':False}}
    validator('schemas/catalyst_analytics_r_policy_evaluation_export.schema.json').validate(export_example)
    validator('schemas/catalyst_analytics_r_econometric_evaluation.schema.json').validate(load('outputs/example_policy_evaluation_export.json')['evaluations']['did'])
    prior=[('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json'),('schemas/catalyst_analytics_r_workspace.schema.json','examples/workspace_input.json'),('schemas/catalyst_analytics_r_regional_portfolio.schema.json','outputs/example_regional_portfolio_export.json'),('schemas/catalyst_analytics_r_policy_optimization.schema.json','outputs/example_policy_optimization_export.json')]
    for schema,payload in prior: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.4\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Econometrics and policy evaluation','Evaluate policy effect','Causal boundary','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'1.4.0'",'mapped_econometric_policy_evaluation_contract_not_r_execution','causal_validity_not_automatic','automated_policy_authorization:false'):
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
    print('Catalyst Analytics R v1.4.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, econometrics and policy-evaluation contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
