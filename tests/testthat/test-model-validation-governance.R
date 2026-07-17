test_that("historical and holdout validation report metrics and diagnostics", {
  fixture <- model_validation_fixture()
  validation <- fixture$validation
  expect_s3_class(validation, "catalyst_model_validation")
  expect_true(all(c("calibration", "holdout") %in% validation$metrics$split))
  expect_true(all(c("rmse", "mae", "bias", "r_squared") %in% names(validation$metrics)))
  expect_true(all(c("mean_residual", "lag1_autocorrelation") %in% names(validation$residual_diagnostics)))
  expect_identical(validation$status, "passed")
})

test_that("solver benchmarks and stability tests preserve numerical evidence", {
  fixture <- model_validation_fixture()
  benchmark <- solver_benchmark(fixture$scenario, methods = c("rk4", "euler"), step_sizes = c(1, 0.5), reference_step = 0.5)
  expect_s3_class(benchmark, "catalyst_solver_benchmark")
  expect_equal(nrow(benchmark$summary), 4)
  expect_true(all(benchmark$summary$success))
  stability <- stability_assessment(fixture$scenario, perturbation_fraction = 0.001, tolerance = 0.2)
  expect_s3_class(stability, "catalyst_stability_assessment")
  expect_true(all(stability$invariants$passed))
  expect_true(all(stability$boundary_conditions$passed))
})

test_that("model governance enforces evidence and lifecycle transitions", {
  card <- model_card(
    intended_uses = "educational scenario analysis",
    prohibited_uses = c("forecast", "compliance determination"),
    parameters = list(parameter_card("regen", "Regeneration", "Natural-capital regeneration rate", calibrated = TRUE)),
    assumptions = list(assumption_record("constant-rate", "Regeneration is constant during calibration.")),
    limitations = list(limitation_record("synthetic-only", "Synthetic evidence", "The fixture is not real-world validation.", severity = "high")),
    calibration_evidence = "calibration-1", validation_evidence = "validation-1", status = "experimental"
  )
  governance <- model_governance_record(card, reviewers = list("Reviewer"))
  governance <- transition_model_status(governance, "under_review", "Reviewer", "Evidence submitted")
  governance <- transition_model_status(governance, "validated_for_specified_use", "Reviewer", "Approved within stated boundary", approval = list(decision = "approved"))
  expect_identical(governance$lifecycle_status, "validated_for_specified_use")
  expect_equal(model_governance_summary(governance)$transitions, 3)
  expect_error(transition_model_status(governance, "experimental", "Reviewer", "Invalid rollback"), "not allowed")
})
