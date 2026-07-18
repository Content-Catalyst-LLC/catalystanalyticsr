from pathlib import Path
import json, re
import jsonschema
ROOT=Path(__file__).resolve().parents[1]

def load(path): return json.loads((ROOT/path).read_text())

def test_public_api_and_handoff_examples_validate():
    pairs=[
      ('schemas/catalyst_analytics_r_public_api.schema.json','outputs/example_public_api_manifest.json'),
      ('schemas/catalyst_analytics_r_api_request.schema.json','examples/public_api_request.json'),
      ('schemas/catalyst_analytics_r_api_response.schema.json','outputs/example_api_response.json'),
      ('schemas/catalyst_analytics_r_platform_handoff.schema.json','outputs/example_platform_handoff.json'),
      ('schemas/catalyst_analytics_r_platform_demo_export.schema.json','outputs/example_browser_platform_export.json')]
    for schema,payload in pairs:
        jsonschema.Draft202012Validator(load(schema)).validate(load(payload))

def test_public_api_contract_has_all_products_and_boundaries():
    source=(ROOT/'R/public_api_handoffs.R').read_text()
    for token in ('site_intelligence_handoff','research_lab_handoff','workbench_handoff','catalyst_canvas_handoff','decision_studio','knowledge_library','transport_server_not_included','human_review_required'):
        assert token in source
    fixture=load('tests/fixtures/public_api_handoff_contract_v1.json')
    assert fixture['repository_version']=='2.0.0'
    assert len(fixture['targets'])==6

def test_new_rd_usage_is_real_multiline_r_code():
    for name in ('public_api_handoffs.Rd','export_platform_handoffs.Rd'):
        text=(ROOT/'man'/name).read_text()
        import re
        assert not re.search(r'\\n(?!ame\{)', text)
        assert '\\usage{' in text
        assert text.endswith('\n')
