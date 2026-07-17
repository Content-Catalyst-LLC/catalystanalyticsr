test_that("catalyst_demo returns a complete reproducible run", {
  run <- catalyst_demo(budget_mode = "pass")
  expect_s3_class(run, "catalyst_run")
  expect_true(is.data.frame(run$trajectory_wide))
  expect_true(is.data.frame(run$sdg_indicators))
  expect_true(is.list(run$carbon_budget))
  expect_true(run$carbon_budget$within_budget)
  expect_equal(run$meta$model, "khncpa")
  expect_equal(run$meta$model_version, "1.0.0")
  expect_equal(run$meta$model_contract_version, "1.0.0")
})

test_that("catalyst_demo supports deterministic pass and fail budgets", {
  passing <- catalyst_demo(seed = 7, budget_mode = "pass")
  failing <- catalyst_demo(seed = 7, budget_mode = "fail")
  expect_true(passing$carbon_budget$within_budget)
  expect_false(failing$carbon_budget$within_budget)

  metric_columns <- setdiff(names(passing$trajectory_wide), "scenario")
  expect_equal(
    passing$trajectory_wide[metric_columns],
    failing$trajectory_wide[metric_columns]
  )
  expect_identical(unique(passing$trajectory_wide$scenario), "demo_pass")
  expect_identical(unique(failing$trajectory_wide$scenario), "demo_fail")
})

test_that("custom demo budgets are validated", {
  expect_error(catalyst_demo(budget_mode = "custom"), "supply `emissions_budget`")
  expect_error(catalyst_demo(budget_mode = "pass", emissions_budget = 10), "only used")
})
