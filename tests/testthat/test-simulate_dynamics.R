test_that("simulate_dynamics returns expected structure", {
  times <- seq(0, 10, by = 1)
  x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)

  res <- simulate_dynamics(times, x0)
  expect_true(is.list(res))
  expect_true(is.data.frame(res$trajectory_wide))
  expect_true(is.data.frame(res$trajectory_long))
  expect_equal(nrow(res$trajectory_wide), length(times))
  expect_true(all(c("t","scenario","K","H","N","C","P","A","gdp","emissions","ans") %in% names(res$trajectory_wide)))
})

test_that("simulate_dynamics respects zero-dynamics invariant when configured", {
  times <- seq(0, 5, by = 1)
  x0 <- c(K = 2, H = 3, N = 1, C = 7, P = 5, A = 11)

  params <- list(
    deltaK = 0, deltaH = 0,
    regen = 0, depletion_intensity = 0,
    emissions_intensity = 0, absorption = 0,
    pop_growth = 0, tech_growth = 0,
    abatement_cost_scale = 0
  )
  policy <- list(s = 0, e = 0, a = 0)

  res <- simulate_dynamics(times, x0, policy = policy, params = params, method = "rk4")
  tw <- res$trajectory_wide

  expect_equal(tw$K, rep(x0[["K"]], length(times)))
  expect_equal(tw$H, rep(x0[["H"]], length(times)))
  expect_equal(tw$N, rep(x0[["N"]], length(times)))
  expect_equal(tw$C, rep(x0[["C"]], length(times)))
  expect_equal(tw$P, rep(x0[["P"]], length(times)))
  expect_equal(tw$A, rep(x0[["A"]], length(times)))
})
