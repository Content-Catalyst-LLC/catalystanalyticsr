test_that("v1 API manifest declares stable contracts", {
  manifest <- catalyst_api_manifest()
  expect_identical(manifest$package$version, "1.0.0")
  expect_true(all(c("catalyst_scenario", "run_uncertainty", "export_project_publication") %in% manifest$stable))
  expect_identical(manifest$contract_versions$release_readiness, "1.0.0")
})

test_that("release readiness fails closed", {
  ready <- catalyst_release_readiness(evidence = list(r_cmd_check = "0 errors, 0 warnings, 0 notes"))
  expect_identical(ready$status, "ready")
  expect_silent(validate_release_readiness(ready, require_ready = TRUE))
  blocked <- catalyst_release_readiness(checks = c(accessibility_reviewed = FALSE))
  expect_identical(blocked$status, "not_ready")
  expect_error(validate_release_readiness(blocked, require_ready = TRUE), "not ready")
  expect_error(catalyst_release_readiness(checks = c(unknown_gate = TRUE)), "Unknown")
})

test_that("compatibility manifest maps WordPress companion", {
  compatibility <- catalyst_compatibility_manifest()
  expect_identical(compatibility$wordpress$version, "2.0.0")
  expect_identical(compatibility$wordpress$compatible_repository_version, "1.0.0")
  expect_true("1.0.0" %in% compatibility$supported_inputs$project)
})
