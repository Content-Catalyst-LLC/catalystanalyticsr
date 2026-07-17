sample_catalyst_dataset <- function() {
  data <- data.frame(
    year = c(2020, 2021, 2022, 2020, 2021, 2022),
    region = c("North", "North", "North", "South", "South", "South"),
    gdp = c(100, 105, 111, 80, 84, 89),
    population = c(50, 51, 52, 44, 45, 46),
    emissions = c(40, 38, 35, 34, 33, 31),
    natural_capital = c(90, 91, 93, 82, 82.5, 84),
    gross_savings = c(24, 26, 29, 18, 19, 21),
    depreciation = c(8, 8.2, 8.5, 6.5, 6.7, 7),
    depletion = c(4, 3.8, 3.4, 5, 4.8, 4.3),
    damages = c(3, 3, 2.8, 3.5, 3.5, 3.3),
    education_investment = c(5, 5.2, 5.7, 3.8, 4, 4.4),
    stringsAsFactors = FALSE
  )
  as_catalyst_dataset(
    data,
    id = "test-dataset",
    title = "Test dataset",
    time_field = "year",
    entity_fields = "region",
    required_fields = c("year", "region", "gdp", "population", "emissions"),
    units = list(
      year = "year", gdp = "currency", population = "person",
      emissions = "tCO2e", natural_capital = "index",
      gross_savings = "currency", depreciation = "currency",
      depletion = "currency", damages = "currency",
      education_investment = "currency"
    ),
    source = dataset_source("test-source", "Test source", license = "CC0")
  )
}
