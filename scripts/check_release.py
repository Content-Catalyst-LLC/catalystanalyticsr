#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v1.1.0."""
from __future__ import annotations
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.dont_write_bytecode = True
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_VERSION = '1.1.0'
PLUGIN_VERSION = '2.1.0'
MANIFEST_VERSION = '2.1.0'

def fail(message): raise AssertionError(message)
def read(path): return (ROOT / path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
    schema = load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
    env = dict(os.environ); env['PYTHONDONTWRITEBYTECODE'] = '1'; subprocess.run(command, cwd=ROOT, check=True, env=env)

def main():
    if not re.search(r'^Version:\s*1\.1\.0$', read('DESCRIPTION'), re.M): fail('DESCRIPTION version mismatch')
    manifest = load('catalyst_analytics_r_manifest.json')
    if manifest['schema_version'] != MANIFEST_VERSION or manifest['repository_version'] != REPOSITORY_VERSION or manifest['r_package']['version'] != REPOSITORY_VERSION: fail('Manifest version mismatch')
    if manifest['wordpress_demo']['version'] != PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version'] != REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
    for name in ('workspace', 'workspace_export', 'workspace_browser_export'):
        if manifest['contracts'][name]['version'] != '1.0.0': fail(f'{name} contract mismatch')
    required = [
        'R/workspaces.R', 'man/workspaces.Rd',
        'schemas/catalyst_analytics_r_workspace.schema.json',
        'schemas/catalyst_analytics_r_workspace_export.schema.json',
        'schemas/catalyst_analytics_r_workspace_demo_export.schema.json',
        'examples/workspace_input.json', 'outputs/example_workspace_export.json',
        'outputs/example_browser_workspace_export.json', 'tests/fixtures/workspace_contract_v1.json',
        'tests/testthat/helper-workspaces.R', 'tests/testthat/test-workspaces.R',
        'tests/testthat/test-workspace-export.R',
        'docs/saved-workspaces-and-scenario-libraries.md',
        'docs/migration-v1.0-to-v1.1.md', 'docs/releases/v1.1.0.md',
        f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip'
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing: fail(f'Missing v1.1.0 files: {missing}')
    source = read('R/workspaces.R')
    for token in ('persistent_analytical_workspace', 'workspace_clone_scenario', 'workspace_restore_snapshot', 'policy_packages', 'run-history.csv', 'all_bundle_files_except_manifest'):
        if token not in source: fail(f'Workspace implementation missing: {token}')
    for token in ('workspace["active_project_id"] <- list(next_project_id)', 'workspace["active_project_id"] <- list(NULL)', 'run["result"] <- list(NULL)'):
        if token not in source and token not in read('R/reproducible_projects.R'):
            fail(f'Workspace nullable-field repair missing: {token}')
    for token in ('.restored_workspace_fingerprint', 'semantic_change = FALSE', 'state[[".restored_workspace_fingerprint"]] <- NULL', 'record$workspace_fingerprint'):
        if token not in source:
            fail(f'Workspace snapshot identity repair missing: {token}')
    workspace_tests = read('tests/testthat/test-workspaces.R')
    export_tests = read('tests/testthat/test-workspace-export.R')
    for token in ('active_project_id" %in% names(changed)', 'active_project_id", exact = TRUE', 'empty workspace JSON round trip preserves nullable active project'):
        if token not in workspace_tests: fail(f'Workspace null regression test missing: {token}')
    for token in ('workspace snapshot identity survives JSON round trips', 'semantic workspace changes clear restored fingerprint identity', '.restored_workspace_fingerprint'):
        if token not in workspace_tests: fail(f'Workspace snapshot fingerprint regression test missing: {token}')
    for token in ('"result" %in% names(run)', '"result", exact = TRUE'):
        if token not in export_tests: fail(f'Workspace result-null regression test missing: {token}')
    namespace = read('NAMESPACE')
    workspace_exports = (
        'catalyst_workspace','validate_catalyst_workspace','workspace_add_project','workspace_get_project',
        'workspace_remove_project','workspace_set_active_project','workspace_add_scenario','workspace_get_scenario',
        'workspace_clone_scenario','workspace_add_parameter_set','workspace_get_parameter_set',
        'workspace_add_policy_package','workspace_list_scenarios','workspace_run_history',
        'workspace_compare_projects','workspace_fingerprint','workspace_snapshot',
        'workspace_restore_snapshot','workspace_manifest','workspace_to_json','workspace_from_json','export_workspace'
    )
    docs = read('man/workspaces.Rd')
    for name in workspace_exports:
        if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in docs: fail(f'Workspace API documentation missing: {name}')
    if 'S3method(print,catalyst_workspace)' not in namespace: fail('Workspace print method is not registered')
    production = read('R/production_readiness.R')
    for token in ('workspaces = c(', 'workspace = "1.0.0"', 'workspace_export = "1.0.0"', 'version = "1.1.0"', 'version = "2.1.0"'):
        if token not in production: fail(f'Stable API/compatibility contract missing: {token}')
    for path in sorted((ROOT / 'R').glob('*.R')):
        try: path.read_bytes().decode('ascii')
        except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
    for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
    validator('schemas/catalyst_analytics_r_workspace.schema.json').validate(load('examples/workspace_input.json'))
    validator('schemas/catalyst_analytics_r_workspace_export.schema.json').validate(load('outputs/example_workspace_export.json')['export_manifest'])
    validator('schemas/catalyst_analytics_r_workspace_demo_export.schema.json').validate(load('outputs/example_browser_workspace_export.json'))
    prior = [
        ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
        ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
        ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
        ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
        ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
        ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),
        ('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),
        ('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json')
    ]
    for schema, payload in prior: validator(schema).validate(load(payload))
    php = read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php')
    js = read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js')
    css = read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
    if not re.search(r'^ \* Version:\s*2\.1\.0$', php, re.M): fail('Plugin version mismatch')
    for token in ('Saved workspace and scenario library', 'Clone transition scenario', 'Create snapshot', 'aria-live="polite"'):
        if token not in php: fail(f'Plugin workspace UI missing: {token}')
    for token in ("compatible_repository_version: '1.1.0'", 'browser_saved_workspace_and_scenario_library', 'mapped_workspace_contract_not_r_execution', 'policy_packages', 'workspace_manifest'):
        if token not in js: fail(f'Browser workspace contract missing: {token}')
    if ':focus-visible' not in css: fail('Focus visibility contract missing')
    with zipfile.ZipFile(ROOT / f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
        if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
    exports = re.findall(r'^export\(([^)]+)\)$', namespace, re.M)
    aliases = '\n'.join(path.read_text(encoding='utf-8') for path in (ROOT / 'man').glob('*.Rd'))
    missing_alias = [name for name in exports if f'\\alias{{{name}}}' not in aliases]
    if missing_alias: fail(f'Exported functions missing Rd aliases: {missing_alias}')
    run([sys.executable, 'scripts/check_r_structure.py'])
    run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests_py'])
    if subprocess.run(['bash','-lc','command -v node >/dev/null'], cwd=ROOT).returncode == 0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
    if subprocess.run(['bash','-lc','command -v php >/dev/null'], cwd=ROOT).returncode == 0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
    debris = [p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
    if debris: fail(f'Generated debris remains: {debris}')
    print('Catalyst Analytics R v1.1.0 release contract passed.')
    print(f'Validated {len(list(ROOT.rglob("*.json")))} JSON files, workspace contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
