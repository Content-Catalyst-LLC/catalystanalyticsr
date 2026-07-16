from pathlib import Path
import json
import re

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def description_version() -> str:
    text = (ROOT / "DESCRIPTION").read_text(encoding="utf-8")
    match = re.search(r"^Version:\s*(\S+)$", text, re.MULTILINE)
    assert match
    return match.group(1)


def plugin_version() -> str:
    text = (ROOT / "wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php").read_text(encoding="utf-8")
    match = re.search(r"^ \* Version:\s*(\S+)$", text, re.MULTILINE)
    assert match
    return match.group(1)


def test_release_manifest_versions_and_shortcode_are_consistent():
    manifest = load_json("catalyst_analytics_r_manifest.json")
    assert manifest["repository"] == "catalystanalyticsr"
    assert manifest["repository_version"] == "0.1.4"
    assert manifest["r_package"]["version"] == description_version() == "0.1.4"
    assert manifest["wordpress_demo"]["version"] == plugin_version() == "1.0.1"
    assert manifest["wordpress_demo"]["compatible_repository_version"] == "0.1.4"
    assert manifest["wordpress_demo"]["shortcode"] == "[catalyst_analytics_r_demo]"


def test_scenario_examples_validate_against_schema():
    schema = load_json("schemas/catalyst_analytics_r_scenario.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(load_json("examples/scenario_input.json"))
    samples = load_json("inst/extdata/sample_scenarios.json")
    assert samples
    for sample in samples:
        validator.validate(sample)


def test_browser_export_validates_against_schema():
    schema = load_json("schemas/catalyst_analytics_r_demo_export.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(load_json("outputs/example_browser_export.json"))


def test_no_placeholder_tests_or_course_language_remain():
    test_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "tests/testthat").glob("*.R"))
    assert "multiplication works" not in test_text
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "R").glob("*.R"))
    assert "CS50R" not in source_text


def test_export_contract_has_no_stale_top_level_fields():
    text = (ROOT / "R/export_catalyst_bundle.R").read_text(encoding="utf-8")
    assert "results$kaya" not in text
    assert "results$params" not in text
    assert "meta$params" in text
    assert 'write_df("parameters"' in text
    assert 'write_df("policy"' in text


def test_theme_has_one_definition():
    text = (ROOT / "R/theme_catalyst.R").read_text(encoding="utf-8")
    assert text.count("theme_catalyst <- function") == 1


def test_raw_json_is_not_stored_in_r_data_directory():
    data_dir = ROOT / "data"
    assert not data_dir.exists() or not list(data_dir.glob("*.json"))
    assert (ROOT / "inst/extdata/sample_scenarios.json").exists()


def test_r_source_is_ascii_portable():
    for path in sorted((ROOT / "R").glob("*.R")):
        assert all(byte <= 127 for byte in path.read_bytes()), path


def test_r_build_ignore_excludes_repository_only_directories():
    entries = (ROOT / ".Rbuildignore").read_text(encoding="ascii")
    for expected in (r"^\.github$", r"^\.pytest_cache$", r"^wordpress$", r"^tests_py$"):
        assert expected in entries


def test_demo_test_compares_values_without_erasing_scenario_identity():
    text = (ROOT / "tests/testthat/test-demo.R").read_text(encoding="utf-8")
    assert 'setdiff(names(passing$trajectory_wide), "scenario")' in text
    assert 'expect_identical(unique(passing$trajectory_wide$scenario), "demo_pass")' in text
    assert 'expect_identical(unique(failing$trajectory_wide$scenario), "demo_fail")' in text
