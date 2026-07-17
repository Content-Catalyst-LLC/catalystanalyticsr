project_fixture <- function() {
  scenarios <- comparison_scenarios()
  baseline <- scenarios[[1L]]
  run <- run_catalyst_scenario(baseline, include_phase_plane = FALSE, include_sensitivity = FALSE)
  project <- catalyst_project(
    "transition-evidence", "Transition evidence project",
    description = "Compare a governed baseline with a transition pathway and preserve the complete analytical record.",
    owner = "Sustainable Catalyst",
    scope = list(geography = "WORLD", sector = "all", period = "0-6 years"),
    tags = c("transition", "reproducibility")
  )
  project <- project_add_scenario(project, baseline)
  project <- project_add_dataset(project, sample_catalyst_dataset())
  project <- project_add_model(project, get_catalyst_model("khncpa", "1.0.0"))
  project <- project_add_parameter_set(project, "baseline-parameters", list(regen = 0.02, emissions_intensity = 0.30), "khncpa", "1.0.0", "Baseline parameter set")
  project <- project_add_run(project, run, "baseline-run", "Baseline model run", scenario_ids = baseline$id, parameter_set_id = "baseline-parameters")
  project <- project_add_note(project, "interpretation-1", "The baseline remains within the declared educational scope.", "Analyst", "baseline-run")
  project <- project_add_review(project, "review-1", "Reviewer", "approved", "Approved for publication as an educational reproducibility record.", run_ids = "baseline-run")
  project_snapshot(project, "snapshot-1", "Publication candidate")
}
