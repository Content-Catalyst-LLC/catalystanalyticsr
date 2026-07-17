test_that("KH-NC-PA reference trajectory remains within numerical tolerance", {
  fixture_path <- testthat::test_path("..", "fixtures", "khncpa_reference_v1.json")
  fixture <- jsonlite::read_json(fixture_path, simplifyVector = TRUE)
  scenario <- as_catalyst_scenario(fixture$scenario)
  result <- run_catalyst_scenario(
    scenario,
    method = fixture$integration_method,
    include_phase_plane = FALSE,
    include_sensitivity = FALSE
  )
  expected <- as.data.frame(fixture$checkpoints, stringsAsFactors = FALSE)
  metrics <- c("K", "H", "N", "C", "P", "A", "gdp", "emissions", "ans")
  for (metric in metrics) {
    expect_equal(
      result$trajectory_wide[[metric]],
      expected[[metric]],
      tolerance = fixture$tolerance,
      info = metric
    )
  }
})
