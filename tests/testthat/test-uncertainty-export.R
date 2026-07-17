test_that("uncertainty exports include provenance and failure records", {
  scenario <- scenario_from_json(system.file("extdata", "scenarios", "canonical_uncertain_policy_v1.json", package = "catalystanalyticsr"))
  ensemble <- run_uncertainty(scenario, n = 4, sampling = "monte_carlo", seed = 5, metrics = c("emissions", "natural_capital"))
  out <- tempfile("uncertainty-bundle-")
  paths <- export_uncertainty_analysis(ensemble, dir = out, include_samples = TRUE, zip_bundle = FALSE)
  expect_true(file.exists(file.path(out, "uncertainty-analysis.json")))
  expect_true(file.exists(file.path(out, "uncertainty-manifest.json")))
  payload <- jsonlite::fromJSON(file.path(out, "uncertainty-analysis.json"), simplifyVector = FALSE)
  expect_identical(payload$analysis_type, "uncertainty_ensemble")
  expect_identical(payload$meta$seed, 5L)
})


test_that("stress exports use the comparative bundle contract", {
  scenario <- scenario_from_json(system.file("extdata", "scenarios", "canonical_baseline_v1.json", package = "catalystanalyticsr"))
  result <- run_stress_tests(
    scenario,
    cases = list(stress_case("resource-shock", "Resource shock", list(stress_shock("initial_state.N", 0.9, "multiply")))),
    metrics = c("emissions", "natural_capital")
  )
  parent <- tempfile("stress-bundle-")
  out <- export_stress_test(result, dir = parent, prefix = "check")
  expect_true(dir.exists(out$bundle_dir))
  expect_true(file.exists(out$stress_cases))
  expect_true(file.exists(file.path(out$bundle_dir, "comparison.json")))
})
