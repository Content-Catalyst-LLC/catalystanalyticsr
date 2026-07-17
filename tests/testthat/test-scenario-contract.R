test_that("canonical scenarios validate and round trip through JSON", {
  scenario <- catalyst_scenario(
    title = "Policy pathway",
    id = "policy-pathway",
    role = "intervention",
    times = 0:5,
    constraints = list(emissions_budget = 10),
    assumptions = list(list(
      id = "stable-policy",
      statement = "Policy controls remain fixed over the scenario horizon.",
      status = "declared"
    )),
    metadata = list(created_at = "2026-07-16T00:00:00Z")
  )
  expect_s3_class(scenario, "catalyst_scenario")
  expect_true(validate_catalyst_scenario(scenario))

  json <- scenario_to_json(scenario)
  expect_match(json, '"schema_version": "1.0.0"', fixed = TRUE)
  expect_match(json, '"parameters": {}', fixed = TRUE)
  restored <- scenario_from_json(json)
  expect_identical(scenario_fingerprint(restored), scenario_fingerprint(scenario))
  expect_equal(restored$time$values, 0:5)
  expect_equal(restored$constraints$emissions_budget, 10)
})

test_that("canonical scenarios execute and remain attached to the run", {
  scenario <- catalyst_scenario(
    title = "Executable scenario",
    id = "executable-scenario",
    times = 0:3,
    constraints = list(emissions_budget = 5),
    metadata = list(created_at = "2026-07-16T00:00:00Z")
  )
  result <- run_catalyst_scenario(
    scenario,
    include_phase_plane = FALSE,
    include_sensitivity = FALSE
  )
  expect_s3_class(result, "catalyst_run")
  expect_s3_class(result$scenario, "catalyst_scenario")
  expect_equal(result$meta$scenario_schema_version, "1.0.0")
  expect_equal(result$meta$model_version, "1.0.0")
  expect_identical(result$meta$scenario_fingerprint, scenario_fingerprint(scenario))
})

test_that("scenario validation rejects incompatible contracts", {
  scenario <- catalyst_scenario(
    title = "Validation scenario",
    metadata = list(created_at = "2026-07-16T00:00:00Z")
  )
  broken <- unclass(scenario)
  broken$model$version <- "9.9.9"
  expect_error(validate_catalyst_scenario(broken), "not registered")

  broken <- unclass(scenario)
  broken$time$end <- 99
  expect_error(validate_catalyst_scenario(broken), "start/end")
})
