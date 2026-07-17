test_that("integrated model validation exports governed evidence", {
  fixture <- model_validation_fixture()
  card <- model_card(
    intended_uses = "educational scenario analysis", prohibited_uses = "forecast",
    calibration_evidence = fixture$calibration$calibration_id,
    validation_evidence = fixture$validation$validation_id,
    limitations = list(limitation_record("synthetic-only", "Synthetic evidence", "Not real-world validation.", severity = "high")),
    status = "under_review"
  )
  governance <- model_governance_record(card, reviewers = list("Reviewer"))
  governance <- transition_model_status(governance, "validated_for_specified_use", "Reviewer", "Approved for synthetic educational use", approval = list(decision = "approved"))
  benchmark <- solver_benchmark(fixture$scenario, methods = "rk4", step_sizes = c(1, 0.5), reference_step = 0.5)
  stability <- stability_assessment(fixture$scenario, perturbation_fraction = 0.001, tolerance = 0.2)
  analysis <- model_validation_analysis(fixture$calibration, fixture$validation, benchmark, stability, governance)
  expect_s3_class(analysis, "catalyst_model_validation_analysis")
  path <- tempfile("model-validation-")
  exported <- export_model_validation(analysis, dir = path, zip_bundle = FALSE)
  expect_true(file.exists(exported$analysis))
  expect_true(file.exists(exported$governance))
  expect_true(file.exists(exported$manifest))
  payload <- jsonlite::read_json(exported$analysis, simplifyVector = TRUE)
  expect_equal(payload$schema_version, "1.0.0")
  expect_equal(payload$governance$lifecycle_status, "validated_for_specified_use")
})
