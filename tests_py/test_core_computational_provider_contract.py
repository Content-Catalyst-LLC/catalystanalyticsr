import json
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
def validate(schema,payload): jsonschema.Draft202012Validator(load(schema)).validate(load(payload))

def test_core_provider_contract_examples_validate():
    validate('schemas/catalyst_analytics_r_core_provider.schema.json','examples/core_provider_manifest.json')
    validate('schemas/catalyst_analytics_r_core_request.schema.json','examples/core_analytical_request.json')
    validate('schemas/catalyst_analytics_r_workspace_core_execution.schema.json','examples/workspace_core_execution_envelope.json')
    validate('schemas/catalyst_analytics_r_core_result.schema.json','examples/core_analytical_result.json')

def test_provider_matches_platform_core_310_contract():
    p=load('examples/core_provider_manifest.json')
    assert p['provider_key']=='catalystanalyticsr' and p['provider_version']=='2.2.0'
    assert p['core_contract']=='sc.core.analytical-runtime-provider.v1'
    assert p['runtime']=='r' and p['execution_host']=='workspace'
    assert p['boundary']['core_executes_provider'] is False
    caps={x['capability_key'] for x in p['capabilities']}
    assert caps=={'scenario_simulation','uncertainty_analysis','sensitivity_analysis','econometrics','causal_inference','policy_evaluation','forecasting','model_validation','climate_accounting','natural_capital','inclusive_wealth','distribution_analysis'}

def test_core_r_api_and_boundaries_are_exported():
    ns=(ROOT/'NAMESPACE').read_text(); src=(ROOT/'R/core_computational_provider.R').read_text(); docs=(ROOT/'man/core_computational_provider.Rd').read_text()
    names=['catalyst_core_provider_manifest','core_analytical_request','as_core_analytical_request','validate_core_analytical_request','core_execution_plan','workspace_core_execution_envelope','core_analytical_result','validate_core_analytical_result','core_request_to_json','core_request_from_json','core_result_to_json','core_result_from_json']
    for n in names:
        assert f'export({n})' in ns and f'\\alias{{{n}}}' in docs
    for token in ['core_executes_provider = FALSE','workspace_controls_execution_environment = TRUE','arbitrary_function_dispatch = FALSE','workspace_must_resolve_input_refs = TRUE','result_does_not_certify_scientific_validity = TRUE']:
        assert token in src

def test_forecasting_scope_is_not_overstated():
    p=load('examples/core_provider_manifest.json')
    f=next(x for x in p['capabilities'] if x['capability_key']=='forecasting')
    assert f['execution_status']=='projection_only'
    assert f['method_refs']==['scenario_projection']
