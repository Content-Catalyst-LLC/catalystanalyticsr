test_that("uncertainty specifications validate supported distributions", {
  spec <- uncertainty_spec("parameters.emissions_intensity", "triangular", list(min = 0.08, mode = 0.12, max = 0.18))
  expect_identical(spec$distribution, "triangular")
  expect_error(uncertainty_spec("parameters.emissions_intensity", "uniform", list(min = 1, max = 0)))
})

test_that("sampling is reproducible and Latin hypercube covers requested rows", {
  scenario <- scenario_from_json(system.file("extdata", "scenarios", "canonical_uncertain_policy_v1.json", package = "catalystanalyticsr"))
  a <- sample_uncertainty(scenario, n = 12, method = "latin_hypercube", seed = 9)
  b <- sample_uncertainty(scenario, n = 12, method = "latin_hypercube", seed = 9)
  expect_equal(a, b)
  expect_equal(nrow(a), 12)
  expect_true(all(c("parameters.emissions_intensity", "parameters.regen", "policy.a") %in% names(a)))
})

test_that("uncertainty ensembles retain intervals probabilities and sensitivity", {
  scenario <- scenario_from_json(system.file("extdata", "scenarios", "canonical_uncertain_policy_v1.json", package = "catalystanalyticsr"))
  ensemble <- run_uncertainty(
    scenario, n = 8, sampling = "latin_hypercube", seed = 11,
    metrics = c("gdp", "emissions", "ans"),
    thresholds = list(emissions = list(value = 1, operator = "<="))
  )
  expect_s3_class(ensemble, "catalyst_uncertainty_run")
  expect_equal(ensemble$meta$requested, 8)
  expect_true(all(c("p10", "median", "p90") %in% names(ensemble$summary)))
  expect_equal(nrow(ensemble$probabilities), 1)
  expect_true(nrow(ensemble$sensitivity) >= 3)
})

test_that("local sensitivity and named stress tests are comparison ready", {
  scenario <- scenario_from_json(system.file("extdata", "scenarios", "canonical_uncertain_policy_v1.json", package = "catalystanalyticsr"))
  local <- local_sensitivity(scenario, targets = "parameters.emissions_intensity", change = 0.02, metrics = "emissions")
  expect_equal(nrow(local), 1)
  cases <- list(
    stress_case("high-emissions", "High emissions", list(stress_shock("parameters.emissions_intensity", 1.5, "multiply"))),
    stress_case("restoration", "Restoration", list(stress_shock("parameters.regen", 1.5, "multiply")))
  )
  stressed <- run_stress_tests(scenario, cases, metrics = c("emissions", "natural_capital"))
  expect_s3_class(stressed, "catalyst_stress_test")
  expect_equal(stressed$meta$case_count, 2)
  expect_equal(length(stressed$scenario_set$runs), 3)
})
