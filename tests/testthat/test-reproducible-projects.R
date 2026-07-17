test_that("project records preserve analytical components and stable hashes", {
  project <- project_fixture()
  expect_s3_class(project, "catalyst_project")
  expect_true(validate_catalyst_project(project))
  expect_equal(length(project$scenarios), 1L)
  expect_equal(length(project$datasets), 1L)
  expect_equal(length(project$models), 1L)
  expect_equal(length(project$parameter_sets), 1L)
  expect_equal(length(project$runs), 1L)
  expect_equal(project$runs[[1L]]$status, "completed")
  expect_match(project$runs[[1L]]$input_hash, "^[a-f0-9]{32}$")
  expect_match(project$runs[[1L]]$output_hash, "^[a-f0-9]{32}$")
  expect_equal(project$metadata$review_status, "approved")
  expect_match(project_fingerprint(project), "^[a-f0-9]{32}$")
})

test_that("project fingerprint ignores volatile timestamps and source paths", {
  project <- project_fixture()
  copy <- project
  copy$metadata$created_at <- "2030-01-01T00:00:00Z"
  copy$metadata$updated_at <- "2030-01-02T00:00:00Z"
  copy$environment$captured_at <- "2030-01-03T00:00:00Z"
  expect_identical(project_fingerprint(project), project_fingerprint(copy))
})

test_that("project JSON round trip preserves the contract", {
  project <- project_fixture()
  path <- tempfile(fileext = ".json")
  project_to_json(project, path)
  restored <- project_from_json(path)
  expect_s3_class(restored, "catalyst_project")
  expect_equal(restored$id, project$id)
  expect_equal(names(restored$runs), names(project$runs))
  expect_true(validate_catalyst_project(restored))
})

test_that("project references are validated", {
  project <- catalyst_project("reference-validation", "Reference validation")
  scenario <- comparison_scenarios()[[1L]]
  expect_error(project_add_run(project, list(value = 1), "run", scenario_ids = scenario$id), "Unknown project scenarios")
  project <- project_add_scenario(project, scenario)
  expect_error(project_add_run(project, list(value = 1), "run", scenario_ids = scenario$id, parameter_set_id = "missing"), "Unknown project parameter set")
})

test_that("environment capture records software identity", {
  environment <- capture_project_environment(include_session = FALSE)
  expect_equal(environment$schema_version, "1.0.0")
  expect_true(nzchar(environment$r$version))
  expect_true(length(environment$packages) >= 1L)
})
