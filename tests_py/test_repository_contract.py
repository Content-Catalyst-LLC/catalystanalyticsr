from __future__ import annotations
import importlib.util, json, math, re, zipfile
from pathlib import Path
import jsonschema
import pytest

ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def validator(path):
 schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)

def test_description_version(): assert re.search(r'^Version:\s*0\.9\.0$',(ROOT/'DESCRIPTION').read_text(),re.M)
def test_manifest_versions():
 m=load('catalyst_analytics_r_manifest.json'); assert m['schema_version']=='1.8.0'; assert m['repository_version']=='0.9.0'; assert m['r_package']['version']=='0.9.0'; assert m['wordpress_demo']['version']=='1.8.0'; assert m['wordpress_demo']['compatible_repository_version']=='0.9.0'
def test_new_contract_versions():
 c=load('catalyst_analytics_r_manifest.json')['contracts']
 for name in ('project','analytical_publication','project_handoff'): assert c[name]['version']=='1.0.0'
def test_project_schema_validates_example(): validator('schemas/catalyst_analytics_r_project.schema.json').validate(load('examples/project_input.json'))
def test_publication_schema_validates_manifest(): validator('schemas/catalyst_analytics_r_publication.schema.json').validate(load('outputs/example_project_publication_export.json')['publication_manifest'])
def test_handoff_schema_validates_decision(): validator('schemas/catalyst_analytics_r_project_handoff.schema.json').validate(load('outputs/example_project_publication_export.json')['handoffs']['decision_studio'])
def test_handoff_schema_validates_knowledge(): validator('schemas/catalyst_analytics_r_project_handoff.schema.json').validate(load('outputs/example_project_publication_export.json')['handoffs']['knowledge_library'])
def test_browser_project_export_validates(): validator('schemas/catalyst_analytics_r_project_demo_export.schema.json').validate(load('outputs/example_browser_project_publication_export.json'))
def test_project_run_hashes():
 p=load('examples/project_input.json'); run=p['runs']['baseline-run']; assert re.fullmatch(r'[a-f0-9]{32}',run['input_hash']); assert re.fullmatch(r'[a-f0-9]{32}',run['output_hash'])
def test_project_environment_present():
 e=load('examples/project_input.json')['environment']; assert e['schema_version']=='1.0.0'; assert e['r']['version']; assert e['operating_system']; assert e['packages']
def test_project_review_and_snapshot():
 p=load('examples/project_input.json'); assert p['metadata']['review_status']=='approved'; assert p['reviews'][0]['decision']=='approved'; assert re.fullmatch(r'[a-f0-9]{32}',p['snapshots'][0]['project_fingerprint'])
def test_project_records_model_version():
 p=load('examples/project_input.json'); assert 'khncpa@1.0.0' in p['models']; assert p['runs']['baseline-run']['model']=={'id':'khncpa','version':'1.0.0'}
def test_publication_formats_complete():
 m=load('outputs/example_project_publication_export.json')['publication_manifest']; assert set(('json','csv','markdown','html','quarto')).issubset(m['formats'])
def test_publication_integrity_records():
 m=load('outputs/example_project_publication_export.json')['publication_manifest']; assert m['integrity']['complete'] is True; assert all(re.fullmatch(r'[a-f0-9]{32}',x['md5']) for x in m['files'])
def test_decision_handoff_boundary(): assert load('outputs/example_project_publication_export.json')['handoffs']['decision_studio']['decision_boundary']['human_decision_required'] is True
def test_knowledge_handoff_boundary(): assert load('outputs/example_project_publication_export.json')['handoffs']['knowledge_library']['publication_boundary']['limitations_require_prominent_disclosure'] is True
def test_browser_contract_boundary():
 p=load('outputs/example_browser_project_publication_export.json'); assert p['contract']['parity_status']=='mapped_project_contract_not_r_execution'; assert p['review_boundary']['r_not_executed'] is True
def test_browser_has_two_runs(): assert len(load('outputs/example_browser_project_publication_export.json')['run_index'])==2
def test_fixture_expectations():
 f=load('tests/fixtures/project_publication_contract_v1.json'); p=load('outputs/example_project_publication_export.json'); assert p['project']['id']==f['project_id']; assert p['publication_manifest']['package']['version']==f['expected_package_version']; assert len(p['project']['runs'])==f['expected_run_count']; assert p['project']['metadata']['review_status']==f['expected_review_status']
def test_namespace_exports():
 text=(ROOT/'NAMESPACE').read_text()
 for name in ('capture_project_environment','catalyst_project','validate_catalyst_project','project_add_scenario','project_add_dataset','project_add_model','project_add_parameter_set','project_add_run','project_add_indicator','project_add_plot','project_add_note','project_add_review','project_snapshot','project_fingerprint','project_summary','project_manifest','project_to_json','project_from_json','decision_studio_handoff','knowledge_library_handoff','export_project_publication'): assert f'export({name})' in text
def test_s3_methods_registered():
 text=(ROOT/'NAMESPACE').read_text(); assert 'S3method(print,catalyst_project)' in text; assert 'S3method(print,catalyst_project_run)' in text
def test_project_r_implementations_present():
 text=(ROOT/'R/reproducible_projects.R').read_text()+(ROOT/'R/project_publication.R').read_text()
 for token in ('input_hash','output_hash','capture_project_environment','analytical-publication.qmd','decision-studio-handoff.json','knowledge-library-methodology.json','reproducible_not_necessarily_valid'): assert token in text
def test_r_docs_aliases_present():
 aliases='\n'.join(p.read_text() for p in (ROOT/'man').glob('*.Rd'))
 for name in ('catalyst_project','project_add_run','project_snapshot','project_manifest','export_project_publication','decision_studio_handoff','knowledge_library_handoff'): assert f'\\alias{{{name}}}' in aliases
def test_project_test_files_present():
 for path in ('tests/testthat/helper-projects.R','tests/testthat/test-reproducible-projects.R','tests/testthat/test-project-publication.R'): assert (ROOT/path).exists()
def test_plugin_version(): assert re.search(r'^ \* Version:\s*1\.8\.0$',(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(),re.M)
def test_plugin_project_interface():
 php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); assert 'Reproducible project and publication studio' in php; assert 'Build project record' in php; assert 'Platform handoffs' in php
def test_plugin_contract_tokens():
 js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text()
 for token in ('browser_reproducible_project_publication','mapped_project_contract_not_r_execution',"compatible_repository_version: '0.9.0'",'project_contract_version','publication_contract_version','decision_studio_analytical_project','knowledge_library_methodology_package'): assert token in js
def test_plugin_zip_integrity():
 path=ROOT/'dist/catalyst-analytics-r-demo-v1.8.0.zip'; assert path.exists()
 with zipfile.ZipFile(path) as z: assert z.testzip() is None; assert 'catalyst-analytics-r-demo/catalyst-analytics-r-demo.php' in z.namelist()
def test_python_brief_supports_project_export():
 path=ROOT/'python/catalyst_analytics_brief.py'; spec=importlib.util.spec_from_file_location('brief',path); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); text=module.brief(load('outputs/example_project_publication_export.json')); assert '# Catalyst Analytics R Project Publication Brief' in text and 'Reproducibility record' in text
def test_release_docs(): assert 'Reproducible Projects and Analytical Publication' in (ROOT/'docs/releases/v0.9.0.md').read_text()
def test_methodology_docs(): assert 'Decision Studio' in (ROOT/'docs/reproducible-projects-analytical-publication.md').read_text()
def test_description_mentions_projects(): assert 'reproducible analytical projects' in (ROOT/'DESCRIPTION').read_text().lower()
def test_buildignore_layers():
 text=(ROOT/'.Rbuildignore').read_text(); assert '^wordpress$' in text and '^tests_py$' in text and '^schemas$' in text and '^outputs$' in text
@pytest.mark.parametrize('schema,payload',[
 ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
 ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
 ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
 ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
 ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
 ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),
 ('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json')])
def test_prior_contracts(schema,payload): validator(schema).validate(load(payload))
def test_prior_calibration_contract(): validator('schemas/catalyst_analytics_r_calibration.schema.json').validate(load('outputs/example_model_validation_export.json')['calibration'])
def test_prior_governance_contract(): validator('schemas/catalyst_analytics_r_model_governance.schema.json').validate(load('outputs/example_model_validation_export.json')['governance'])
def test_all_manifest_fixtures_resolve(): assert all((ROOT/path).exists() for path in load('catalyst_analytics_r_manifest.json')['fixtures'].values())
def test_no_stale_package_expectations():
 for p in (ROOT/'tests/testthat').glob('*.R'): assert '"0.7.0"' not in p.read_text(); assert '"0.8.0"' not in p.read_text()
def test_no_non_ascii_r_source():
 for path in (ROOT/'R').glob('*.R'): path.read_bytes().decode('ascii')
def test_no_generated_debris():
 assert not any(p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck') for p in ROOT.rglob('*'))
def test_all_json_parses():
 for path in ROOT.rglob('*.json'): json.loads(path.read_text(encoding='utf-8'))
