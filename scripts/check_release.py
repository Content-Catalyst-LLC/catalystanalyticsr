#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='2.1.0'; PLUGIN_VERSION='3.1.0'; MANIFEST_VERSION='3.1.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*2\.1\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('connected_platform','connected_platform_export','connected_api'):
        if manifest['contracts'][name]['version']!='2.0.0': fail(f'{name} protocol contract changed unexpectedly')
    for name in ('core_provider','core_execution_request','core_execution_result','workspace_core_execution'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/core_computational_provider.R','man/core_computational_provider.Rd','schemas/catalyst_analytics_r_core_provider.schema.json','schemas/catalyst_analytics_r_core_request.schema.json','schemas/catalyst_analytics_r_core_result.schema.json','schemas/catalyst_analytics_r_workspace_core_execution.schema.json','examples/core_provider_manifest.json','examples/core_analytical_request.json','examples/workspace_core_execution_envelope.json','examples/core_analytical_result.json','tests/testthat/test-core-computational-provider.R','tests_py/test_core_computational_provider_contract.py','docs/platform-core-computational-provider.md','docs/releases/v2.1.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v2.1.0 files: {missing}')
    source=read('R/core_computational_provider.R')
    for token in ('sc.core.analytical-runtime-provider.v1','core_executes_provider = FALSE','workspace_controls_execution_environment = TRUE','arbitrary_function_dispatch = FALSE','workspace_must_resolve_input_refs = TRUE','result_does_not_certify_scientific_validity = TRUE','projection_only'):
        if token not in source: fail(f'Core provider boundary missing: {token}')
    provider=load('examples/core_provider_manifest.json')
    if provider['provider_key']!='catalystanalyticsr' or provider['provider_version']!='2.1.0' or provider['runtime']!='r' or provider['execution_host']!='workspace': fail('Provider identity mismatch')
    if provider['boundary']['core_executes_provider'] is not False or provider['boundary']['arbitrary_function_dispatch'] is not False: fail('Provider runtime boundary mismatch')
    if len(provider['capabilities']) != 12: fail('Expected 12 Core analytical capabilities')
    schemas=[('schemas/catalyst_analytics_r_core_provider.schema.json','examples/core_provider_manifest.json'),('schemas/catalyst_analytics_r_core_request.schema.json','examples/core_analytical_request.json'),('schemas/catalyst_analytics_r_workspace_core_execution.schema.json','examples/workspace_core_execution_envelope.json'),('schemas/catalyst_analytics_r_core_result.schema.json','examples/core_analytical_result.json'),('schemas/catalyst_analytics_r_release_readiness.schema.json','examples/release_readiness.json'),('schemas/catalyst_analytics_r_connected_platform.schema.json','examples/connected_platform_input.json')]
    for schema,payload in schemas: validator(schema).validate(load(payload))
    namespace=read('NAMESPACE'); docs=read('man/core_computational_provider.Rd')
    apis=('catalyst_core_provider_manifest','core_analytical_request','as_core_analytical_request','validate_core_analytical_request','core_execution_plan','workspace_core_execution_envelope','core_analytical_result','validate_core_analytical_result','core_request_to_json','core_request_from_json','core_result_to_json','core_result_from_json')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'Core provider API documentation missing: {name}')
    readiness=read('R/production_readiness.R')
    for token in ('connected_platform = "2.0.0"','core_provider = "1.0.0"','core_execution_request = "1.0.0"','core_execution_result = "1.0.0"','workspace_core_execution = "1.0.0"','.catalyst_package_version()','version = "3.1.0"'):
        if token not in readiness: fail(f'Production contract missing: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*3\.1\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Platform Core','Analytical runtime provider','catalystanalyticsr 2.1.0','Workspace execution host','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'2.1.0'","core_provider_contract:'sc.core.analytical-runtime-provider.v1'","runtime:'r'","execution_host:'workspace'","core_executes_provider:false"):
        if token not in js: fail(f'Browser provider contract missing: {token}')
    if ':focus-visible' not in css: fail('Focus visibility contract missing')
    with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
        if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
    exports=re.findall(r'^export\(([^)]+)\)$',namespace,re.M); aliases='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'man').glob('*.Rd')); missing_alias=[n for n in exports if f'\\alias{{{n}}}' not in aliases]
    if missing_alias: fail(f'Exported functions missing Rd aliases: {missing_alias}')
    for rd in (ROOT/'man').glob('*.Rd'):
        text=rd.read_text(encoding='utf-8')
        if re.search(r'\\n(?!ame\{)', text): fail(f'Stray escaped newline in Rd: {rd.name}')
    run([sys.executable,'scripts/check_r_structure.py']); run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
    if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
    if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
    debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
    if debris: fail(f'Generated debris remains: {debris}')
    print('Catalyst Analytics R v2.1.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, Core computational-provider contracts, prior analytical contracts, WordPress mapping, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
