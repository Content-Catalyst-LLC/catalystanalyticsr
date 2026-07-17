test_that("public API manifest declares versioned read-only contracts", {
  manifest <- catalyst_public_api_manifest()
  expect_identical(manifest$api_version, "v1")
  expect_true(length(manifest$endpoints) >= 8L)
  expect_true(all(vapply(manifest$endpoints, function(endpoint) startsWith(endpoint$path, "/v1/"), logical(1))))
  expect_false(any(vapply(manifest$endpoints, function(endpoint) isTRUE(endpoint$side_effects), logical(1))))
})

test_that("API request and response envelopes validate and round trip through dispatch", {
  request <- api_request("health", context = list(test = TRUE))
  expect_s3_class(request, "catalyst_api_request")
  expect_true(validate_api_request(request))
  response <- dispatch_api_request(request)
  expect_s3_class(response, "catalyst_api_response")
  expect_identical(response$status, "ok")
  expect_identical(response$data$package_version, "1.5.0")
  expect_true(response$boundary$human_review_required)
})

test_that("scenario validation endpoint returns governed fingerprints", {
  scenario <- comparison_scenarios()[[1L]]
  response <- dispatch_api_request(api_request("scenario.validate", list(scenario = scenario)))
  expect_identical(response$status, "ok")
  expect_true(response$data$valid)
  expect_match(response$data$fingerprint, "^[a-f0-9]{32}$")
})

test_that("unknown or invalid endpoint payloads return error envelopes", {
  request <- api_request("scenario.validate", list())
  response <- dispatch_api_request(request)
  expect_identical(response$status, "error")
  expect_length(response$errors, 1L)
  expect_false(response$boundary$automated_decision_authorization)
})

test_that("all first-party handoffs preserve provenance and review boundaries", {
  project <- project_fixture()
  options <- list(
    site_intelligence = list(indicators = c("emissions")),
    research_lab = list(job_type = "batch_simulation"),
    workbench = list(formulas = list(carbon_intensity = "emissions / gdp")),
    catalyst_canvas = list(objectives = list(list(id = "reduce-emissions", title = "Reduce emissions")))
  )
  targets <- c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library")
  for (target in targets) {
    handoff <- platform_handoff(project, target, if (is.null(options[[target]])) list() else options[[target]])
    expect_s3_class(handoff, "catalyst_platform_handoff")
    expect_identical(handoff$target, target)
    expect_true(handoff$review$human_reviewer_required)
    expect_true(handoff$boundary$human_review_required)
    expect_identical(handoff$package_version, "1.5.0")
    restored <- handoff_from_json(handoff_to_json(handoff))
    expect_identical(restored$handoff_type, handoff$handoff_type)
  }
})

test_that("platform handoff export writes all target artifacts and integrity manifest", {
  project <- project_fixture()
  out <- tempfile("platform-handoffs-")
  paths <- export_platform_handoffs(project, out, zip_bundle = FALSE)
  expect_true(file.exists(paths$manifest)); expect_true(file.exists(paths$index)); expect_true(file.exists(paths$api_manifest))
  expect_true(all(vapply(c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library"), function(target) file.exists(paths[[target]]), logical(1))))
  manifest <- jsonlite::fromJSON(paths$manifest, simplifyVector = FALSE)
  expect_identical(manifest$package$version, "1.5.0")
  expect_gte(manifest$file_count, 9L)
  expect_false(manifest$boundary$automated_platform_action)
})

test_that("workspaces retain reusable platform handoffs", {
  project <- project_fixture()
  handoff <- site_intelligence_handoff(project, indicators = "emissions")
  workspace <- workspace_add_platform_handoff(catalyst_workspace("handoff-workspace", "Handoff workspace"), handoff)
  stored <- workspace_get_platform_handoff(workspace, paste(project$id, "site_intelligence", sep = "--"))
  expect_identical(stored$target, "site_intelligence")
  expect_identical(workspace_manifest(workspace)$counts$platform_handoffs, 1L)
})
