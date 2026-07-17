
test_that("causal assumptions and regression specifications are governed", {
  assumption <- econometric_assumptions_fixture()[[1L]]
  expect_equal(assumption$status, "supported")
  spec <- regression_spec("basic-regression", "Basic regression", "y", "x", assumptions = list(assumption))
  expect_true(validate_regression_spec(spec, data.frame(y=1:4,x=2:5)))
  expect_error(validate_regression_spec(spec, data.frame(y=1:4)), "Unknown regression columns")
})

test_that("policy regression estimates coefficients and robust diagnostics", {
  data <- data.frame(x=1:20, y=3 + 2 * (1:20))
  spec <- regression_spec("linear-policy", "Linear policy model", "y", "x")
  fit <- fit_policy_regression(data, spec, covariance="hc1")
  expect_s3_class(fit, "catalyst_policy_regression")
  expect_equal(fit$coefficients$estimate[fit$coefficients$term=="x"], 2, tolerance=1e-8)
  expect_true(regression_diagnostics(fit)$r_squared > .999)
})

test_that("difference in differences recovers the policy effect", {
  result <- difference_in_differences(econometric_panel_fixture(), "outcome", "treated", "post", "unit", "time", assumptions=econometric_assumptions_fixture())
  expect_s3_class(result, "catalyst_difference_in_differences")
  expect_equal(result$effect$estimate, 5, tolerance=1e-7)
  expect_true(result$boundary$causal_effect_requires_parallel_trends)
})

test_that("event study preserves dynamic effects and pretrend evidence", {
  result <- event_study(econometric_panel_fixture(), "outcome", "treated", "event_time", "unit", "time", window=c(-3,2), assumptions=econometric_assumptions_fixture())
  expect_s3_class(result, "catalyst_event_study")
  expect_true(all(c("period","estimate","conf_low","conf_high") %in% names(result$effects)))
  expect_true(any(result$effects$period >= 0))
})

test_that("interrupted time series estimates level and slope changes", {
  result <- interrupted_time_series(econometric_its_fixture(), "outcome", "time", 11)
  expect_s3_class(result, "catalyst_interrupted_time_series")
  expect_equal(result$immediate_level_change$estimate, 4, tolerance=1e-7)
  expect_equal(result$slope_change$estimate, 2, tolerance=1e-7)
})

test_that("synthetic control reconstructs the untreated pathway", {
  result <- synthetic_control(econometric_synth_fixture(), "outcome", "unit", "time", "treated", 6)
  expect_s3_class(result, "catalyst_synthetic_control")
  expect_equal(sum(result$donor_weights$weight), 1, tolerance=1e-8)
  expect_equal(result$summary$average_post_effect, 5, tolerance=1e-3)
  expect_true(result$summary$pre_rmspe < 1e-3)
})

test_that("integrated policy evaluation summarizes effects and assumptions", {
  did <- difference_in_differences(econometric_panel_fixture(), "outcome", "treated", "post", "unit", "time", assumptions=econometric_assumptions_fixture())
  its <- interrupted_time_series(econometric_its_fixture(), "outcome", "time", 11)
  analysis <- policy_evaluation_analysis("evaluation-suite", "Policy evaluation suite", list(did=did,its=its), assumptions=econometric_assumptions_fixture(), decision_context="Review transition policy evidence")
  expect_s3_class(analysis, "catalyst_policy_evaluation_analysis")
  expect_equal(policy_evaluation_summary(analysis)$evaluations, 2L)
  expect_true(nrow(policy_effect_summary(analysis)) >= 2L)
})

test_that("policy evaluation exports portable evidence", {
  did <- difference_in_differences(econometric_panel_fixture(), "outcome", "treated", "post", "unit", "time", assumptions=econometric_assumptions_fixture())
  analysis <- policy_evaluation_analysis("export-suite", "Export suite", list(did=did), assumptions=econometric_assumptions_fixture())
  out <- tempfile("policy-evaluation-")
  paths <- export_policy_evaluation(analysis, out, zip_bundle=FALSE)
  expect_true(file.exists(paths$analysis)); expect_true(file.exists(paths$effects)); expect_true(file.exists(paths$manifest))
  manifest <- jsonlite::fromJSON(paths$manifest, simplifyVector=FALSE)
  expect_true(manifest$file_count >= 5L)
  expect_identical(manifest$package$version, "1.6.0")
})

test_that("workspaces retain reusable policy evaluations", {
  did <- difference_in_differences(econometric_panel_fixture(), "outcome", "treated", "post", "unit", "time")
  analysis <- policy_evaluation_analysis("workspace-evaluation", "Workspace evaluation", list(did=did))
  workspace <- workspace_add_policy_evaluation(catalyst_workspace("econometrics-workspace", "Econometrics workspace"), analysis)
  stored <- workspace_get_policy_evaluation(workspace, "workspace-evaluation")
  expect_equal(stored$identification_status, "requires_review")
  expect_equal(workspace_manifest(workspace)$counts$policy_evaluations, 1L)
})
