test_that("simulation rejects malformed package inputs", {
  state <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
  expect_error(simulate_dynamics(c(0, 0), state), "strictly increasing")
  expect_error(simulate_dynamics(0:2, state[-1]), "must include names")
  expect_error(simulate_dynamics(0:2, state, scenario = ""), "non-empty")
  expect_error(simulate_dynamics(0:2, state, params = list(unknown = 1)), "Unknown model parameter")
  expect_error(simulate_dynamics(0:2, state, policy = list(s = 0.2, e = 0.1)), "include values named")
})

test_that("parameter contract rejects invalid elasticities", {
  state <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
  expect_error(
    simulate_dynamics(0:2, state, params = list(alpha = 0.8, beta = 0.4)),
    "must be <= 1"
  )
})
