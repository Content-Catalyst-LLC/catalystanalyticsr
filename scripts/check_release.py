#!/usr/bin/env python3
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.6.0'; PLUGIN_VERSION='2.6.0'; MANIFEST_VERSION='2.6.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
    if not re.search(r'^Version:\s*1\.6\.0$',read('DESCRIPTION'),re.M): fail('DESCRIPTION version mismatch')
    manifest=load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('institutional_governance','institutional_governance_export'):
        if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
    required=['R/institutional_governance.R','man/institutional_governance.Rd','man/export_institutional_governance.Rd','schemas/catalyst_analytics_r_institutional_governance.schema.json','schemas/catalyst_analytics_r_institutional_governance_export.schema.json','schemas/catalyst_analytics_r_institutional_governance_demo_export.schema.json','examples/institutional_governance_input.json','outputs/example_institutional_governance_export.json','outputs/example_browser_institutional_governance_export.json','tests/fixtures/institutional_governance_contract_v1.json','tests/testthat/test-institutional-governance.R','tests_py/test_institutional_governance_contract.py','docs/collaborative-review-institutional-governance.md','docs/migration-v1.5-to-v1.6.md','docs/releases/v1.6.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
    missing=[p for p in required if not (ROOT/p).exists()]
    if missing: fail(f'Missing v1.6.0 files: {missing}')
    source=read('R/institutional_governance.R')
    for token in ('institutional_governance_workflow','assign_institutional_review','add_review_comment','submit_change_request','resolve_change_request','record_governance_approval','sign_analytical_release','archive_governance_workflow','restricted_access_policy','governance_audit_log','workspace_add_institutional_governance','automated_publication = FALSE'):
        if token not in source: fail(f'Institutional governance implementation missing: {token}')
    workspace=read('R/workspaces.R')
    for token in ('institutional_governance = list()','institutional_governance = length','institutional-governance.csv'):
        if token not in workspace: fail(f'Workspace governance integration missing: {token}')
    namespace=read('NAMESPACE'); docs=read('man/institutional_governance.Rd')+'\n'+read('man/export_institutional_governance.Rd')
    apis=('institutional_role','governance_actor','institutional_template','restricted_access_policy','institutional_governance_workflow','validate_institutional_governance','assign_institutional_review','add_review_comment','submit_change_request','resolve_change_request','record_governance_approval','sign_analytical_release','archive_governance_workflow','apply_governance_to_project','governance_audit_log','governance_summary','governance_to_json','governance_from_json','export_institutional_governance','workspace_add_institutional_governance','workspace_get_institutional_governance')
    for name in apis:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'Governance API documentation missing: {name}')
    readiness=read('R/production_readiness.R')
    for token in ('institutional_governance = "1.0.0"','institutional_governance_export = "1.0.0"','version = "1.6.0"','version = "2.6.0"'):
        if token not in readiness: fail(f'Production contract missing: {token}')
    for path in sorted((ROOT/'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    json_files=sorted(ROOT.rglob('*.json'))
    for path in json_files: json.loads(path.read_text(encoding='utf-8'))
    pairs=[('schemas/catalyst_analytics_r_institutional_governance.schema.json','examples/institutional_governance_input.json'),('schemas/catalyst_analytics_r_institutional_governance_export.schema.json','outputs/example_institutional_governance_export.json'),('schemas/catalyst_analytics_r_institutional_governance_demo_export.schema.json','outputs/example_browser_institutional_governance_export.json'),('schemas/catalyst_analytics_r_platform_handoff.schema.json','outputs/example_platform_handoff.json'),('schemas/catalyst_analytics_r_policy_evaluation.schema.json','outputs/example_policy_evaluation_export.json')]
    for schema,payload in pairs: validator(schema).validate(load(payload))
    php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.6\.0$',php,re.M): fail('Plugin version mismatch')
    for token in ('Collaborative review and institutional governance','Build governance preview','Governance boundary','aria-live="polite"'):
        if token not in php: fail(f'Plugin UI missing: {token}')
    for token in ("compatible_repository_version:'1.6.0'",'mapped_institutional_governance_contract_not_r_execution','identity_not_verified:true','automated_publication:false'):
        if token not in js: fail(f'Browser governance contract missing: {token}')
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
    print('Catalyst Analytics R v1.6.0 release contract passed.')
    print(f'Validated {len(json_files)} JSON files, institutional governance, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0
if __name__=='__main__': raise SystemExit(main())
