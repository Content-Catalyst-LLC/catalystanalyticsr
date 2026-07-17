#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.5.0'; PLUGIN_VERSION='2.5.0'; MANIFEST_VERSION='2.5.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*1\.5\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('public_api','api_request','api_response','platform_handoff','platform_handoff_export'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/public_api_handoffs.R','R/export_platform_handoffs.R','man/public_api_handoffs.Rd','man/export_platform_handoffs.Rd','schemas/catalyst_analytics_r_public_api.schema.json','schemas/catalyst_analytics_r_api_request.schema.json','schemas/catalyst_analytics_r_api_response.schema.json','schemas/catalyst_analytics_r_platform_handoff.schema.json','schemas/catalyst_analytics_r_platform_handoff_export.schema.json','schemas/catalyst_analytics_r_platform_demo_export.schema.json','examples/public_api_request.json','outputs/example_public_api_manifest.json','outputs/example_api_response.json','outputs/example_platform_handoff.json','outputs/example_platform_handoff_export.json','outputs/example_browser_platform_export.json','tests/fixtures/public_api_handoff_contract_v1.json','tests/testthat/test-public-api-handoffs.R','tests_py/test_public_api_handoff_contract.py','docs/public-api-and-platform-handoffs.md','docs/migration-v1.4-to-v1.5.md','docs/releases/v1.5.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v1.5.0 files: {missing}')
    source=read('R/public_api_handoffs.R')+'\n'+read('R/export_platform_handoffs.R')
    for token in ('catalyst_public_api_manifest','dispatch_api_request','site_intelligence_handoff','research_lab_handoff','workbench_handoff','catalyst_canvas_handoff','decision_studio','knowledge_library','transport_server_not_included','automated_platform_action = FALSE','workspace_add_platform_handoff'):
        if token not in source: fail(f'Public API/handoff implementation missing: {token}')
    workspace=read('R/workspaces.R')
    for token in ('platform_handoffs = list()','platform_handoffs = length','platform-handoffs.csv'):
        if token not in workspace: fail(f'Workspace handoff integration missing: {token}')
    namespace=read('NAMESPACE'); docs=read('man/public_api_handoffs.Rd')+'\n'+read('man/export_platform_handoffs.Rd')
    apis=('api_endpoint','catalyst_public_api_manifest','api_request','validate_api_request','api_response','validate_api_response','dispatch_api_request','site_intelligence_handoff','research_lab_handoff','workbench_handoff','catalyst_canvas_handoff','platform_handoff','validate_platform_handoff','handoff_to_json','handoff_from_json','export_platform_handoffs','workspace_add_platform_handoff','workspace_get_platform_handoff')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'API documentation missing: {name}')
    readiness_test=read('tests/testthat/test-production-readiness.R')
    if 'expect_identical(compatibility$wordpress$version, "2.5.0")' not in readiness_test: fail('Production-readiness compatibility test is stale')
    if 'expect_identical(compatibility$wordpress$version, "2.4.0")' in readiness_test: fail('Stale WordPress 2.4.0 compatibility expectation remains')
    production=read('R/production_readiness.R')
    for token in ('platform_api = c(','public_api = "1.0.0"','platform_handoff = "1.0.0"','version = "1.5.0"','version = "2.5.0"'):
        if token not in production: fail(f'Stable API contract missing: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    pairs=[('schemas/catalyst_analytics_r_public_api.schema.json','outputs/example_public_api_manifest.json'),('schemas/catalyst_analytics_r_api_request.schema.json','examples/public_api_request.json'),('schemas/catalyst_analytics_r_api_response.schema.json','outputs/example_api_response.json'),('schemas/catalyst_analytics_r_platform_handoff.schema.json','outputs/example_platform_handoff.json'),('schemas/catalyst_analytics_r_platform_handoff_export.schema.json','outputs/example_platform_handoff_export.json'),('schemas/catalyst_analytics_r_platform_demo_export.schema.json','outputs/example_browser_platform_export.json')]
    for schema,payload in pairs: validator(schema).validate(load(payload))
    prior=[('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json'),('schemas/catalyst_analytics_r_workspace.schema.json','examples/workspace_input.json'),('schemas/catalyst_analytics_r_regional_portfolio.schema.json','outputs/example_regional_portfolio_export.json'),('schemas/catalyst_analytics_r_policy_optimization.schema.json','outputs/example_policy_optimization_export.json'),('schemas/catalyst_analytics_r_policy_evaluation.schema.json','outputs/example_policy_evaluation_export.json')]
    for schema,payload in prior: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.5\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Public API and platform handoffs','Build handoff preview','Execution boundary','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'1.5.0'",'mapped_public_api_and_platform_handoff_contract_not_r_execution','credentials_not_collected:true','automated_platform_action:false'):
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
    print('Catalyst Analytics R v1.5.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, public API and first-party platform handoff contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
