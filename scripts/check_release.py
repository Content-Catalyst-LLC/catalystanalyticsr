#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.8.0."""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='0.8.0'; PLUGIN_VERSION='1.7.0'; MANIFEST_VERSION='1.7.0'
NEW_CONTRACTS=('calibration','model_validation','model_governance')
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
 schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
 env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def documented_exports():
 exports=re.findall(r'^export\(([^)]+)\)$',read('NAMESPACE'),re.M)
 aliases='\n'.join(path.read_text(encoding='utf-8') for path in (ROOT/'man').glob('*.Rd'))
 missing=[name for name in exports if f'\\alias{{{name}}}' not in aliases]
 if missing: fail(f'Exported functions missing Rd aliases: {missing}')
def main():
 description=read('DESCRIPTION'); match=re.search(r'^Version:\s*(\S+)$',description,re.M)
 if not match or match.group(1)!=REPOSITORY_VERSION: fail('DESCRIPTION version mismatch')
 manifest=load('catalyst_analytics_r_manifest.json')
 if manifest['schema_version']!=MANIFEST_VERSION: fail('Manifest schema mismatch')
 if manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Repository version mismatch')
 if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
 if manifest['contracts']['browser_export']['version']!=PLUGIN_VERSION: fail('Browser export contract mismatch')
 for name in NEW_CONTRACTS:
  if manifest['contracts'][name]['version']!='1.0.0': fail(f'{name} contract mismatch')
 required=[
  'R/model_calibration.R','R/model_validation.R','R/model_governance.R','R/model_validation_analysis.R','R/export_model_validation.R',
  'man/model_calibration.Rd','man/model_validation.Rd','man/model_governance.Rd','man/model_validation_analysis.Rd','man/export_model_validation.Rd',
  'schemas/catalyst_analytics_r_calibration.schema.json','schemas/catalyst_analytics_r_model_validation.schema.json','schemas/catalyst_analytics_r_model_governance.schema.json','schemas/catalyst_analytics_r_governance_demo_export.schema.json',
  'examples/model_validation_input.json','outputs/example_model_validation_export.json','outputs/example_browser_governance_export.json',
  'inst/extdata/governance/sample_historical_observations.csv','inst/extdata/governance/sample_historical_observations_source.json',
  'tests/fixtures/model_validation_contract_v1.json','tests/testthat/helper-model-validation.R','tests/testthat/test-model-calibration.R','tests/testthat/test-model-validation-governance.R','tests/testthat/test-model-validation-export.R','tests/testthat/test-model-validation-json-safety.R',
  'docs/calibration-validation-model-governance.md','docs/releases/v0.8.0.md',
  'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js',
  'dist/catalyst-analytics-r-demo-v1.7.0.zip'
 ]
 missing=[p for p in required if not (ROOT/p).exists()]
 if missing: fail(f'Missing v0.8.0 release files: {missing}')
 source='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'R').glob('*.R'))
 symbols=('calibration_spec <- function','calibrate_model <- function','calibration_summary <- function','validation_split <- function','model_error_metrics <- function','residual_diagnostics <- function','validate_model_fit <- function','solver_benchmark <- function','stability_assessment <- function','parameter_card <- function','assumption_record <- function','limitation_record <- function','model_card <- function','model_governance_record <- function','transition_model_status <- function','model_validation_analysis <- function','export_model_validation <- function')
 for symbol in symbols:
  if symbol not in source: fail(f'Missing implementation symbol: {symbol}')
 for token in ('weighted_rmse','holdout','r_squared','lag1_autocorrelation','max_absolute_terminal_error','boundary_conditions','validated_for_specified_use','prohibited_uses','transition_history','review_boundary'):
  if token not in source: fail(f'Model-validation implementation incomplete: {token}')
 if 'jsonlite::write_json(.safe_json_value(payload)' not in read('R/export_model_validation.R'): fail('Model-validation JSON writer is not S3 safe')
 safe_json=read('R/validation_internal.R')
 if 'sprintf("<unsupported:%s:%s>", typeof(x), class_label)' not in safe_json: fail('JSON fallback is not class safe')
 if 'suppressWarnings(as.character(x))' not in safe_json or 'error = function(error) character()' not in safe_json: fail('JSON fallback can still throw through as.character')
 if 'as.character(x)\n}' in safe_json: fail('Unsafe terminal as.character fallback remains')
 if 'terminal_values <- vapply(available' not in read('R/model_validation.R'): fail('Solver benchmark does not use explicit scalar extraction')
 if 'baseline_values <- vapply(available' not in read('R/model_validation.R'): fail('Stability assessment does not use explicit scalar extraction')
 calibration_source=read('R/model_calibration.R')
 if '.validate_calibration_targets <- function' not in calibration_source: fail('Calibration target pre-validation is missing')
 if '.validate_calibration_targets(scenario, spec)' not in calibration_source: fail('Calibration targets are not validated before optimization')
 calibration_test=read('tests/testthat/test-model-calibration.R')
 if 'parameters.not_registered' not in calibration_test: fail('Missing unregistered calibration-target regression test')
 stale=[]
 for path in sorted((ROOT/'tests'/'testthat').glob('*.R')):
  if '"0.7.0"' in path.read_text(encoding='utf-8'): stale.append(str(path.relative_to(ROOT)))
 if stale: fail(f'Stale v0.7.0 expectations remain: {stale}')
 for path in sorted((ROOT/'R').glob('*.R')):
  try: path.read_bytes().decode('ascii')
  except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
 for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
 payload=load('outputs/example_model_validation_export.json')
 validator('schemas/catalyst_analytics_r_model_validation.schema.json').validate(payload)
 validator('schemas/catalyst_analytics_r_calibration.schema.json').validate(payload['calibration'])
 validator('schemas/catalyst_analytics_r_model_governance.schema.json').validate(payload['governance'])
 validator('schemas/catalyst_analytics_r_governance_demo_export.schema.json').validate(load('outputs/example_browser_governance_export.json'))
 if payload['validation']['status']!='passed': fail('Validation fixture did not pass')
 if payload['governance']['lifecycle_status']!='validated_for_specified_use': fail('Governance fixture lifecycle mismatch')
 if not payload['governance']['model_card']['evidence']['calibration'] or not payload['governance']['model_card']['evidence']['validation']: fail('Validated fixture lacks evidence')
 if any(not row['passed'] for row in payload['validation']['checks']): fail('Validation checks failed')
 if not payload['stability_assessment']['stable']: fail('Stability fixture failed')
 for row in payload['calibration']['fitted']:
  if abs(row['residual']-(row['observed']-row['predicted']))>1e-12: fail('Residual fixture mismatch')
 prior=[
  ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
  ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
  ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
  ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
  ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
  ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json')]
 for schema,payload_path in prior: validator(schema).validate(load(payload_path))
 php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js')
 if not re.search(r'^ \* Version:\s*1\.7\.0$',php,re.M): fail('Plugin version mismatch')
 for token in ('Calibration, validation, and model governance','Run calibration and validation'):
  if token not in php: fail(f'WordPress interface missing: {token}')
 for token in ('browser_model_validation_governance','mapped_governance_contract_not_numerical_parity',"compatible_repository_version: '0.8.0'",'calibration_contract_version','validation_contract_version','governance_contract_version','validated_for_specified_use','limitations'):
  if token not in js: fail(f'WordPress contract missing: {token}')
 documented_exports()
 run([sys.executable,'scripts/check_r_structure.py'])
 run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
 if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
 if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
 debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
 if debris: fail(f'Generated debris remains: {[str(p.relative_to(ROOT)) for p in debris]}')
 json_count=len(list(ROOT.rglob('*.json')))
 print('Catalyst Analytics R v0.8.0 release contract passed.')
 print(f'Validated {json_count} JSON files, calibration/validation/governance contracts, JavaScript, PHP, documentation aliases, and repository tests.')
 return 0
if __name__=='__main__': raise SystemExit(main())
