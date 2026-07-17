test_that("capital accounts reconcile stocks, flows, and values", {
  account <- capital_account(
    "produced", opening_stock = c(100, 110), investment = c(20, 18),
    depreciation = c(10, 8), closing_stock = c(110, 120), shadow_price = 1.5,
    time = c(2025, 2030), entity = "Region"
  )
  expect_s3_class(account, "catalyst_capital_account")
  expect_true(validate_capital_account(account))
  expect_equal(account$data$expected_closing_stock, c(110, 120))
  expect_equal(account$data$closing_value, c(165, 180))
  expect_equal(max(abs(account$data$reconciliation_error)), 0)
})

test_that("inclusive wealth combines aligned capital accounts", {
  analysis <- example_inclusive_development()
  expect_s3_class(analysis$wealth, "catalyst_inclusive_wealth")
  expect_equal(
    analysis$wealth$data$inclusive_wealth,
    analysis$wealth$data$produced_capital_value + analysis$wealth$data$human_capital_value + analysis$wealth$data$natural_capital_value
  )
  summary <- inclusive_wealth_summary(analysis$wealth)
  expect_true(summary$closing_inclusive_wealth > summary$opening_inclusive_wealth)
  expect_true(is.finite(summary$closing_per_capita))
})

test_that("capital validation rejects unreconciled accounts", {
  account <- capital_account("natural", 100, investment = 5, depletion = 3)
  account$data$closing_stock <- account$data$closing_stock + 1
  account$data$reconciliation_error <- 1
  expect_error(validate_capital_account(account), "reconcile")
})
