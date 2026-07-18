import json
import pathlib
import re
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def read(path): return (ROOT / path).read_text(encoding="utf-8")
def load(path): return json.loads(read(path))

def test_connected_platform_contract_files_and_versions():
    manifest = load("catalyst_analytics_r_manifest.json")
    assert manifest["repository_version"] == "2.0.0"
    assert manifest["wordpress_demo"]["version"] == "3.0.0"
    assert manifest["contracts"]["connected_platform"]["version"] == "2.0.0"
    assert manifest["contracts"]["connected_platform_export"]["version"] == "2.0.0"
    assert manifest["contracts"]["connected_api"]["version"] == "2.0.0"
    required = [
        "R/connected_platform.R", "man/connected_platform.Rd", "man/export_connected_platform.Rd",
        "schemas/catalyst_analytics_r_connected_platform.schema.json",
        "schemas/catalyst_analytics_r_connected_platform_export.schema.json",
        "schemas/catalyst_analytics_r_connected_platform_demo_export.schema.json",
        "examples/connected_platform_input.json", "outputs/example_connected_platform_export.json",
        "outputs/example_browser_connected_platform_export.json", "tests/fixtures/connected_platform_contract_v2.json",
        "docs/connected-sustainability-analytics-decision-platform.md", "docs/releases/v2.0.0.md"
    ]
    assert not [path for path in required if not (ROOT / path).exists()]

def test_connected_platform_r_api_and_boundaries():
    source = read("R/connected_platform.R")
    for token in [
        "connected_sustainability_platform", "platform_add_workspace", "platform_add_project",
        "platform_register_records", "platform_add_decision", "platform_add_publication",
        "platform_add_governance", "platform_add_handoff", "platform_lineage",
        "connected_platform_manifest", "export_connected_platform", "catalyst_connected_api_manifest",
        ".connected_platform_fingerprint_record", ".connected_platform_raw_fingerprint",
        "serialized_platform_fingerprint", ".restored_connected_platform_state_fingerprint",
        "automated_decision_authorization = FALSE", "automated_publication = FALSE"
    ]:
        assert token in source
    namespace = read("NAMESPACE")
    assert "export(connected_sustainability_platform)" in namespace
    assert "export(export_connected_platform)" in namespace

def test_browser_connected_platform_contract():
    php = read("wordpress/catalyst-analytics-r-demo/catalyst-analytics-r-demo.php")
    js = read("wordpress/catalyst-analytics-r-demo/assets/catalyst-analytics-r-demo.js")
    assert re.search(r"^ \* Version:\s*3\.0\.0$", php, re.M)
    for token in ["Connected Sustainability Analytics and Decision Platform", "Build connected platform", 'aria-live="polite"']:
        assert token in php
    for token in ["compatible_repository_version:'2.0.0'", "mapped_connected_platform_contract_not_r_execution", "automated_decision_authorization:false", "automated_publication:false"]:
        assert token in js
    with zipfile.ZipFile(ROOT / "dist/catalyst-analytics-r-demo-v3.0.0.zip") as archive:
        assert archive.testzip() is None


def test_connected_platform_round_trip_fingerprint_regression_is_guarded():
    source = read("R/connected_platform.R")
    r_test = read("tests/testthat/test-connected-platform.R")
    assert 'record$metadata$serialized_platform_fingerprint <- connected_platform_fingerprint(platform)' in source
    assert 'result[[".restored_connected_platform_state_fingerprint"]] <- .connected_platform_raw_fingerprint(result)' in source
    assert 'expect_identical(connected_platform_fingerprint(restored), original_fingerprint)' in r_test
    assert 'expect_false(identical(connected_platform_fingerprint(changed), original_fingerprint))' in r_test
