test_that("comparative bundles preserve scenarios, tables, plots, and manifests", {
  scenarios <- comparison_scenarios()[1:2]
  comparison <- compare_scenarios(
    run_scenarios(scenarios),
    metrics = c("gdp", "emissions", "ans", "natural_capital")
  )
  out <- export_scenario_comparison(
    comparison,
    dir = tempdir(),
    comparison_id = "test-comparison",
    zip = FALSE,
    overwrite = TRUE,
    quiet = TRUE
  )
  expect_true(dir.exists(out$bundle_dir))
  expected <- c(
    "scenario_index.csv", "terminal_values.csv", "deltas.csv", "rankings.csv",
    "scorecard.csv", "tradeoffs.csv", "pareto_front.csv", "dominance.csv",
    "comparison.json", "manifest.json"
  )
  expect_true(all(file.exists(file.path(out$bundle_dir, expected))))
  expect_true(file.exists(file.path(out$bundle_dir, "scenarios", "reference-baseline.json")))
  expect_true(file.exists(file.path(out$bundle_dir, "trajectories", "transition-policy.csv")))
  expect_true(file.exists(file.path(out$bundle_dir, "plots", "gdp_trajectory.png")))

  manifest <- jsonlite::read_json(file.path(out$bundle_dir, "manifest.json"), simplifyVector = TRUE)
  expect_equal(manifest$schema_version, "1.0.0")
  expect_equal(manifest$package_version, "0.8.0")
  expect_equal(manifest$baseline_id, "reference-baseline")
  expect_equal(manifest$scenario_count, 2)
  expect_true("comparison.json" %in% manifest$files)
})
