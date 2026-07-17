test_that("workspace export writes portable project and library indexes", {
  workspace <- workspace_fixture()
  dir <- tempfile("workspace-export-")
  paths <- export_workspace(workspace, dir, prefix = "workspace", zip_bundle = TRUE)
  for (name in c("workspace", "workspace_manifest", "project_index", "scenario_library", "parameter_library", "run_history", "readme", "manifest", "zip")) {
    expect_true(file.exists(paths[[name]]), info = name)
  }
  manifest <- jsonlite::read_json(paths$manifest, simplifyVector = TRUE)
  expect_identical(manifest$schema_version, "1.0.0")
  expect_identical(manifest$package$version, "1.6.0")
  expect_identical(manifest$workspace_id, workspace$id)
  file_count <- if (is.data.frame(manifest$files)) nrow(manifest$files) else length(manifest$files)
  expect_gte(file_count, 7L)
  expect_identical(manifest$file_count, file_count)
  expect_true(manifest$integrity$complete)
})

test_that("workspace export can omit complete run results", {
  workspace <- workspace_fixture()
  dir <- tempfile("workspace-export-light-")
  paths <- export_workspace(workspace, dir, prefix = "workspace", include_project_results = FALSE, zip_bundle = FALSE)
  restored <- workspace_from_json(paths$workspace)
  run <- workspace_get_project(restored)$runs[[1L]]
  expect_true("result" %in% names(run))
  expect_null(run[["result", exact = TRUE]])
  expect_match(run$output_hash, "^[a-f0-9]{32}$")
})
