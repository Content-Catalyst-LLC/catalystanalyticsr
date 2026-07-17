test_that("built-in indicators are discoverable and calculate traceable values", {
  dataset <- sample_catalyst_dataset()
  registry <- list_catalyst_indicators()
  expect_true(all(c("carbon_intensity", "adjusted_net_savings", "cumulative_emissions") %in% registry$id))

  result <- calculate_indicator(dataset, "carbon_intensity")
  expect_s3_class(result, "catalyst_indicator_result")
  expect_equal(result$values$value[1], 0.4)
  expect_identical(result$values$unit[1], "tCO2e/currency")
  trace <- indicator_trace(result)
  expect_identical(trace$dataset$id, dataset$id)
  expect_identical(trace$indicator$formula, "emissions / gdp")
  expect_identical(trace$calculation$input_rows, nrow(dataset$data))
})

test_that("aggregate indicators support governed grouping", {
  dataset <- sample_catalyst_dataset()
  result <- calculate_indicator(dataset, "cumulative_emissions", group_by = "region")
  expect_equal(nrow(result$values), 2)
  north <- result$values$value[result$values$region == "North"]
  south <- result$values$value[result$values$region == "South"]
  expect_equal(north, 113)
  expect_equal(south, 98)
})

test_that("custom indicators can be registered and combined", {
  dataset <- sample_catalyst_dataset()
  definition <- new_catalyst_indicator(
    id = "savings_rate_observed",
    version = "1.0.0",
    title = "Observed savings rate",
    description = "Gross savings divided by GDP.",
    formula = "gross_savings / gdp",
    required_fields = c("gross_savings", "gdp"),
    unit = "fraction",
    direction = "higher_better",
    aggregation = "rowwise",
    source = list(type = "derived"),
    calculation = function(data, dataset, na_rm) data$gross_savings / data$gdp
  )
  register_catalyst_indicator(definition, overwrite = TRUE)
  expect_identical(get_catalyst_indicator("savings_rate_observed")$version, "1.0.0")
  set <- calculate_indicators(dataset, list("carbon_intensity", definition))
  expect_s3_class(set, "catalyst_indicator_set")
  expect_equal(length(set$results), 2)
  expect_true(all(c("carbon_intensity", "savings_rate_observed") %in% set$values$indicator))
  expect_equal(length(catalyst_indicator_manifest(c("carbon_intensity", "savings_rate_observed"))), 2)
})
