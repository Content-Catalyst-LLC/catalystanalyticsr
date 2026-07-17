test_that("institutional workflow enforces collaborative roles and review lifecycle", {
  project <- project_fixture()
  actors <- list(
    governance_actor("analyst", "Analyst", "analyst"),
    governance_actor("reviewer", "Reviewer", "reviewer"),
    governance_actor("approver", "Approver", "approver"),
    governance_actor("publisher", "Publisher", "publisher")
  )
  workflow <- institutional_governance_workflow(project, "review-1", "institution-1", "Institution One", actors)
  workflow <- assign_institutional_review(workflow, "assignment-1", "reviewer", assigned_by = NULL)
  workflow <- add_review_comment(workflow, "comment-1", "reviewer", "Document the baseline source.", severity = "major")
  workflow <- submit_change_request(workflow, "change-1", "reviewer", "Document baseline", "Add source and uncertainty method.", priority = "high")
  expect_error(sign_analytical_release(workflow, "release-1", "publisher", "Release 1", list(report = "abc")), "Open change requests")
  workflow <- resolve_change_request(workflow, "change-1", "analyst", "Source and uncertainty method added.")
  workflow <- record_governance_approval(workflow, "approval-1", "approver", "approved")
  workflow <- sign_analytical_release(workflow, "release-1", "publisher", "Release 1", list(report = "abc"))
  expect_identical(workflow$status, "signed")
  expect_match(workflow$signed_releases$`release-1`$signature, "^[a-f0-9]{32}$")
  expect_identical(governance_summary(workflow)$open_change_requests, 0L)
  expect_gte(nrow(governance_audit_log(workflow)), 7L)
})

test_that("governance JSON and workspace storage preserve contracts", {
  project <- project_fixture()
  actors <- list(governance_actor("reviewer", "Reviewer", c("reviewer", "administrator")))
  workflow <- institutional_governance_workflow(project, "review-json", "institution-1", "Institution One", actors)
  restored <- governance_from_json(governance_to_json(workflow))
  expect_s3_class(restored, "catalyst_institutional_governance")
  expect_identical(restored$id, workflow$id)
  workspace <- workspace_add_institutional_governance(catalyst_workspace("governed-workspace", "Governed workspace"), workflow)
  expect_identical(workspace_get_institutional_governance(workspace, "review-json")$project$id, project$id)
  expect_identical(workspace_manifest(workspace)$counts$institutional_governance, 1L)
})

test_that("institutional governance export writes review, signature, audit, and integrity artifacts", {
  project <- project_fixture()
  actors <- list(
    governance_actor("analyst", "Analyst", "analyst"),
    governance_actor("approver", "Approver", c("approver", "administrator")),
    governance_actor("publisher", "Publisher", "publisher")
  )
  workflow <- institutional_governance_workflow(project, "review-export", "institution-1", "Institution One", actors)
  workflow <- record_governance_approval(workflow, "approval-1", "approver", "approved")
  workflow <- sign_analytical_release(workflow, "release-1", "publisher", "Release 1", list(report = "abc"))
  out <- tempfile("institutional-governance-")
  paths <- export_institutional_governance(workflow, out, zip_bundle = FALSE)
  expect_true(all(vapply(paths[c("workflow", "summary", "review_assignments", "comments", "change_requests", "approvals", "signed_releases", "audit", "manifest")], file.exists, logical(1))))
  manifest <- jsonlite::fromJSON(paths$manifest, simplifyVector = FALSE)
  expect_identical(manifest$package$version, "1.6.0")
  expect_true(manifest$boundary$human_approval_required)
  expect_false(manifest$boundary$automated_publication)
})

test_that("restricted access policy blocks prohibited publication and export", {
  project <- project_fixture()
  actors <- list(governance_actor("approver", "Approver", c("approver", "administrator")), governance_actor("publisher", "Publisher", "publisher"))
  policy <- restricted_access_policy("restricted-policy", "restricted", export_allowed = FALSE, publication_allowed = FALSE)
  workflow <- institutional_governance_workflow(project, "restricted-review", "institution-1", "Institution One", actors, access_policy = policy)
  workflow <- record_governance_approval(workflow, "approval-1", "approver", "approved")
  expect_error(sign_analytical_release(workflow, "release-1", "publisher", "Release 1", list(report = "abc")), "prohibits publication")
  expect_error(export_institutional_governance(workflow, tempfile("restricted-")), "prohibits export")
})
