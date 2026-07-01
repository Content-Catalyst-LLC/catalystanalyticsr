from pathlib import Path
import json


def test_manifest_exists_and_names_shortcode():
    manifest = json.loads(Path("catalyst_analytics_r_manifest.json").read_text())
    assert manifest["repository"] == "catalystanalyticsr"
    assert manifest["wordpress_shortcode"] == "[catalyst_analytics_r_demo]"


def test_schema_valid_json():
    json.loads(Path("schemas/catalyst_analytics_r_scenario.schema.json").read_text())


def test_sample_scenarios_valid_json():
    data = json.loads(Path("data/sample_scenarios.json").read_text())
    assert isinstance(data, list)
    assert data
    assert "scenarioName" in data[0]
