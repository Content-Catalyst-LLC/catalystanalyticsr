#!/usr/bin/env python3
"""Static release-contract checks for Catalyst Analytics R v1.0.0."""
from __future__ import annotations
import json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY_VERSION='1.0.0'; PLUGIN_VERSION='2.0.0'; MANIFEST_VERSION='2.0.0'
def fail(message): raise AssertionError(message)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
def validator(path):
 schema=load(path); jsonschema.Draft202012Validator.check_schema(schema); return jsonschema.Draft202012Validator(schema)
def run(command):
 env=dict(os.environ); env['PYTHONDONTWRITEBYTECODE']='1'; subprocess.run(command,cwd=ROOT,check=True,env=env)
def main():
 desc=read('DESCRIPTION');
 if not re.search(r'^Version:\s*1\.0\.0$',desc,re.M): fail('DESCRIPTION version mismatch')
 manifest=load('catalyst_analytics_r_manifest.json')
 if manifest['schema_version']!=MANIFEST_VERSION or manifest['repository_version']!=REPOSITORY_VERSION or manifest['r_package']['version']!=REPOSITORY_VERSION: fail('Manifest version mismatch')
 if manifest['wordpress_demo']['version']!=PLUGIN_VERSION or manifest['wordpress_demo']['compatible_repository_version']!=REPOSITORY_VERSION: fail('WordPress compatibility mismatch')
 required=['R/production_readiness.R','man/production_readiness.Rd','schemas/catalyst_analytics_r_release_readiness.schema.json','examples/release_readiness.json','outputs/example_release_readiness.json','tests/testthat/test-production-readiness.R','docs/production-readiness.md','docs/api-stability-policy.md','docs/migration-v0.9-to-v1.0.md','docs/tutorial-production-workflow.md','docs/releases/v1.0.0.md',f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip']
 missing=[p for p in required if not (ROOT/p).exists()]
 if missing: fail(f'Missing v1.0.0 files: {missing}')
 source='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'R').glob('*.R'))
 for token in ('catalyst_api_manifest <- function','catalyst_compatibility_manifest <- function','catalyst_release_readiness <- function','validate_release_readiness <- function','automated_release_authorization = FALSE'):
  if token not in source: fail(f'Production implementation missing: {token}')
 namespace=read('NAMESPACE')
 for name in ('catalyst_api_manifest','catalyst_compatibility_manifest','catalyst_release_readiness','validate_release_readiness'):
  if f'export({name})' not in namespace or f'\\alias{{{name}}}' not in read('man/production_readiness.Rd'): fail(f'API documentation missing: {name}')
 for path in sorted((ROOT/'R').glob('*.R')):
  try:path.read_bytes().decode('ascii')
  except UnicodeDecodeError as exc: raise AssertionError(f'Non-ASCII R source: {path.relative_to(ROOT)}') from exc
 for path in sorted(ROOT.rglob('*.json')): json.loads(path.read_text(encoding='utf-8'))
 validator('schemas/catalyst_analytics_r_release_readiness.schema.json').validate(load('outputs/example_release_readiness.json'))
 readiness=load('outputs/example_release_readiness.json')
 if readiness['status']!='ready' or readiness['failed_checks'] or readiness['decision_boundary']['automated_release_authorization'] is not False: fail('Readiness fixture is not fail-closed')
 prior=[('schemas/catalyst_analytics_r_scenario.schema.json','examples/scenario_input.json'),('schemas/catalyst_analytics_r_comparison.schema.json','outputs/example_comparison_export.json'),('schemas/catalyst_analytics_r_uncertainty.schema.json','outputs/example_uncertainty_export.json'),('schemas/catalyst_analytics_r_data_analysis.schema.json','outputs/example_data_analysis_export.json'),('schemas/catalyst_analytics_r_climate_accounting.schema.json','outputs/example_climate_accounting_export.json'),('schemas/catalyst_analytics_r_inclusive_development.schema.json','outputs/example_inclusive_development_export.json'),('schemas/catalyst_analytics_r_model_validation.schema.json','outputs/example_model_validation_export.json'),('schemas/catalyst_analytics_r_project.schema.json','examples/project_input.json')]
 for schema,payload in prior: validator(schema).validate(load(payload))
 php=read('wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'); js=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'); css=read('wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.css')
 if not re.search(r'^ \* Version:\s*2\.0\.0$',php,re.M): fail('Plugin version mismatch')
 for token in ('Stable production contract','aria-live="polite"','Catalyst Analytics R v1.0.0'): 
  if token not in php: fail(f'Plugin production UI missing: {token}')
 for token in ("compatible_repository_version: '1.0.0'",'browser_reproducible_sustainability_analytics_engine'):
  if token not in js: fail(f'Browser contract missing: {token}')
 if ':focus-visible' not in css: fail('Focus visibility contract missing')
 with zipfile.ZipFile(ROOT/f'dist/catalyst-analytics-r-demo-v{PLUGIN_VERSION}.zip') as archive:
  if archive.testzip() is not None: fail('Plugin ZIP integrity failure')
 exports=re.findall(r'^export\(([^)]+)\)$',namespace,re.M); aliases='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'man').glob('*.Rd')); missing_alias=[n for n in exports if f'\\alias{{{n}}}' not in aliases]
 if missing_alias: fail(f'Exported functions missing Rd aliases: {missing_alias}')
 run([sys.executable,'scripts/check_r_structure.py'])
 run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests_py'])
 if subprocess.run(['bash','-lc','command -v node >/dev/null'],cwd=ROOT).returncode==0: run(['node','--check','wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js'])
 if subprocess.run(['bash','-lc','command -v php >/dev/null'],cwd=ROOT).returncode==0: run(['php','-l','wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php'])
 debris=[p for p in ROOT.rglob('*') if p.name in {'.pytest_cache','__pycache__'} or p.name.endswith('.Rcheck')]
 if debris: fail(f'Generated debris remains: {debris}')
 print('Catalyst Analytics R v1.0.0 release contract passed.')
 print(f'Validated {len(list(ROOT.rglob("*.json")))} JSON files, stable API/readiness contracts, prior analytical contracts, browser accessibility, documentation aliases, and repository tests.')
 return 0
if __name__=='__main__': raise SystemExit(main())
