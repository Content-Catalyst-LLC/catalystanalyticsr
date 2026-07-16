test_that("catalyst_export writes governed metadata and parameter records", {
  run <- catalyst_run(
    times = 0:3,
    x0 = c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1),
    include_phase_plane = FALSE,
    include_sensitivity = FALSE
  )
  parent <- file.path(tempdir(), paste0("catalyst-export-", as.integer(Sys.time())))
  out <- catalyst_export(run, parent, run_id = "test run", zip = FALSE, overwrite = TRUE, quiet = TRUE)

  expect_true(dir.exists(out$bundle_dir))
  expect_true(file.exists(file.path(out$bundle_dir, "parameters.csv")))
  expect_true(file.exists(file.path(out$bundle_dir, "policy.csv")))
  expect_true(file.exists(file.path(out$bundle_dir, "run_metadata.json")))
  expect_equal(out$manifest$run_id, "test-run")
  expect_true(length(out$manifest$file_inventory) >= 1)
})
