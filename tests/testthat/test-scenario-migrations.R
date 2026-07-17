test_that("browser inputs migrate to the canonical scenario contract", {
  fixture_path <- testthat::test_path("..", "fixtures", "browser_contract_mapping_v1.json")
  fixture <- jsonlite::read_json(fixture_path, simplifyVector = FALSE)
  created_at <- fixture$expected_canonical_scenario$metadata$created_at[[1L]]
  migrated <- browser_scenario_to_catalyst(fixture$browser_input, created_at = created_at)
  expected <- as_catalyst_scenario(fixture$expected_canonical_scenario)

  expect_identical(scenario_fingerprint(migrated), scenario_fingerprint(expected))
  browser <- catalyst_scenario_to_browser(migrated)
  expect_equal(browser$scenarioName, "Policy pathway")
  expect_equal(browser$years, 20)
  expect_equal(browser$savings, 0.22)
  expect_equal(browser$emissionsBudget, 120)
})

test_that("legacy R scenarios migrate from schema 0.1.0", {
  path <- system.file("extdata", "scenarios", "legacy_r_scenario_v0.1.0.json", package = "catalystanalyticsr")
  migrated <- scenario_from_json(path)
  expect_s3_class(migrated, "catalyst_scenario")
  expect_equal(migrated$schema_version, "1.0.0")
  expect_equal(migrated$id, "legacy-r-scenario")
  expect_equal(migrated$time$values, 0:3)
})
