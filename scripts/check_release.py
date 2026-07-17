#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v1.2.0."""
from __future__ import annotations
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.2.0'; PLUGIN_VERSION='2.2.0'; MANIFEST_VERSION='2.2.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*1\.2\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('regional_portfolio','regional_portfolio_export'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/regional_portfolio.R','R/export_regional_portfolio.R','man/regional_portfolio.Rd','schemas/catalyst_analytics_r_regional_portfolio.schema.json','schemas/catalyst_analytics_r_regional_portfolio_export.schema.json','schemas/catalyst_analytics_r_regional_portfolio_demo_export.schema.json','examples/regional_portfolio_input.json','outputs/example_regional_portfolio_export.json','outputs/example_browser_regional_portfolio_export.json','tests/fixtures/regional_portfolio_contract_v1.json','tests/testthat/helper-regional-portfolio.R','tests/testthat/test-regional-portfolio.R','tests/testthat/test-regional-portfolio-export.R','docs/regional-sector-portfolio-analytics.md','docs/migration-v1.1-to-v1.2.md','docs/releases/v1.2.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v1.2.0 files: {missing}')
    source=read('R/regional_portfolio.R')
    for token in ('regional_sector_portfolio','portfolio_aggregate','portfolio_compare_regions','remaining_budget','absolute_decoupling','human_review_required','.normalize_portfolio_price_year','x["price_year"] <- list'):
        if token not in source: fail(f'Regional implementation missing: {token}')
    tests=read('tests/testthat/test-regional-portfolio.R')
    for token in ('normalizes JSON null and omission','price year validation is nullable and scalar','expect_identical(restored$price_year, NA_integer_)'):
        if token not in tests: fail(f'Missing price-year regression coverage: {token}')
    namespace=read('NAMESPACE'); docs=read('man/regional_portfolio.Rd')+'\n'+read('man/workspaces.Rd')
    apis=('geography_scope','validate_geography_scope','sector_scope','validate_sector_scope','scope_scenario','portfolio_member','regional_portfolio','validate_regional_portfolio','portfolio_aggregate','portfolio_compare_regions','weighted_indicator_summary','regional_carbon_budgets','sector_transition_pathways','regional_portfolio_analysis','regional_portfolio_summary','regional_portfolio_to_json','regional_portfolio_from_json','plot_portfolio_indicators','plot_regional_carbon_budgets','export_regional_portfolio_analysis','workspace_add_regional_portfolio','workspace_get_regional_portfolio')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'API documentation missing: {name}')
    for method in ('S3method(print,catalyst_regional_portfolio)','S3method(print,catalyst_regional_portfolio_analysis)'):
        if method not in namespace: fail(f'Missing S3 registration: {method}')
    production=read('R/production_readiness.R')
    for token in ('regional_portfolios = c(','regional_portfolio = "1.0.0"','regional_portfolio_analysis = "1.0.0"','version = "1.2.0"','version = "2.2.0"'):
        if token not in production: fail(f'Stable API contract missing: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
    validator('schemas/catalyst_analytics_r_regional_portfolio.schema.json').validate(load('outputs/example_regional_portfolio_export.json'))
    validator('schemas/catalyst_analytics_r_regional_portfolio_demo_export.schema.json').validate(load('outputs/example_browser_regional_portfolio_export.json'))
    export_example={'schema_version':'1.0.0','export_type':'regional_sector_portfolio_analytics_bundle','analysis_id':'transition-portfolio','package':{'name':'catalystanalyticsr','version':'1.2.0'},'file_count':8,'files':[],'integrity':{},'boundary':{}}
    validator('schemas/catalyst_analytics_r_regional_portfolio_export.schema.json').validate(export_example)
    prior=[('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json'),('schemas/catalyst_analytics_r_workspace.schema.json','examples/workspace_input.json')]
    for schema,payload in prior: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.2\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Regional, sector, and portfolio analytics','Run portfolio analysis','Carbon budgets','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'1.2.0'",'mapped_regional_portfolio_contract_not_r_execution','weights_not_allocation_authority','sector_pathways','portfolio_aggregates'):
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
    print('Catalyst Analytics R v1.2.0 release contract passed.')
    print(f'Validated {len(list(ROOT.rglob("*.json")))} JSON files, regional and sector portfolio contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
