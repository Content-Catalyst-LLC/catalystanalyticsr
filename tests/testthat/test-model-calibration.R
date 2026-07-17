test_that("calibration estimates bounded parameters and preserves fitted values", {
  fixture <- model_validation_fixture()
  calibration <- fixture$calibration
  expect_s3_class(calibration, "catalyst_calibration")
  expect_true(calibration$parameters$estimate[1] >= 0.001)
  expect_true(calibration$parameters$estimate[1] <= 0.08)
  expect_lt(abs(calibration$parameters$estimate[1] - 0.04), 0.02)
  expect_true(all(c("observed", "predicted", "residual", "split") %in% names(calibration$fitted)))
  expect_true(is.finite(calibration_summary(calibration)$objective_value))
})

test_that("calibration targets are validated", {
  scenario <- catalyst_scenario(title = "Bad target", times = 0:2, metadata = list(created_at = "2026-07-17T00:00:00Z"))
  spec <- calibration_spec(list(bad = list(target = "unknown.value", initial = 1, lower = 0, upper = 2)))
  observations <- data.frame(time = 0:2, metric = "N", observed = c(1, 1, 1))
  expect_error(calibrate_model(scenario, observations, spec), "Unsupported calibration target")

  missing_spec <- calibration_spec(list(bad = list(target = "parameters.not_registered", initial = 1, lower = 0, upper = 2)))
  expect_error(calibrate_model(scenario, observations, missing_spec), "Unsupported calibration target")
})
