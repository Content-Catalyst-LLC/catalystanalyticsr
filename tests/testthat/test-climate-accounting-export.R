test_that("climate accounting assembles and exports auditable records", {
  definitions <- list(
    boundary_definition("budget", "Cumulative carbon budget", "cumulative_net_emissions", "MtCO2e", upper = 300),
    boundary_definition("natural", "Natural-capital floor", "natural_capital_closing_stock", "natural_capital_index", direction = "at_or_above", lower = 1000)
  )
  analysis <- climate_accounting(
    sample_emissions_inventory(),
    budget = 300,
    natural_capital = sample_natural_capital_account(),
    boundaries = definitions,
    target_year = 2030,
    target_net_emissions = 0,
    analysis_id = "climate-export-test"
  )
  expect_s3_class(analysis, "catalyst_climate_accounting")
  expect_s3_class(analysis$kaya, "catalyst_kaya_decomposition")
  expect_s3_class(analysis$boundary_assessment, "catalyst_boundary_assessment")
  summary <- climate_accounting_summary(analysis)
  expect_equal(summary$carbon$cumulative_net_emissions, 334)

  out <- export_climate_accounting(
    analysis,
    dir = tempdir(),
    prefix = paste0("climate-export-", as.integer(stats::runif(1, 1, 1e8))),
    zip_bundle = FALSE,
    quiet = TRUE
  )
  expected <- c(
    "inventory_manifest.json", "emissions_inventory.csv", "emissions_summary.csv",
    "carbon_pathway.csv", "carbon_diagnostics.csv", "terminal_values.csv",
    "kaya_levels.csv", "kaya_contributions.csv", "kaya_methodology.json",
    "natural_capital_account.csv", "natural_capital_summary.csv", "natural_capital_metadata.json",
    "boundary_definitions.json", "boundary_assessment.csv", "manifest.json", "brief.md"
  )
  expect_true(all(file.exists(file.path(out$directory, expected))))
  manifest <- jsonlite::fromJSON(file.path(out$directory, "manifest.json"), simplifyVector = FALSE)
  expect_identical(manifest$package$version, "1.6.0")
  expect_true(manifest$included$kaya)
  expect_true(manifest$included$natural_capital)
  unlink(out$directory, recursive = TRUE)
})
