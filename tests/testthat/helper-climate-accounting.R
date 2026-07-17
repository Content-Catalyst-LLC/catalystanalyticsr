sample_climate_dataset <- function() {
  data <- data.frame(
    region = rep("Global", 6),
    year = 2025:2030,
    emissions = c(100, 90, 78, 65, 50, 35),
    removals = c(5, 7, 10, 14, 20, 28),
    energy = c(500, 480, 450, 420, 380, 340),
    gdp = c(1000, 1030, 1060, 1090, 1120, 1150),
    population = c(100, 101, 102, 103, 104, 105),
    opening_stock = c(1000, 993, 990, 990, 993, 999),
    regeneration = c(10, 11, 12, 13, 14, 15),
    restoration = c(2, 3, 4, 5, 6, 7),
    additions = c(0, 0, 1, 1, 1, 1),
    extraction = c(12, 11, 10, 9, 8, 7),
    degradation = c(5, 5, 5, 4, 4, 3),
    damages = c(2, 1, 2, 3, 3, 2),
    closing_stock = c(993, 990, 990, 993, 999, 1010),
    stringsAsFactors = FALSE
  )
  as_catalyst_dataset(
    data,
    id = "climate-test-dataset",
    title = "Climate accounting test dataset",
    time_field = "year",
    entity_fields = "region",
    units = list(
      year = "year",
      emissions = "MtCO2e",
      removals = "MtCO2e",
      energy = "PJ",
      gdp = "currency_index",
      population = "million_persons",
      opening_stock = "natural_capital_index",
      closing_stock = "natural_capital_index"
    ),
    source = dataset_source(
      id = "climate-test-source",
      title = "Synthetic climate accounting fixture",
      publisher = "Content Catalyst LLC",
      license = "CC0-1.0"
    ),
    required_fields = c("region", "year", "emissions", "removals", "energy", "gdp", "population")
  )
}

sample_emissions_inventory <- function() {
  as_emissions_inventory(
    sample_climate_dataset(),
    emissions_field = "emissions",
    removals_field = "removals",
    time_field = "year",
    entity_fields = "region",
    energy_field = "energy",
    gdp_field = "gdp",
    population_field = "population",
    accounting_basis = "period_total",
    gwp_basis = "AR6 GWP100 synthetic CO2e fixture"
  )
}

sample_natural_capital_account <- function() {
  dataset <- sample_climate_dataset()
  natural_capital_from_dataset(
    dataset,
    opening_field = "opening_stock",
    regeneration_field = "regeneration",
    restoration_field = "restoration",
    additions_field = "additions",
    extraction_field = "extraction",
    degradation_field = "degradation",
    damages_field = "damages",
    closing_field = "closing_stock",
    time_field = "year",
    entity_field = "region",
    unit = "natural_capital_index"
  )
}
