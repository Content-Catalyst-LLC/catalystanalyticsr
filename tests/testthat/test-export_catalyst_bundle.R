test_that("export_catalyst_bundle writes expected files", {
  times <- seq(0, 3, by = 1)
  x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
  res <- simulate_dynamics(times, x0)

  out <- export_catalyst_bundle(res, dir = tempdir(), run_id = "test_run", zip = FALSE, overwrite = TRUE)

  expect_true(dir.exists(out$bundle_dir))
  expect_true(file.exists(file.path(out$bundle_dir, "trajectory_wide.csv")))
  expect_true(file.exists(file.path(out$bundle_dir, "trajectory_long.csv")))
  expect_true(file.exists(file.path(out$bundle_dir, "manifest.json")))

  m <- jsonlite::read_json(file.path(out$bundle_dir, "manifest.json"))
  expect_equal(m$run_id, "test_run")
  expect_true("trajectory_wide.csv" %in% m$files)
})
