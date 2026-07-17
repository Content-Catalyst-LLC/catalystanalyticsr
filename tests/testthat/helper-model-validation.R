model_validation_fixture <- function() {
  truth <- catalyst_scenario(
    title = "Calibration truth",
    id = "calibration-truth",
    times = 0:6,
    parameters = list(regen = 0.04),
    metadata = list(created_at = "2026-07-17T00:00:00Z")
  )
  truth_run <- run_catalyst_scenario(truth, include_phase_plane = FALSE, include_sensitivity = FALSE)
  observations <- data.frame(
    time = truth_run$trajectory_wide$t,
    metric = "N",
    observed = truth_run$trajectory_wide$N + c(0, 0.001, -0.001, 0.001, -0.001, 0.001, -0.001),
    weight = 1,
    stringsAsFactors = FALSE
  )
  observations <- validation_split(observations, holdout_fraction = 2 / 7)
  template <- catalyst_scenario(
    title = "Calibration template",
    id = "calibration-template",
    times = 0:6,
    parameters = list(regen = 0.015),
    metadata = list(created_at = "2026-07-17T00:00:00Z")
  )
  spec <- calibration_spec(list(regen = list(
    target = "parameters.regen", initial = 0.015, lower = 0.001, upper = 0.08,
    unit = "fraction_per_year", description = "Natural-capital regeneration rate"
  )), maxit = 100)
  calibration <- calibrate_model(template, observations[observations$split == "calibration", ], spec)
  validation <- validate_model_fit(calibration, observations = observations, thresholds = list(rmse = 0.02, mae = 0.02, absolute_bias = 0.02))
  list(scenario = template, observations = observations, spec = spec, calibration = calibration, validation = validation)
}
