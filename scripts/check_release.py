#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='2.2.0'; PLUGIN_VERSION='3.2.0'; MANIFEST_VERSION='3.2.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*2\.2\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('connected_platform','connected_platform_export','connected_api'):
        if manifest['contracts'][name]['version']!='2.0.0': fail(f'{name} protocol contract changed unexpectedly')
    for name in ('core_provider','core_execution_request','core_execution_result','workspace_core_execution','statistical_diagnostics_validation'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/core_computational_provider.R','R/statistical_diagnostics_validation.R','man/statistical_diagnostics_validation.Rd','schemas/catalyst_analytics_r_statistical_diagnostics_validation.schema.json','examples/statistical_diagnostics_validation.json','tests/testthat/test-statistical-diagnostics-validation.R','tests_py/test_statistical_diagnostics_validation_contract.py','docs/statistical-diagnostics-validation-contract.md','docs/releases/v2.2.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v2.2.0 files: {missing}')
    source=read('R/statistical_diagnostics_validation.R')
    for token in ('sc.analytics-r.statistical-diagnostics-validation.v1','diagnostics_are_evidence = TRUE','p_values_do_not_certify_validity = TRUE','model_comparison_does_not_select_a_winner = TRUE','no_automatic_scientific_validity_certification = TRUE','human_review_required = TRUE'):
        if token not in source: fail(f'Diagnostics boundary missing: {token}')
    provider=load('examples/core_provider_manifest.json')
    if provider['provider_key']!='catalystanalyticsr' or provider['provider_version']!='2.2.0' or provider['runtime']!='r' or provider['execution_host']!='workspace': fail('Provider identity mismatch')
    if provider['boundary']['core_executes_provider'] is not False or provider['boundary']['arbitrary_function_dispatch'] is not False: fail('Provider runtime boundary mismatch')
    schemas=[('schemas/catalyst_analytics_r_statistical_diagnostics_validation.schema.json','examples/statistical_diagnostics_validation.json'),('schemas/catalyst_analytics_r_core_provider.schema.json','examples/core_provider_manifest.json'),('schemas/catalyst_analytics_r_core_request.schema.json','examples/core_analytical_request.json'),('schemas/catalyst_analytics_r_workspace_core_execution.schema.json','examples/workspace_core_execution_envelope.json'),('schemas/catalyst_analytics_r_core_result.schema.json','examples/core_analytical_result.json'),('schemas/catalyst_analytics_r_release_readiness.schema.json','examples/release_readiness.json')]
    for schema,payload in schemas: validator(schema).validate(load(payload))
    namespace=read('NAMESPACE'); aliases='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'man').glob('*.Rd'))
    apis=('statistical_diagnostics_manifest','statistical_diagnostic','statistical_assumption','statistical_robustness_evidence','statistical_model_comparison','statistical_validation_bundle','validate_statistical_validation_bundle','statistical_validation_from_model','statistical_validation_from_regression','statistical_validation_to_json','statistical_validation_from_json')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in aliases: fail(f'Diagnostics API documentation missing: {name}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*3\.2\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Catalyst Analytics R v2.2.0','Diagnostics contract v1','catalystanalyticsr 2.2.0'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'2.2.0'","statistical_diagnostics_contract:'sc.analytics-r.statistical-diagnostics-validation.v1'","core_executes_provider:false"):
        if token not in js: fail(f'Browser diagnostics contract missing: {token}')
    if ':focus-visible' not in css: fail('Focus visibility contract missing')
    with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
        if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
    run([sys.executable,'scripts/check_r_structure.py']); run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
    if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
    if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
    debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
    if debris: fail(f'Generated debris remains: {debris}')
    print('Catalyst Analytics R v2.2.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, diagnostics/validation contract, Core provider compatibility, WordPress mapping, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
