test_that("carbon pathways calculate budget use, overshoot, lock-in, and stranded signals", {
  pathway <- carbon_budget_pathway(
    sample_emissions_inventory(),
    budget = 300,
    target_year = 2030,
    target_net_emissions = 0
  )
  expect_s3_class(pathway, "catalyst_carbon_pathway")
  expect_equal(utils::tail(pathway$pathway$cumulative_net_emissions, 1), 334)
  expect_equal(utils::tail(pathway$pathway$remaining_budget, 1), -34)
  expect_identical(pathway$diagnostics$overshoot_time, 2029L)
  expect_true(pathway$diagnostics$stranded_pathway_signal)
  expect_false(pathway$diagnostics$within_budget)
  expect_s3_class(plot_carbon_budget_pathway(pathway), "ggplot")
})

test_that("Kaya decomposition reconstructs emissions and reconciles additive effects", {
  decomposition <- kaya_decomposition(sample_emissions_inventory())
  expect_s3_class(decomposition, "catalyst_kaya_decomposition")
  expect_lt(max(abs(decomposition$levels$identity_error)), 1e-8)
  expect_lt(max(abs(decomposition$contributions$residual)), 1e-8)
  expect_equal(decomposition$contributions$emissions_change, -65)
  expect_s3_class(plot_kaya_decomposition(decomposition), "ggplot")
})
