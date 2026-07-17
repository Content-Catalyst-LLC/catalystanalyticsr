test_that("workspace indexes projects and reusable libraries", {
  workspace <- workspace_fixture()
  expect_s3_class(workspace, "catalyst_workspace")
  expect_true(validate_catalyst_workspace(workspace))
  expect_equal(length(workspace$projects), 1L)
  expect_equal(length(workspace$libraries$scenarios), 1L)
  expect_equal(length(workspace$libraries$parameter_sets), 1L)
  expect_equal(length(workspace$libraries$policy_packages), 1L)
  expect_equal(workspace$active_project_id, names(workspace$projects)[1L])
  expect_match(workspace_fingerprint(workspace), "^[a-f0-9]{32}$")
})

test_that("scenario library supports retrieval and cloning", {
  workspace <- workspace_fixture()
  source_id <- names(workspace$libraries$scenarios)[1L]
  source <- workspace_get_scenario(workspace, source_id)
  expect_s3_class(source, "catalyst_scenario")
  workspace <- workspace_clone_scenario(
    workspace, source_id, "transition-clone", "transition-clone",
    title = "Transition clone", role = "intervention"
  )
  clone <- workspace_get_scenario(workspace, "transition-clone")
  expect_equal(clone$id, "transition-clone")
  expect_equal(clone$role, "intervention")
  expect_false(identical(scenario_fingerprint(source), scenario_fingerprint(clone)))
  expect_equal(nrow(workspace_list_scenarios(workspace)), 2L)
})

test_that("workspace snapshots restore complete state", {
  workspace <- workspace_fixture()
  original <- workspace_fingerprint(workspace)
  project_id <- workspace$active_project_id
  changed <- workspace_remove_project(workspace, project_id)
  expect_equal(length(changed$projects), 0L)
  expect_true("active_project_id" %in% names(changed))
  expect_null(changed[["active_project_id", exact = TRUE]])
  restored <- workspace_restore_snapshot(changed, "workspace-snapshot-1")
  expect_equal(length(restored$projects), 1L)
  expect_equal(restored$active_project_id, project_id)
  expect_equal(workspace_fingerprint(restored), original)
})

test_that("workspace JSON round trip preserves projects and libraries", {
  workspace <- workspace_fixture()
  path <- tempfile(fileext = ".json")
  workspace_to_json(workspace, path)
  restored <- workspace_from_json(path)
  expect_s3_class(restored, "catalyst_workspace")
  expect_s3_class(workspace_get_project(restored), "catalyst_project")
  expect_s3_class(workspace_get_scenario(restored, names(restored$libraries$scenarios)[1L]), "catalyst_scenario")
  expect_equal(workspace_manifest(restored)$counts$projects, 1L)
})

test_that("workspace consolidates run history and project comparison", {
  workspace <- workspace_fixture()
  history <- workspace_run_history(workspace)
  comparison <- workspace_compare_projects(workspace)
  expect_equal(nrow(history), 1L)
  expect_equal(history$status[1L], "completed")
  expect_equal(nrow(comparison), 1L)
  expect_equal(comparison$runs[1L], 1L)
  expect_equal(comparison$completed_runs[1L], 1L)
})

test_that("workspace validates library references", {
  workspace <- catalyst_workspace("validation-workspace", "Validation Workspace")
  expect_error(workspace_add_policy_package(workspace, "invalid", "Invalid", scenario_ids = "missing"), "Unknown policy-package scenarios")
  expect_error(workspace_get_project(workspace), "Project is not present")
})


test_that("empty workspace JSON round trip preserves nullable active project", {
  workspace <- catalyst_workspace("empty-workspace", "Empty Workspace")
  path <- tempfile(fileext = ".json")
  workspace_to_json(workspace, path)
  restored <- workspace_from_json(path)
  expect_true("active_project_id" %in% names(restored))
  expect_null(restored[["active_project_id", exact = TRUE]])
  expect_true(validate_catalyst_workspace(restored))
})

test_that("workspace snapshot identity survives JSON round trips", {
  workspace <- workspace_fixture()
  original <- workspace_fingerprint(workspace)
  path <- tempfile(fileext = ".json")
  workspace_to_json(workspace, path)
  imported <- workspace_from_json(path)
  changed <- workspace_remove_project(imported, imported$active_project_id)
  restored <- workspace_restore_snapshot(changed, "workspace-snapshot-1")
  expect_equal(workspace_fingerprint(restored), original)
  expect_false(grepl("restored_workspace_fingerprint", paste(readLines(path, warn = FALSE), collapse = "\n"), fixed = TRUE))
})

test_that("semantic workspace changes clear restored fingerprint identity", {
  workspace <- workspace_fixture()
  original <- workspace_fingerprint(workspace)
  changed <- workspace_remove_project(workspace, workspace$active_project_id)
  restored <- workspace_restore_snapshot(changed, "workspace-snapshot-1")
  source_id <- names(restored$libraries$scenarios)[1L]
  updated <- workspace_clone_scenario(
    restored, source_id, "restored-clone", "restored-clone",
    title = "Restored clone", role = "intervention"
  )
  expect_false(identical(workspace_fingerprint(updated), original))
  expect_null(updated[[".restored_workspace_fingerprint", exact = TRUE]])
})
