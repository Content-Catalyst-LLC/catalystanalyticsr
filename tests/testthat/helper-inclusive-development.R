example_inclusive_development <- function() {
  time <- c(2025, 2030, 2035)
  entity <- rep("Example region", 3)
  produced <- capital_account(
    "produced", opening_stock = c(500, 535, 570), investment = c(55, 58, 62),
    depreciation = c(20, 23, 25), closing_stock = c(535, 570, 607),
    shadow_price = 1, time = time, entity = entity, unit = "wealth_index"
  )
  human <- capital_account(
    "human", opening_stock = c(400, 424, 450), investment = c(36, 39, 42),
    depreciation = c(12, 13, 14), closing_stock = c(424, 450, 478),
    shadow_price = 1.2, time = time, entity = entity, unit = "wealth_index"
  )
  natural <- capital_account(
    "natural", opening_stock = c(300, 298, 297), investment = c(12, 14, 16),
    depletion = c(8, 9, 9), damages = c(6, 6, 6), closing_stock = c(298, 297, 298),
    shadow_price = 1.5, time = time, entity = entity, unit = "wealth_index"
  )
  wealth <- inclusive_wealth_account(produced, human, natural, population = c(5, 5.15, 5.3))
  ans <- adjusted_net_savings_decomposition(
    gross_savings = c(80, 86, 94), produced_capital_depreciation = c(20, 23, 25),
    education_investment = c(22, 24, 27), health_investment = c(14, 15, 16),
    natural_resource_depletion = c(8, 9, 9), pollution_damages = c(5, 5, 4),
    climate_damages = c(6, 6, 6), gni = c(1000, 1100, 1220), time = time, entity = entity
  )
  hdi <- human_development_indicators(
    life_expectancy = c(72, 73, 74), expected_schooling = c(13, 13.5, 14),
    mean_schooling = c(9, 9.4, 9.8), income_per_capita = c(16000, 17500, 19300),
    time = time, entity = entity
  )
  distribution <- distributional_analysis(
    values = c(18, 31, 45, 63, 98), weights = rep(0.2, 5),
    groups = paste0("Quintile ", 1:5), indicator = "household_resources",
    social_floor = 25, entity = "Example region", time = 2035
  )
  intergenerational <- intergenerational_analysis(
    wealth = wealth$data$inclusive_wealth, population = wealth$data$population,
    time = time, target_per_capita = 310, entity = "Example region"
  )
  score_data <- data.frame(
    entity = entity, time = time,
    wealth_per_capita = wealth$data$inclusive_wealth_per_capita,
    adjusted_savings_rate = ans$adjusted_net_savings_percent_gni,
    human_development = hdi$human_development_index,
    natural_share = wealth$data$natural_share,
    stringsAsFactors = FALSE
  )
  definition <- composite_score_definition(
    "inclusive-development-score", "Inclusive development score",
    components = c("wealth_per_capita", "adjusted_savings_rate", "human_development", "natural_share"),
    weights = c(0.30, 0.25, 0.25, 0.20), directions = rep("higher", 4),
    lower_bounds = c(250, -5, 0.55, 0.15), upper_bounds = c(350, 15, 0.90, 0.35)
  )
  composite <- calculate_composite_score(score_data, definition, entity_fields = "entity", time_field = "time")
  composite$sensitivity <- composite_weight_sensitivity(score_data, definition, weight_shift = 0.20)
  inclusive_development_analysis(
    wealth, adjusted_net_savings = ans, human_development = hdi,
    distribution = distribution, intergenerational = intergenerational,
    composite = composite, analysis_id = "example-inclusive-development"
  )
}
