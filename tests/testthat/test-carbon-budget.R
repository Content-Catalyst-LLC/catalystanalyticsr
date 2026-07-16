test_that("carbon_budget uses trapezoidal integration", {
  trajectory <- data.frame(t = c(0, 1, 3), emissions = c(2, 4, 4))
  result <- carbon_budget(trajectory, budget = 12)
  expect_equal(result$cumulative_emissions, 11)
  expect_equal(result$remaining, 1)
  expect_true(result$within_budget)
})

test_that("carbon_budget rejects invalid trajectories", {
  expect_error(carbon_budget(data.frame(t = c(0, 0), emissions = c(1, 1)), 10), "strictly increasing")
  expect_error(carbon_budget(data.frame(t = 0:1, emissions = c(1, NA)), 10), "finite")
  expect_error(carbon_budget(data.frame(t = 0:1, emissions = c(1, -1)), 10), "cannot be negative")
})
