test_that("data analysis export preserves records, definitions, quality, and trace", {
  dataset <- sample_catalyst_dataset()
  out <- export_data_analysis(
    dataset,
    indicators = c("carbon_intensity", "adjusted_net_savings"),
    dir = tempdir(),
    analysis_id = paste0("data-export-", as.integer(stats::runif(1, 1, 1e8))),
    zip = FALSE,
    quiet = TRUE
  )
  expect_true(dir.exists(out$directory))
  expected <- c(
    "data.csv", "dataset_manifest.json", "source.json", "quality_flags.csv",
    "transformations.json", "indicator_values.csv", "indicator_definitions.json",
    "indicator_trace.json", "manifest.json"
  )
  expect_true(all(file.exists(file.path(out$directory, expected))))
  manifest <- jsonlite::fromJSON(file.path(out$directory, "manifest.json"), simplifyVector = FALSE)
  expect_identical(manifest$dataset$id, dataset$id)
  expect_identical(manifest$package$version, "1.5.0")
  unlink(out$directory, recursive = TRUE)
})
