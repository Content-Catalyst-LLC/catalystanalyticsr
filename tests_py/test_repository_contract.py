from __future__ import annotations
import importlib.util, json, math, re
from pathlib import Path
import jsonschema, pytest
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def validator(path):
 schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)

def test_description_version(): assert re.search(r'^Version: 0\.8\.0$',(ROOT/'DESCRIPTION').read_text(),re.M)
def test_manifest_version(): assert load('catalyst_analytics_r_manifest.json')['repository_version']=='0.8.0'
def test_package_manifest_version(): assert load('catalyst_analytics_r_manifest.json')['r_package']['version']=='0.8.0'
def test_plugin_version(): assert ' * Version: 1.7.0' in (ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text()
def test_manifest_compatibility(): assert load('catalyst_analytics_r_manifest.json')['wordpress_demo']['compatible_repository_version']=='0.8.0'
def test_manifest_schema_version(): assert load('catalyst_analytics_r_manifest.json')['schema_version']=='1.7.0'
@pytest.mark.parametrize('contract',['calibration','model_validation','model_governance'])
def test_new_contract_versions(contract): assert load('catalyst_analytics_r_manifest.json')['contracts'][contract]['version']=='1.0.0'
def test_browser_contract_version(): assert load('catalyst_analytics_r_manifest.json')['contracts']['browser_export']['version']=='1.7.0'

def test_model_validation_export_validates(): validator('schemas/catalyst_analytics_r_model_validation.schema.json').validate(load('outputs/example_model_validation_export.json'))
def test_calibration_export_validates(): validator('schemas/catalyst_analytics_r_calibration.schema.json').validate(load('outputs/example_model_validation_export.json')['calibration'])
def test_governance_export_validates(): validator('schemas/catalyst_analytics_r_model_governance.schema.json').validate(load('outputs/example_model_validation_export.json')['governance'])
def test_browser_export_validates(): validator('schemas/catalyst_analytics_r_governance_demo_export.schema.json').validate(load('outputs/example_browser_governance_export.json'))

def test_calibration_parameter_is_bounded():
 p=load('outputs/example_model_validation_export.json')['calibration']['parameters'][0]; assert p['lower'] <= p['estimate'] <= p['upper']
def test_calibration_moved_parameter():
 p=load('outputs/example_model_validation_export.json')['calibration']['parameters'][0]; assert p['estimate'] != p['initial']
def test_calibration_converged(): assert load('outputs/example_model_validation_export.json')['calibration']['convergence']['code']==0
def test_fitted_residuals_reconcile():
 for row in load('outputs/example_model_validation_export.json')['calibration']['fitted']: assert math.isclose(row['residual'],row['observed']-row['predicted'],abs_tol=1e-12)
def test_calibration_and_holdout_present(): assert {'calibration','holdout'}=={r['split'] for r in load('outputs/example_model_validation_export.json')['calibration']['fitted']}
def test_metrics_recalculate():
 p=load('outputs/example_model_validation_export.json')
 for m in p['validation']['metrics']:
  rows=[r for r in p['calibration']['fitted'] if r['split']==m['split'] and r['metric']==m['metric']]
  residual=[r['residual'] for r in rows]
  assert math.isclose(m['rmse'],math.sqrt(sum(x*x for x in residual)/len(residual)),abs_tol=1e-12)
  assert math.isclose(m['mae'],sum(abs(x) for x in residual)/len(residual),abs_tol=1e-12)
def test_validation_checks_pass(): assert all(r['passed'] for r in load('outputs/example_model_validation_export.json')['validation']['checks'])
def test_validation_status_passed(): assert load('outputs/example_model_validation_export.json')['validation']['status']=='passed'
def test_residual_diagnostics_present():
 d=load('outputs/example_model_validation_export.json')['validation']['residual_diagnostics']; assert len(d)==2 and all('lag1_autocorrelation' in x for x in d)
def test_solver_reference_present(): assert load('outputs/example_model_validation_export.json')['solver_benchmark']['reference']=={'method':'rk4','step':0.25}
def test_solver_cases(): assert len(load('outputs/example_model_validation_export.json')['solver_benchmark']['summary'])==4
def test_solver_cases_succeed(): assert all(r['success'] for r in load('outputs/example_model_validation_export.json')['solver_benchmark']['summary'])
def test_solver_error_increases_for_coarse_euler():
 rows=load('outputs/example_model_validation_export.json')['solver_benchmark']['summary']; rk4=min(r['max_absolute_terminal_error'] for r in rows if r['method']=='rk4'); euler=max(r['max_absolute_terminal_error'] for r in rows if r['method']=='euler'); assert euler>rk4
def test_stability_passed(): assert load('outputs/example_model_validation_export.json')['stability_assessment']['stable'] is True
def test_invariants_passed(): assert all(r['passed'] for r in load('outputs/example_model_validation_export.json')['stability_assessment']['invariants'])
def test_boundary_conditions_passed(): assert all(r['passed'] for r in load('outputs/example_model_validation_export.json')['stability_assessment']['boundary_conditions'])
def test_governance_lifecycle(): assert load('outputs/example_model_validation_export.json')['governance']['lifecycle_status']=='validated_for_specified_use'
def test_governance_has_evidence():
 e=load('outputs/example_model_validation_export.json')['governance']['model_card']['evidence']; assert e['calibration'] and e['validation']
def test_model_card_has_use_boundaries():
 c=load('outputs/example_model_validation_export.json')['governance']['model_card']; assert c['intended_uses'] and c['prohibited_uses']
def test_parameter_cards_present(): assert len(load('outputs/example_model_validation_export.json')['governance']['model_card']['parameters'])>=1
def test_assumptions_present(): assert len(load('outputs/example_model_validation_export.json')['governance']['model_card']['assumptions'])>=1
def test_limitations_present(): assert len(load('outputs/example_model_validation_export.json')['governance']['model_card']['limitations'])>=2
def test_high_severity_limitation_present(): assert any(x['severity']=='high' for x in load('outputs/example_model_validation_export.json')['governance']['model_card']['limitations'])
def test_approval_present(): assert load('outputs/example_model_validation_export.json')['governance']['approvals']
def test_transition_history_order():
 h=load('outputs/example_model_validation_export.json')['governance']['transition_history']; assert [x['to'] for x in h]==['experimental','under_review','validated_for_specified_use']
def test_review_boundary_complete(): assert all(load('outputs/example_model_validation_export.json')['review_boundary'].values())
def test_fixture_matches_summary():
 f=load('tests/fixtures/model_validation_contract_v1.json'); s=load('outputs/example_model_validation_export.json')['summary'][0]; assert s['validation_status']==f['expected_validation_status'] and s['lifecycle_status']==f['expected_lifecycle_status']
def test_holdout_below_fixture_limit():
 f=load('tests/fixtures/model_validation_contract_v1.json'); assert load('outputs/example_model_validation_export.json')['summary'][0]['holdout_rmse']<=f['maximum_holdout_rmse']
def test_csv_fixture_rows(): assert (ROOT/'inst/extdata/governance/sample_historical_observations.csv').read_text().count('\n')==11
def test_source_fixture_license(): assert load('inst/extdata/governance/sample_historical_observations_source.json')['license']=='CC0-1.0'

def test_namespace_exports():
 text=(ROOT/'NAMESPACE').read_text()
 for name in ('calibration_spec','calibrate_model','calibration_summary','validation_split','model_error_metrics','residual_diagnostics','validate_model_fit','solver_benchmark','stability_assessment','parameter_card','assumption_record','limitation_record','model_card','model_governance_record','transition_model_status','model_validation_analysis','model_validation_summary','export_model_validation'): assert f'export({name})' in text
def test_s3_methods_registered():
 text=(ROOT/'NAMESPACE').read_text()
 for cls in ('catalyst_calibration','catalyst_model_validation','catalyst_model_card','catalyst_model_governance','catalyst_model_validation_analysis'): assert f'S3method(print,{cls})' in text
def test_no_non_ascii_r_source():
 for path in (ROOT/'R').glob('*.R'): path.read_bytes().decode('ascii')
def test_no_placeholder_tests(): assert 'multiplication works' not in '\n'.join(p.read_text() for p in (ROOT/'tests/testthat').glob('*.R'))
def test_plugin_has_governance_interface():
 php=(ROOT/'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php').read_text(); assert 'Calibration, validation, and model governance' in php and 'Run calibration and validation' in php
def test_plugin_has_contract_tokens():
 js=(ROOT/'wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js').read_text()
 for token in ('browser_model_validation_governance','mapped_governance_contract_not_numerical_parity',"compatible_repository_version: '0.8.0'",'calibration_contract_version','validation_contract_version','governance_contract_version','validated_for_specified_use','limitations'): assert token in js
def test_python_brief_supports_validation_export():
 path=ROOT/'python/catalyst_analytics_brief.py'; spec=importlib.util.spec_from_file_location('brief',path); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); text=module.brief(load('outputs/example_model_validation_export.json')); assert '# Catalyst Analytics R Model Validation Brief' in text and 'Known limitations' in text
@pytest.mark.parametrize('schema,payload',[
 ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
 ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
 ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
 ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
 ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
 ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json')])
def test_prior_contracts(schema,payload): validator(schema).validate(load(payload))
def test_manifest_fixtures_resolve(): assert all((ROOT/path).exists() for path in load('catalyst_analytics_r_manifest.json')['fixtures'].values())
def test_release_docs_present(): assert '0.8.0' in (ROOT/'docs/releases/v0.8.0.md').read_text()
def test_methodology_docs_present(): assert 'validated_for_specified_use' in (ROOT/'docs/calibration-validation-model-governance.md').read_text()
def test_package_description_mentions_calibration(): assert 'calibration' in (ROOT/'DESCRIPTION').read_text().lower()
def test_buildignore_excludes_repository_layers():
 text=(ROOT/'.Rbuildignore').read_text(); assert '^wordpress$' in text and '^tests_py$' in text and '^schemas$' in text
def test_all_json_parses():
 for path in ROOT.rglob('*.json'): json.loads(path.read_text(encoding='utf-8'))


def test_json_fallback_is_non_throwing_and_class_aware():
 text=(ROOT/'R/validation_internal.R').read_text()
 assert 'sprintf("<unsupported:%s:%s>", typeof(x), class_label)' in text
 assert 'suppressWarnings(as.character(x))' in text
 assert 'error = function(error) character()' in text
 assert 'as.character(x)\n}' not in text

def test_json_safety_has_unsupported_object_regression():
 text=(ROOT/'tests/testthat/test-model-validation-json-safety.R').read_text()
 assert 'unsupported objects use a plain JSON-safe descriptor' in text
 assert 'catalyst_json_s4_probe' in text
