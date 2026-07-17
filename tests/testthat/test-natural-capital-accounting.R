test_that("natural-capital accounts reconcile stocks and flows", {
  account <- sample_natural_capital_account()
  expect_s3_class(account, "catalyst_natural_capital_account")
  expect_true(validate_natural_capital_account(account))
  expect_equal(account$data$reconciliation_error, rep(0, 6))
  summary <- natural_capital_summary(account)
  expect_equal(summary$opening_stock, 1000)
  expect_equal(summary$closing_stock, 1010)
  expect_equal(summary$net_change, 10)
  expect_s3_class(plot_natural_capital_account(account), "ggplot")
})

test_that("natural-capital accounts reject unreconciled observed stocks", {
  account <- natural_capital_account(
    opening_stock = 100,
    regeneration = 5,
    extraction = 2,
    closing_stock = 110
  )
  expect_error(validate_natural_capital_account(account), "does not reconcile")
})
