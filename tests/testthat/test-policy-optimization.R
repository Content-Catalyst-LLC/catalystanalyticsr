test_that("policy optimization contracts validate variables, objectives, and constraints", {
  spec <- policy_spec_fixture()
  expect_s3_class(spec, "catalyst_policy_optimization_spec")
  expect_true(validate_policy_optimization_spec(spec))
  expect_error(decision_variable("bad", "Bad", "policy$s", 2, 1), "less than")
  expect_error(policy_objective("target", "Target", "emissions", "target"), "require")
  expect_error(policy_constraint("range", "Range", "jobs", "between", lower = 10), "require")
})

test_that("optimization identifies feasible and Pareto policy choices", {
  result <- optimize_policy(policy_spec_fixture(), policy_evaluator_fixture)
  expect_s3_class(result, "catalyst_policy_optimization")
  expect_true(any(result$candidates$feasible))
  expect_true(nrow(policy_pareto_frontier(result)) >= 1L)
  expect_true(result$recommendation$metrics$emissions <= 70)
  expect_true(result$recommendation$metrics$jobs >= 48)
  expect_type(result$recommendation$metrics$jobs, "double")
  expect_length(result$recommendation$metrics$jobs, 1L)
  expect_true(all(c("emissions", "cost", "jobs") %in% names(result$recommendation$metrics)))
  expect_true(policy_feasible_region(result)$feasible_share > 0)
})

test_that("random search is reproducible", {
  one <- optimize_policy(policy_spec_fixture("random_search"), policy_evaluator_fixture)
  two <- optimize_policy(policy_spec_fixture("random_search"), policy_evaluator_fixture)
  expect_equal(one$candidates[, c("carbon_price", "investment")], two$candidates[, c("carbon_price", "investment")])
})

test_that("target-seeking scenarios preserve canonical contracts", {
  result <- target_seeking_scenario(comparison_scenarios()[[1L]], policy_spec_fixture(), policy_evaluator_fixture, id = "optimized-transition", title = "Optimized transition")
  expect_s3_class(result$scenario, "catalyst_scenario")
  expect_true(validate_catalyst_scenario(result$scenario))
  expect_equal(result$scenario$policy$e, result$optimization$recommendation$decisions$carbon_price)
  expect_equal(result$scenario$policy$a, result$optimization$recommendation$decisions$investment)
  expect_true(result$boundary$human_review_required)
})

test_that("cost-effectiveness and marginal abatement preserve transparent calculations", {
  options <- data.frame(option = c("efficiency", "renewables", "removals"), cost = c(20, 45, 90), effect = c(10, 25, 30), abatement = c(10, 20, 12))
  ce <- cost_effectiveness_analysis(options)
  mac <- marginal_abatement_curve(options)
  expect_s3_class(ce, "catalyst_cost_effectiveness")
  expect_s3_class(mac, "catalyst_marginal_abatement")
  expect_equal(mac$cost_per_unit, mac$cost / mac$abatement)
  expect_true(all(diff(mac$cost_per_unit) >= 0))
})

test_that("adaptive pathways generate review prompts without executing actions", {
  pathway <- policy_pathway_fixture()
  evidence <- data.frame(time = c(2027, 2030), emissions = c(92, 72), jobs = c(50, 44))
  evaluation <- evaluate_policy_pathway(pathway, evidence)
  expect_s3_class(pathway, "catalyst_policy_pathway")
  expect_true(any(evaluation$trigger_status$status == "triggered_for_review"))
  expect_true(evaluation$boundary$triggers_do_not_execute_actions)
  expect_equal(nrow(policy_sequence(pathway)), 3L)
})

test_that("robust pathway analysis reports normalized regret", {
  pathways <- list(policy_pathway_fixture("path-a"), policy_pathway_fixture("path-b"))
  performance <- data.frame(
    pathway_id = rep(c("path-a", "path-b"), each = 2),
    scenario_id = rep(c("rapid", "slow"), 2),
    emissions = c(50, 75, 58, 65), cost = c(180, 140, 150, 155)
  )
  robust <- robust_pathway_analysis(pathways, performance, policy_spec_fixture()$objectives, regret_tolerance = 0.6)
  expect_s3_class(robust, "catalyst_robust_pathway_analysis")
  expect_true(all(robust$performance$regret >= 0))
  expect_equal(sort(robust$summary$pathway_id), c("path-a", "path-b"))
})

test_that("workspaces retain optimization summaries and adaptive pathways", {
  optimization <- optimize_policy(policy_spec_fixture(), policy_evaluator_fixture)
  pathway <- policy_pathway_fixture()
  workspace <- catalyst_workspace("policy-workspace", "Policy Workspace")
  workspace <- workspace_add_policy_optimization(workspace, optimization)
  workspace <- workspace_add_policy_pathway(workspace, pathway)
  expect_equal(workspace_get_policy_optimization(workspace, optimization$id)$id, optimization$id)
  expect_s3_class(workspace_get_policy_pathway(workspace, pathway$id), "catalyst_policy_pathway")
  manifest <- workspace_manifest(workspace)
  expect_equal(manifest$counts$policy_optimizations, 1L)
  expect_equal(manifest$counts$policy_pathways, 1L)
})
