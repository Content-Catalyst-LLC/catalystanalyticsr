#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v0.9.0."""
from __future__ import annotations
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='0.9.0'; PLUGIN_VERSION='1.8.0'; MANIFEST_VERSION='1.8.0'
NEW_CONTRACTS=('project','analytical_publication','project_handoff')
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
  'R/reproducible_projects.R','R/project_publication.R','man/reproducible_projects.Rd','man/project_publication.Rd',
  'schemas/catalyst_analytics_r_project.schema.json','schemas/catalyst_analytics_r_publication.schema.json','schemas/catalyst_analytics_r_project_handoff.schema.json','schemas/catalyst_analytics_r_project_demo_export.schema.json',
  'examples/project_input.json','outputs/example_project_publication_export.json','outputs/example_browser_project_publication_export.json','tests/fixtures/project_publication_contract_v1.json',
  'tests/testthat/helper-projects.R','tests/testthat/test-reproducible-projects.R','tests/testthat/test-project-publication.R',
  'docs/reproducible-projects-analytical-publication.md','docs/releases/v0.9.0.md',
  'wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css',
  'dist/catalyst-analytics-r-demo-v1.8.0.zip'
 ]
 missing=[p for p in required if not (ROOT/p).exists()]
 if missing: fail(f'Missing v0.9.0 release files: {missing}')
 source='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'R').glob('*.R'))
 symbols=('capture_project_environment <- function','catalyst_project <- function','validate_catalyst_project <- function','project_add_scenario <- function','project_add_dataset <- function','project_add_model <- function','project_add_parameter_set <- function','project_add_run <- function','project_add_indicator <- function','project_add_plot <- function','project_add_note <- function','project_add_review <- function','project_snapshot <- function','project_fingerprint <- function','project_summary <- function','project_manifest <- function','project_to_json <- function','project_from_json <- function','decision_studio_handoff <- function','knowledge_library_handoff <- function','export_project_publication <- function')
 for symbol in symbols:
  if symbol not in source: fail(f'Missing implementation symbol: {symbol}')
 for token in ('input_hash','output_hash','capture_project_environment','analytical-publication.qmd','decision-studio-handoff.json','knowledge-library-methodology.json','reproducible_not_necessarily_valid','approval_not_inferred_from_reproducibility','file_count = length(file_records)','scope = "all_bundle_files_except_manifest"','utils::capture.output'):
  if token not in source: fail(f'Project/publication implementation incomplete: {token}')
 if re.search(r'(?<!utils::)capture\.output\s*\(', source): fail('Unqualified capture.output call remains')
 publication_test=read('tests/testthat/test-project-publication.R')
 for token in ('is.data.frame(manifest$files)', 'nrow(manifest$files)', 'manifest$file_count', 'all_bundle_files_except_manifest'):
  if token not in publication_test: fail(f'Publication regression coverage missing: {token}')
 for path in sorted((ROOT/'R').glob('*.R')):
  try: path.read_bytes().decode('ascii')
  except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
 stale=[]
 for path in sorted((ROOT/'tests'/'testthat').glob('*.R')):
  text=path.read_text(encoding='utf-8')
  if '"0.7.0"' in text or '"0.8.0"' in text: stale.append(str(path.relative_to(ROOT)))
 if stale: fail(f'Stale package expectations remain: {stale}')
 for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
 project=load('examples/project_input.json')
 export=load('outputs/example_project_publication_export.json')
 browser=load('outputs/example_browser_project_publication_export.json')
 validator('schemas/catalyst_analytics_r_project.schema.json').validate(project)
 validator('schemas/catalyst_analytics_r_publication.schema.json').validate(export['publication_manifest'])
 publication_manifest=export['publication_manifest']
 if publication_manifest['file_count'] != len(publication_manifest['files']): fail('Publication manifest file_count mismatch')
 if publication_manifest['integrity'].get('scope') != 'all_bundle_files_except_manifest': fail('Publication manifest integrity scope mismatch')
 validator('schemas/catalyst_analytics_r_project_handoff.schema.json').validate(export['handoffs']['decision_studio'])
 validator('schemas/catalyst_analytics_r_project_handoff.schema.json').validate(export['handoffs']['knowledge_library'])
 validator('schemas/catalyst_analytics_r_project_demo_export.schema.json').validate(browser)
 if project['metadata']['package_version']!='0.9.0': fail('Project fixture package mismatch')
 if not project['runs'] or any(not re.fullmatch(r'[a-f0-9]{32}',run['input_hash']) or not re.fullmatch(r'[a-f0-9]{32}',run['output_hash']) for run in project['runs'].values()): fail('Run hashes are missing or invalid')
 if project['metadata']['review_status']!='approved': fail('Project fixture review mismatch')
 if export['handoffs']['decision_studio']['decision_boundary']['human_decision_required'] is not True: fail('Decision handoff boundary incomplete')
 if export['handoffs']['knowledge_library']['publication_boundary']['limitations_require_prominent_disclosure'] is not True: fail('Knowledge handoff boundary incomplete')
 if browser['contract']['parity_status']!='mapped_project_contract_not_r_execution': fail('Browser parity boundary mismatch')
 prior=[
  ('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),
  ('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),
  ('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),
  ('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),
  ('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),
  ('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),
  ('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json')]
 for schema,payload_path in prior: validator(schema).validate(load(payload_path))
 validation_payload=load('outputs/example_model_validation_export.json')
 validator('schemas/catalyst_analytics_r_calibration.schema.json').validate(validation_payload['calibration'])
 validator('schemas/catalyst_analytics_r_model_governance.schema.json').validate(validation_payload['governance'])
 php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js')
 if not re.search(r'^ \* Version:\s*1\.8\.0$',php,re.M): fail('Plugin version mismatch')
 for token in ('Reproducible project and publication studio','Build project record','Platform handoffs'):
  if token not in php: fail(f'WordPress interface missing: {token}')
 for token in ('browser_reproducible_project_publication','mapped_project_contract_not_r_execution',"compatible_repository_version: '0.9.0'",'project_contract_version','publication_contract_version','decision_studio_analytical_project','knowledge_library_methodology_package'):
  if token not in js: fail(f'WordPress contract missing: {token}')
 with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
  if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
 documented_exports()
 run([sys.executable,'scripts/check_r_structure.py'])
 run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
 if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
 if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
 run([sys.executable,'python/catalyst_analytics_brief.py','outputs/example_project_publication_export.json',str(Path(os.environ.get('TMPDIR','/tmp'))/'catalyst-project-brief.md')])
 debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
 if debris: fail(f'Generated debris remains: {[str(p.relative_to(ROOT)) for p in debris]}')
 json_count=len(list(ROOT.rglob('*.json')))
 print('Catalyst Analytics R v0.9.0 release contract passed.')
 print(f'Validated {json_count} JSON files, project/publication/handoff contracts, prior analytical contracts, JavaScript, PHP, documentation aliases, and repository tests.')
 return 0
if __name__=='__main__': raise SystemExit(main())
