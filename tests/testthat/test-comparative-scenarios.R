test_that("scenario sets execute canonical scenarios in one governed batch", {
  set <- run_scenarios(comparison_scenarios())
  expect_s3_class(set, "catalyst_scenario_set")
  expect_equal(set$meta$requested, 3)
  expect_equal(set$meta$completed, 3)
  expect_equal(set$meta$failed, 0)
  expect_setequal(names(set$runs), c("reference-baseline", "transition-policy", "low-investment"))
  expect_true(all(set$index$status == "completed"))
  expect_equal(set$index$role, c("baseline", "intervention", "counterfactual"))
})

test_that("comparisons produce direction-aware deltas, ranks, rules, and scorecards", {
  set <- run_scenarios(comparison_scenarios())
  comparison <- compare_scenarios(
    set,
    metrics = c("gdp", "emissions", "ans", "natural_capital"),
    targets = list(ans = 0),
    thresholds = list(emissions = list(value = 1, operator = "<="))
  )
  expect_s3_class(comparison, "catalyst_comparison")
  expect_equal(comparison$baseline_id, "reference-baseline")
  expect_equal(comparison$meta$scenario_count, 3)
  expect_equal(comparison$meta$metric_count, 4)
  expect_equal(nrow(comparison$values), 12)
  expect_equal(nrow(comparison$deltas), 12)
  expect_equal(nrow(comparison$rankings), 12)
  expect_true(all(c("absolute_delta", "percentage_delta", "outcome") %in% names(comparison$deltas)))
  expect_true(all(c("target_met", "threshold_met", "pareto_rank") %in% names(comparison$scorecard)))

  baseline_rows <- comparison$deltas[comparison$deltas$scenario_id == "reference-baseline", ]
  expect_equal(baseline_rows$absolute_delta, rep(0, nrow(baseline_rows)))
  expect_true(all(baseline_rows$outcome == "tied"))

  policy_emissions <- comparison$deltas[
    comparison$deltas$scenario_id == "transition-policy" & comparison$deltas$metric == "emissions", ]
  expect_equal(policy_emissions$absolute_delta, policy_emissions$scenario_value - policy_emissions$baseline_value)
  expect_equal(policy_emissions$direction, "lower_better")
})

test_that("extractors and Pareto diagnostics preserve comparison results", {
  comparison <- compare_scenarios(
    run_scenarios(comparison_scenarios()),
    metrics = c("gdp", "emissions", "ans", "natural_capital")
  )
  expect_identical(scenario_deltas(comparison), comparison$deltas)
  expect_identical(scenario_rankings(comparison), comparison$rankings)
  expect_identical(scenario_scorecard(comparison), comparison$scorecard)
  pareto <- pareto_diagnostics(comparison)
  expect_true(any(pareto$front$non_dominated))
  expect_true(all(pareto$front$pareto_rank >= 1))
  expect_setequal(pareto$front$scenario_id, names(comparison$scenario_set$runs))
  expect_true(all(comparison$tradeoffs$classification %in% c(
    "dominates_baseline", "dominated_by_baseline", "tradeoff", "equivalent_or_contextual"
  )))
})

test_that("comparisons require an explicit baseline when multiple baselines exist", {
  scenarios <- comparison_scenarios()
  scenarios[[2]]$role <- "baseline"
  scenarios[[2]] <- structure(scenarios[[2]], class = "catalyst_scenario")
  set <- run_scenarios(scenarios)
  expect_error(compare_scenarios(set, metrics = c("gdp", "emissions")), "Multiple baseline")
  expect_s3_class(compare_scenarios(set, baseline = "reference-baseline", metrics = c("gdp", "emissions")), "catalyst_comparison")
})

test_that("comparison plots return ggplot objects", {
  comparison <- compare_scenarios(
    run_scenarios(comparison_scenarios()),
    metrics = c("gdp", "emissions", "ans", "natural_capital")
  )
  expect_s3_class(plot_scenario_comparison(comparison, "gdp", "trajectory"), "ggplot")
  expect_s3_class(plot_scenario_comparison(comparison, "emissions", "terminal"), "ggplot")
  expect_s3_class(plot_scenario_comparison(comparison, "ans", "delta"), "ggplot")
  expect_s3_class(plot_scenario_tradeoffs(comparison, "gdp", "emissions"), "ggplot")
})
