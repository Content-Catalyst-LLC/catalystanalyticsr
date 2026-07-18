#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='2.0.0'; PLUGIN_VERSION='3.0.0'; MANIFEST_VERSION='3.0.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*2\.0\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('connected_platform','connected_platform_export','connected_api'):
        if manifest['contracts'][name]['version']!='2.0.0': fail(f'{name} contract mismatch')
    required=['R/connected_platform.R','man/connected_platform.Rd','man/export_connected_platform.Rd','schemas/catalyst_analytics_r_connected_platform.schema.json','schemas/catalyst_analytics_r_connected_platform_export.schema.json','schemas/catalyst_analytics_r_connected_platform_demo_export.schema.json','examples/connected_platform_input.json','outputs/example_connected_platform_export.json','outputs/example_browser_connected_platform_export.json','tests/fixtures/connected_platform_contract_v2.json','tests/testthat/test-connected-platform.R','tests_py/test_connected_platform_contract.py','docs/connected-sustainability-analytics-decision-platform.md','docs/migration-v1.6-to-v2.0.md','docs/releases/v2.0.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v2.0.0 files: {missing}')
    source=read('R/connected_platform.R')
    for token in ('connected_sustainability_platform','platform_add_workspace','platform_add_project','platform_register_records','platform_add_decision','platform_add_publication','platform_add_governance','platform_add_handoff','platform_add_workflow','platform_lineage','connected_platform_manifest','export_connected_platform','catalyst_connected_api_manifest','dispatch_connected_api_request','.connected_platform_fingerprint_record','.connected_platform_raw_fingerprint','serialized_platform_fingerprint','.restored_connected_platform_state_fingerprint','automated_decision_authorization = FALSE','automated_publication = FALSE'):
        if token not in source: fail(f'Connected platform implementation missing: {token}')
    namespace=read('NAMESPACE'); docs=read('man/connected_platform.Rd')+'\n'+read('man/export_connected_platform.Rd')
    apis=('platform_node','platform_edge','platform_evidence_record','platform_decision_record','platform_publication_record','connected_workflow','connected_sustainability_platform','validate_connected_platform','platform_add_node','platform_add_edge','platform_add_project','platform_add_workspace','platform_register_records','platform_add_decision','platform_add_publication','platform_add_governance','platform_add_handoff','platform_add_workflow','platform_lineage','connected_platform_summary','connected_platform_manifest','connected_platform_fingerprint','connected_platform_to_json','connected_platform_from_json','export_connected_platform','catalyst_connected_api_manifest','connected_api_request','dispatch_connected_api_request')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'Connected API documentation missing: {name}')
    readiness=read('R/production_readiness.R')
    for token in ('connected_platform = "2.0.0"','connected_platform_export = "2.0.0"','connected_api = "2.0.0"','version = "2.0.0"','version = "3.0.0"'):
        if token not in readiness: fail(f'Production contract missing: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    for schema,payload in [('schemas/catalyst_analytics_r_connected_platform.schema.json','examples/connected_platform_input.json'),('schemas/catalyst_analytics_r_connected_platform_export.schema.json','outputs/example_connected_platform_export.json'),('schemas/catalyst_analytics_r_connected_platform_demo_export.schema.json','outputs/example_browser_connected_platform_export.json'),('schemas/catalyst_analytics_r_institutional_governance.schema.json','examples/institutional_governance_input.json'),('schemas/catalyst_analytics_r_platform_handoff.schema.json','outputs/example_platform_handoff.json')]: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*3\.0\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Connected Sustainability Analytics and Decision Platform','Build connected platform','Connected-platform boundary','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'2.0.0'",'mapped_connected_platform_contract_not_r_execution','automated_decision_authorization:false','automated_publication:false'):
        if token not in js: fail(f'Browser contract missing: {token}')
    if ':focus-visible' not in css: fail('Focus visibility contract missing')
    with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
        if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
    exports=re.findall(r'^export\(([^)]+)\)$',namespace,re.M); aliases='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'man').glob('*.Rd')); missing_alias=[n for n in exports if f'\\alias{{{n}}}' not in aliases]
    if missing_alias: fail(f'Exported functions missing Rd aliases: {missing_alias}')
    connected_test=read('tests/testthat/test-connected-platform.R')
    for token in ('expect_identical(connected_platform_fingerprint(restored), original_fingerprint)','expect_false(identical(connected_platform_fingerprint(changed), original_fingerprint))','serialized_platform_fingerprint'):
        if token not in connected_test: fail(f'Connected-platform fingerprint regression guard missing: {token}')
    for rd in (ROOT/'man').glob('*.Rd'):
        text=rd.read_text(encoding='utf-8')
        if re.search(r'\\n(?!ame\{)', text): fail(f'Stray escaped newline in Rd: {rd.name}')
    run([sys.executable,'scripts/check_r_structure.py']); run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
    if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
    if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
    debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
    if debris: fail(f'Generated debris remains: {debris}')
    print('Catalyst Analytics R v2.0.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, connected platform graph, API v2, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
