from __future__ import annotations
import importlib.util, json, re, zipfile
from pathlib import Path
import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT / path).read_text(encoding='utf-8'))
def validator(path):
    schema = load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)

def test_description_version(): assert re.search(r'^Version:\s*1\.1\.0$', (ROOT/'DESCRIPTION').read_text(), re.M)
def test_manifest_versions():
    m=load('catalyst_analytics_r_manifest.json'); assert m['schema_version']=='2.1.0'; assert m['repository_version']=='1.1.0'; assert m['r_package']['version']=='1.1.0'; assert m['wordpress_demo']['version']=='2.1.0'; assert m['wordpress_demo']['compatible_repository_version']=='1.1.0'
def test_workspace_contract_versions():
    c=load('catalyst_analytics_r_manifest.json')['contracts']
    for name in ('workspace','workspace_export','workspace_browser_export'): assert c[name]['version']=='1.0.0'
def test_prior_project_contract_versions():
    c=load('catalyst_analytics_r_manifest.json')['contracts']
    for name in ('project','analytical_publication','project_handoff','release_readiness'): assert c[name]['version']=='1.0.0'
def test_workspace_schema_validates_example(): validator('schemas/catalyst_analytics_r_workspace.schema.json').validate(load('examples/workspace_input.json'))
def test_workspace_export_schema_validates_manifest(): validator('schemas/catalyst_analytics_r_workspace_export.schema.json').validate(load('outputs/example_workspace_export.json')['export_manifest'])
def test_browser_workspace_schema_validates(): validator('schemas/catalyst_analytics_r_workspace_demo_export.schema.json').validate(load('outputs/example_browser_workspace_export.json'))
def test_workspace_has_projects_and_libraries():
    w=load('examples/workspace_input.json'); assert w['active_project_id'] in w['projects']; assert w['libraries']['scenarios']; assert w['libraries']['parameter_sets']; assert w['libraries']['policy_packages']
def test_workspace_library_references_resolve():
    w=load('examples/workspace_input.json'); package=next(iter(w['libraries']['policy_packages'].values())); assert set(package['scenario_ids']).issubset(w['libraries']['scenarios']); assert set(package['parameter_set_ids']).issubset(w['libraries']['parameter_sets'])
def test_workspace_fingerprints():
    out=load('outputs/example_workspace_export.json'); assert re.fullmatch(r'[a-f0-9]{32}',out['workspace_manifest']['fingerprint']); assert re.fullmatch(r'[a-f0-9]{32}',out['export_manifest']['workspace_fingerprint'])
def test_workspace_export_integrity():
    m=load('outputs/example_workspace_export.json')['export_manifest']; assert m['file_count']==len(m['files']); assert m['integrity']['complete'] is True; assert all(re.fullmatch(r'[a-f0-9]{32}',x['md5']) for x in m['files'])
def test_workspace_snapshot_present():
    w=load('examples/workspace_input.json'); assert w['snapshots']; assert re.fullmatch(r'[a-f0-9]{32}',w['snapshots'][0]['workspace_fingerprint'])
def test_workspace_contract_fixture():
    f=load('tests/fixtures/workspace_contract_v1.json'); assert f['repository_version']=='1.1.0'; assert 'snapshot_restore' in f['capabilities']
def test_namespace_workspace_exports():
    text=(ROOT/'NAMESPACE').read_text()
    names=('catalyst_workspace','validate_catalyst_workspace','workspace_add_project','workspace_get_project','workspace_remove_project','workspace_set_active_project','workspace_add_scenario','workspace_get_scenario','workspace_clone_scenario','workspace_add_parameter_set','workspace_get_parameter_set','workspace_add_policy_package','workspace_list_scenarios','workspace_run_history','workspace_compare_projects','workspace_fingerprint','workspace_snapshot','workspace_restore_snapshot','workspace_manifest','workspace_to_json','workspace_from_json','export_workspace')
    for name in names: assert f'export({name})' in text
def test_workspace_s3_registered(): assert 'S3method(print,catalyst_workspace)' in (ROOT/'NAMESPACE').read_text()
def test_workspace_implementation_tokens():
    text=(ROOT/'R/workspaces.R').read_text()
    for token in ('persistent_analytical_workspace','workspace_clone_scenario','workspace_restore_snapshot','policy_packages','run-history.csv','all_bundle_files_except_manifest'): assert token in text
def test_workspace_documentation_aliases():
    text=(ROOT/'man/workspaces.Rd').read_text()
    for name in ('catalyst_workspace','workspace_add_project','workspace_clone_scenario','workspace_snapshot','workspace_restore_snapshot','export_workspace'): assert f'\\alias{{{name}}}' in text
def test_workspace_r_tests_present():
    for path in ('tests/testthat/helper-workspaces.R','tests/testthat/test-workspaces.R','tests/testthat/test-workspace-export.R'): assert (ROOT/path).exists()
def test_stable_api_contains_workspace():
    text=(ROOT/'R/production_readiness.R').read_text(); assert 'workspaces = c(' in text; assert 'workspace = "1.0.0"' in text; assert 'version = "1.1.0"' in text
def test_plugin_version(): assert re.search(r'^ \* Version:\s*2\.1\.0$',(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(),re.M)
def test_plugin_workspace_interface():
    php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); assert 'Saved workspace and scenario library' in php; assert 'Clone transition scenario' in php; assert 'Create snapshot' in php
def test_plugin_contract_tokens():
    js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text()
    for token in ('browser_saved_workspace_and_scenario_library','mapped_workspace_contract_not_r_execution',"compatible_repository_version: '1.1.0'",'policy_packages','workspace_manifest'): assert token in js
def test_plugin_accessibility():
    php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); css=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css').read_text(); assert 'aria-live="polite"' in php; assert ':focus-visible' in css
def test_plugin_zip_integrity():
    path=ROOT/'dist/catalyst-analytics-r-demo-v2.1.0.zip'; assert path.exists()
    with zipfile.ZipFile(path) as z: assert z.testzip() is None; assert 'catalyst-analytics-r-demo/catalyst-analytics-r-demo.php' in z.namelist()
def test_release_docs(): assert 'Saved Workspaces and Scenario Libraries' in (ROOT/'docs/releases/v1.1.0.md').read_text()
def test_workspace_methodology_docs(): assert 'workspace_restore_snapshot' in (ROOT/'docs/saved-workspaces-and-scenario-libraries.md').read_text()
def test_migration_docs(): assert 'additive' in (ROOT/'docs/migration-v1.0-to-v1.1.md').read_text().lower()
def test_readme_current_versions():
    text=(ROOT/'README.md').read_text(); assert '**Current release:** `1.1.0`' in text; assert '**WordPress companion:** `2.1.0`' in text
def test_description_mentions_workspaces(): assert 'persistent multi-project workspaces' in (ROOT/'DESCRIPTION').read_text().lower()
def test_buildignore_layers():
    text=(ROOT/'.Rbuildignore').read_text(); assert '^wordpress$' in text and '^tests_py$' in text and '^schemas$' in text and '^outputs$' in text
@pytest.mark.parametrize('schema,payload',[
 ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
 ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
 ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
 ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
 ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
 ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),
 ('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),
 ('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json')])
def test_prior_contracts(schema,payload): validator(schema).validate(load(payload))
def test_project_publication_still_valid(): validator('schemas/catalyst_analytics_r_publication.schema.json').validate(load('outputs/example_project_publication_export.json')['publication_manifest'])
def test_release_readiness_fixture():
    validator('schemas/catalyst_analytics_r_release_readiness.schema.json').validate(load('outputs/example_release_readiness.json')); assert load('outputs/example_release_readiness.json')['package_version']=='1.1.0'
def test_all_manifest_fixtures_resolve(): assert all((ROOT/path).exists() for path in load('catalyst_analytics_r_manifest.json')['fixtures'].values())
def test_no_stale_package_expectations():
    for p in (ROOT/'tests/testthat').glob('*.R'): assert 'manifest$package$version, "1.0.0"' not in p.read_text(); assert 'manifest$package_version, "1.0.0"' not in p.read_text()
def test_no_non_ascii_r_source():
    for path in (ROOT/'R').glob('*.R'): path.read_bytes().decode('ascii')
def test_no_generated_debris(): assert not any(p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck') for p in ROOT.rglob('*'))
def test_all_json_parses():
    for path in ROOT.rglob('*.json'): json.loads(path.read_text(encoding='utf-8'))
def test_python_brief_prior_support():
    path=ROOT/'python/catalyst_analytics_brief.py'; spec=importlib.util.spec_from_file_location('brief',path); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); assert 'Project Publication Brief' in module.brief(load('outputs/example_project_publication_export.json'))
