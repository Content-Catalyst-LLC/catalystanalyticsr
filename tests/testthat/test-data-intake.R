test_that("governed datasets retain source, quality, units, and stable fingerprints", {
  dataset <- sample_catalyst_dataset()
  expect_s3_class(dataset, "catalyst_dataset")
  expect_true(validate_catalyst_dataset(dataset))
  expect_identical(dataset$source$id, "test-source")
  expect_identical(dataset$units$emissions, "tCO2e")
  expect_equal(dataset$quality$duplicate_keys, 0)
  expect_match(dataset_fingerprint(dataset), "^[a-f0-9]{32}$")
  expect_identical(dataset_fingerprint(dataset), dataset_fingerprint(dataset))
  manifest <- dataset_manifest(dataset)
  expect_identical(manifest$id, "test-dataset")
  expect_false("data" %in% names(manifest) && !is.null(manifest$data))
})

test_that("CSV and JSON readers create equivalent documented datasets", {
  csv_path <- system.file("extdata", "data", "sample_country_timeseries.csv", package = "catalystanalyticsr")
  json_path <- system.file("extdata", "data", "sample_country_timeseries.json", package = "catalystanalyticsr")
  args <- list(
    id = "sample-read",
    title = "Sample read",
    time_field = "year",
    entity_fields = "region",
    required_fields = c("year", "region", "gdp", "population", "emissions")
  )
  csv <- do.call(read_catalyst_data, c(list(path = csv_path), args))
  json <- do.call(read_catalyst_data, c(list(path = json_path), args))
  expect_equal(csv$data, json$data)
  expect_match(csv$source$metadata$md5, "^[a-f0-9]{32}$")
  expect_equal(nrow(data_quality_report(csv)$flags), 0)
  expect_true(data_quality_report(csv)$time_ordered)
  portable_copy <- csv
  portable_copy$metadata$created_at <- "2099-01-01T00:00:00Z"
  portable_copy$source$metadata$local_path <- "/different/machine/path.csv"
  expect_identical(dataset_fingerprint(csv), dataset_fingerprint(portable_copy))
})

test_that("unit conversions update values, units, and transformation history", {
  dataset <- sample_catalyst_dataset()
  dataset$data$mass <- c(1000, 2000, 3000, 4000, 5000, 6000)
  dataset$units$mass <- "kg"
  dataset$fields[[length(dataset$fields) + 1L]] <- list(name = "mass", type = "numeric", unit = "kg", required = FALSE)
  converted <- convert_dataset_unit(dataset, "mass", "t")
  expect_equal(converted$data$mass, c(1, 2, 3, 4, 5, 6))
  expect_identical(converted$units$mass, "t")
  expect_identical(converted$transformations[[1]]$operation, "unit_conversion")
  expect_true(any(list_unit_conversions()$dimension == "mass"))
})
