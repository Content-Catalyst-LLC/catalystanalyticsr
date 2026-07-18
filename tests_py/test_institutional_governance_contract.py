from pathlib import Path
import json
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text())
def test_institutional_governance_examples_validate():
    pairs=[
      ('schemas/catalyst_analytics_r_institutional_governance.schema.json','examples/institutional_governance_input.json'),
      ('schemas/catalyst_analytics_r_institutional_governance_export.schema.json','outputs/example_institutional_governance_export.json'),
      ('schemas/catalyst_analytics_r_institutional_governance_demo_export.schema.json','outputs/example_browser_institutional_governance_export.json')]
    for schema,payload in pairs: jsonschema.Draft202012Validator(load(schema)).validate(load(payload))
def test_institutional_governance_contract_has_roles_and_boundaries():
    fixture=load('tests/fixtures/institutional_governance_contract_v1.json')
    assert fixture['repository_version']=='2.0.0'
    assert set(('analyst','reviewer','approver','publisher')).issubset(fixture['roles'])
    assert fixture['boundaries']['human_approval_required'] is True
    source=(ROOT/'R/institutional_governance.R').read_text()
    for token in ('assign_institutional_review','add_review_comment','submit_change_request','record_governance_approval','sign_analytical_release','archive_governance_workflow','automated_publication = FALSE'):
        assert token in source
