test_that("Adjusted Net Savings exposes additions, deductions, and GNI rate", {
  result <- adjusted_net_savings_decomposition(
    gross_savings = 100, produced_capital_depreciation = 25,
    education_investment = 15, health_investment = 10,
    natural_resource_depletion = 8, pollution_damages = 4,
    climate_damages = 3, gni = 1000
  )
  expect_equal(result$human_capital_investment, 25)
  expect_equal(result$total_deductions, 40)
  expect_equal(result$adjusted_net_savings, 85)
  expect_equal(result$adjusted_net_savings_percent_gni, 8.5)
  expect_true(result$sustainable_savings_signal)
})

test_that("human development indices remain bounded and decomposed", {
  hdi <- human_development_indicators(72, 13, 9, 16000)
  expect_true(all(hdi$life_expectancy_index >= 0 & hdi$life_expectancy_index <= 1))
  expect_true(all(hdi$education_index >= 0 & hdi$education_index <= 1))
  expect_true(all(hdi$income_index >= 0 & hdi$income_index <= 1))
  expect_equal(hdi$human_development_index, (hdi$life_expectancy_index * hdi$education_index * hdi$income_index)^(1 / 3))
})

test_that("distribution analysis reports inequality and social-floor exposure", {
  result <- distributional_analysis(
    values = c(10, 20, 30, 50, 90), weights = rep(1, 5),
    groups = letters[1:5], social_floor = 25
  )
  expect_s3_class(result, "catalyst_distribution_analysis")
  expect_true(result$summary$gini > 0)
  expect_equal(result$summary$share_below_social_floor, 0.4)
  expect_equal(nrow(result$group_summary), 5)
})

test_that("intergenerational analysis preserves per-capita trajectories", {
  result <- intergenerational_analysis(
    wealth = c(1000, 1200, 1500), population = c(5, 5.5, 6),
    time = c(2025, 2030, 2035), target_per_capita = 240
  )
  expect_s3_class(result, "catalyst_intergenerational_analysis")
  expect_equal(result$trajectory$wealth_per_capita, c(200, 1200 / 5.5, 250))
  expect_true(result$summary$non_declining_signal)
  expect_equal(result$summary$end_target_gap, 10)
})
