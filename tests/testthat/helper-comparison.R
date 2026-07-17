comparison_scenarios <- function() {
  created_at <- "2026-07-16T00:00:00Z"
  list(
    catalyst_scenario(
      title = "Reference baseline",
      id = "reference-baseline",
      role = "baseline",
      times = 0:6,
      policy = list(s = 0.18, e = 0.03, a = 0.01),
      parameters = list(emissions_intensity = 0.30, regen = 0.02),
      constraints = list(emissions_budget = 2),
      metadata = list(created_at = created_at)
    ),
    catalyst_scenario(
      title = "Transition policy",
      id = "transition-policy",
      role = "intervention",
      times = 0:6,
      policy = list(s = 0.24, e = 0.07, a = 0.10),
      parameters = list(emissions_intensity = 0.12, regen = 0.05),
      constraints = list(emissions_budget = 2),
      metadata = list(created_at = created_at)
    ),
    catalyst_scenario(
      title = "Low investment counterfactual",
      id = "low-investment",
      role = "counterfactual",
      times = 0:6,
      policy = list(s = 0.10, e = 0.01, a = 0),
      parameters = list(emissions_intensity = 0.36, regen = 0.01),
      constraints = list(emissions_budget = 2),
      metadata = list(created_at = created_at)
    )
  )
}
