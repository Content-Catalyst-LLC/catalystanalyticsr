test_that("boundary assessment distinguishes within, warning, breach, and unit mismatch", {
  definitions <- list(
    boundary_definition("budget", "Cumulative carbon budget", "cumulative_net_emissions", "MtCO2e", upper = 300),
    boundary_definition("terminal", "Terminal net emissions", "terminal_net_emissions", "MtCO2e", upper = 10, warning_margin = 0.5),
    boundary_definition("natural", "Natural-capital floor", "natural_capital_closing_stock", "natural_capital_index", direction = "at_or_above", lower = 1000)
  )
  values <- data.frame(
    indicator = c("cumulative_net_emissions", "terminal_net_emissions", "natural_capital_closing_stock"),
    value = c(334, 7, 1010),
    unit = c("MtCO2e", "MtCO2e", "natural_capital_index"),
    stringsAsFactors = FALSE
  )
  assessment <- evaluate_boundaries(values, definitions)
  expect_s3_class(assessment, "catalyst_boundary_assessment")
  expect_identical(assessment$assessment$status, c("breached", "warning", "warning"))
  expect_equal(sum(boundary_summary(assessment)$count), 3)
  expect_s3_class(plot_boundary_status(assessment), "ggplot")
})
