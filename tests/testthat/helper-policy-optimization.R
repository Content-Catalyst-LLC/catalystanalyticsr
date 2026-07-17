policy_evaluator_fixture <- function(decisions) {
  price <- decisions$carbon_price
  investment <- decisions$investment
  list(metrics = list(
    cost = 100 + 2 * price + 3 * investment,
    emissions = 120 - 4 * price - 5 * investment,
    jobs = 50 - 0.25 * price + 1.5 * investment,
    resilience = 40 + investment + 0.25 * price
  ))
}

policy_spec_fixture <- function(method = "grid") {
  policy_optimization_spec(
    "transition-optimization", "Transition policy optimization",
    variables = list(
      decision_variable("carbon_price", "Carbon price", "policy$e", 0, 20, initial = 10, step = 5, unit = "index"),
      decision_variable("investment", "Transition investment", "policy$a", 0, 20, initial = 10, step = 5, unit = "index")
    ),
    objectives = list(
      policy_objective("emissions", "Minimize emissions", "emissions", "minimize", weight = 0.65, unit = "MtCO2e"),
      policy_objective("cost", "Minimize cost", "cost", "minimize", weight = 0.35, unit = "index")
    ),
    constraints = list(
      policy_constraint("jobs-floor", "Protect jobs", "jobs", ">=", value = 48),
      policy_constraint("emissions-target", "Meet emissions target", "emissions", "<=", value = 70)
    ),
    method = method, max_evaluations = 100, seed = 13
  )
}

policy_pathway_fixture <- function(id = "adaptive-transition") {
  policy_pathway(
    id, "Adaptive transition pathway",
    stages = list(
      policy_stage("launch", "Launch", 2026, 2028,
        actions = list("Establish investment program"),
        triggers = list(adaptive_trigger("emissions-off-track", "Emissions off track", "emissions", ">", 85, "Review carbon price", 1))
      ),
      policy_stage("scale", "Scale", 2029, 2032,
        actions = list("Scale infrastructure"),
        triggers = list(adaptive_trigger("jobs-pressure", "Jobs pressure", "jobs", "<", 48, "Activate worker transition support", 1))
      ),
      policy_stage("consolidate", "Consolidate", 2033, 2035,
        actions = list("Consolidate proven measures"), triggers = list()
      )
    ),
    objectives = policy_spec_fixture()$objectives
  )
}
