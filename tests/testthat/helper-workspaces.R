workspace_fixture <- function() {
  project <- project_fixture()
  workspace <- catalyst_workspace(
    "transition-workspace", "Transition Analytics Workspace",
    description = "Reusable projects, scenarios, parameter sets, and publication candidates.",
    owner = "Sustainable Catalyst", tags = c("transition", "reproducibility")
  )
  workspace <- workspace_add_project(workspace, project)
  workspace <- workspace_add_policy_package(
    workspace, "baseline-package", "Baseline policy package",
    scenario_ids = names(workspace$libraries$scenarios),
    parameter_set_ids = names(workspace$libraries$parameter_sets),
    description = "Reusable baseline scenario and parameter set."
  )
  workspace_snapshot(workspace, "workspace-snapshot-1", "Initial reusable workspace")
}
