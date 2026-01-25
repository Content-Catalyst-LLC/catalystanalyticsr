test_that("ans computes adjusted net savings correctly", {
  expect_equal(ans(100, 10, 5, 2), 103)
  expect_equal(ans(c(100, 200), c(10, 20), c(5, 10), c(2, 4)), c(103, 206))
})

test_that("ans validates inputs", {
  expect_error(ans("100", 10, 5, 2), "numeric")
  expect_error(ans(100, -1, 5, 2), "cannot be negative")
  expect_error(ans(100, 10, -5, 2), "cannot be negative")
  expect_error(ans(100, 10, 5, -2), "cannot be negative")
})
