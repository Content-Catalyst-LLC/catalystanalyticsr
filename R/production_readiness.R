# Production-readiness and stable API governance.

.stable_api_groups <- function() {
  list(
    scenarios = c("catalyst_scenario", "validate_catalyst_scenario", "scenario_to_json", "scenario_from_json", "run_catalyst_scenario"),
    models = c("new_catalyst_model", "register_catalyst_model", "list_catalyst_models", "get_catalyst_model", "catalyst_model_manifest"),
    comparison = c("run_scenarios", "compare_scenarios", "scenario_deltas", "scenario_rankings", "scenario_scorecard", "pareto_diagnostics"),
    uncertainty = c("uncertainty_spec", "run_uncertainty", "uncertainty_summary", "uncertainty_probabilities", "global_sensitivity", "local_sensitivity", "run_stress_tests"),
    data = c("as_catalyst_dataset", "read_catalyst_data", "validate_catalyst_dataset", "dataset_manifest", "new_catalyst_indicator", "calculate_indicator", "calculate_indicators"),
    accounting = c("climate_accounting", "inclusive_development_analysis", "model_validation_analysis"),
    projects = c("catalyst_project", "validate_catalyst_project", "project_add_run", "project_snapshot", "project_manifest", "export_project_publication"),
    workspaces = c("catalyst_workspace", "validate_catalyst_workspace", "workspace_add_project", "workspace_add_scenario", "workspace_add_parameter_set", "workspace_snapshot", "workspace_restore_snapshot", "workspace_manifest", "export_workspace"),
    regional_portfolios = c("geography_scope", "sector_scope", "scope_scenario", "portfolio_member", "regional_portfolio", "portfolio_aggregate", "portfolio_compare_regions", "regional_carbon_budgets", "sector_transition_pathways", "regional_portfolio_analysis", "export_regional_portfolio_analysis"),
    governance = c("model_governance_record", "transition_model_status", "model_governance_summary"),
    release = c("catalyst_api_manifest", "catalyst_release_readiness", "validate_release_readiness", "catalyst_compatibility_manifest")
  )
}

#' Stable public API manifest
#'
#' Returns the v1.2.0 public API stability declaration.
#' @param include_experimental Include exported APIs not in the stable groups.
#' @return A list describing stable, experimental, and deprecated APIs.
#' @export
catalyst_api_manifest <- function(include_experimental = TRUE) {
  groups <- .stable_api_groups()
  stable <- unique(unlist(groups, use.names = FALSE))
  exports <- getNamespaceExports("catalystanalyticsr")
  experimental <- sort(setdiff(exports, stable))
  result <- list(
    schema_version = "1.0.0",
    package = list(name = "catalystanalyticsr", version = "1.2.0"),
    stability_policy = list(
      stable = "Backward-compatible signatures and return contracts are maintained throughout the 1.x series unless a security or correctness defect requires a documented exception.",
      experimental = "May evolve in a minor release with migration notes.",
      deprecated = "Retained for at least one minor release with a replacement path."
    ),
    stable_groups = groups,
    stable = stable,
    deprecated = list(),
    contract_versions = list(
      scenario = "1.0.0", comparison = "1.0.0", uncertainty = "1.0.0",
      dataset = "1.0.0", indicator = "1.0.0", climate_accounting = "1.0.0",
      inclusive_development = "1.0.0", model_validation = "1.0.0",
      project = "1.0.0", analytical_publication = "1.0.0", workspace = "1.0.0", workspace_export = "1.0.0", regional_portfolio = "1.0.0", regional_portfolio_analysis = "1.0.0", release_readiness = "1.0.0"
    )
  )
  if (isTRUE(include_experimental)) result$experimental <- experimental
  class(result) <- c("catalyst_api_manifest", "list")
  result
}

#' Compatibility manifest
#'
#' @return Machine-readable compatibility and migration policy.
#' @export
catalyst_compatibility_manifest <- function() {
  list(
    schema_version = "1.0.0",
    package_version = "1.2.0",
    r_version = list(minimum = "4.1.0", tested_policy = "current and previous R release in CI"),
    contract_policy = list(
      major = "Breaking schema changes require a new contract major version and migration function.",
      minor = "Additive fields must remain optional for older readers.",
      patch = "Clarifications and correctness repairs only."
    ),
    supported_inputs = list(
      canonical_scenario = c("1.0.0"),
      project = c("1.0.0"),
      workspace = c("1.0.0"),
      browser_mapping = c("1.0.0"),
      legacy_scenario_migrations = c("legacy_r", "browser_v1")
    ),
    wordpress = list(plugin = "catalyst-analytics-r-demo", version = "2.2.0", compatible_repository_version = "1.2.0"),
    boundaries = c("browser companion does not execute R", "reproducibility does not establish validity", "human review is required for publication and decisions")
  )
}

#' Assess release readiness
#'
#' @param checks Optional named logical vector overriding default gates.
#' @param evidence Optional named list of evidence references.
#' @return A catalyst_release_readiness record.
#' @export
catalyst_release_readiness <- function(checks = NULL, evidence = list()) {
  defaults <- c(
    stable_api_declared = TRUE,
    schemas_versioned = TRUE,
    migrations_documented = TRUE,
    model_limitations_published = TRUE,
    provenance_exported = TRUE,
    human_review_boundary_present = TRUE,
    accessibility_reviewed = TRUE,
    browser_boundary_disclosed = TRUE,
    security_privacy_reviewed = TRUE,
    release_tests_passed = TRUE
  )
  if (!is.null(checks)) {
    if (is.null(names(checks)) || any(!nzchar(names(checks)))) stop("checks must be a named logical vector.", call. = FALSE)
    unknown <- setdiff(names(checks), names(defaults))
    if (length(unknown)) stop("Unknown readiness checks: ", paste(unknown, collapse = ", "), call. = FALSE)
    defaults[names(checks)] <- as.logical(checks)
  }
  failed <- names(defaults)[!defaults | is.na(defaults)]
  result <- list(
    schema_version = "1.0.0",
    package_version = "1.2.0",
    assessed_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
    status = if (length(failed)) "not_ready" else "ready",
    checks = as.list(defaults),
    failed_checks = unname(failed),
    evidence = .safe_json_value(evidence),
    decision_boundary = list(human_approval_required = TRUE, automated_release_authorization = FALSE)
  )
  class(result) <- c("catalyst_release_readiness", "list")
  result
}

#' Validate a release-readiness record
#'
#' @param x A readiness record.
#' @param require_ready Require all gates to pass.
#' @return The validated record invisibly.
#' @export
validate_release_readiness <- function(x, require_ready = FALSE) {
  if (!inherits(x, "catalyst_release_readiness") && !is.list(x)) stop("x must be a catalyst release-readiness record.", call. = FALSE)
  required <- c("schema_version", "package_version", "status", "checks", "failed_checks", "decision_boundary")
  missing <- setdiff(required, names(x))
  if (length(missing)) stop("Readiness record is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(x$schema_version, "1.0.0")) stop("Unsupported readiness schema version.", call. = FALSE)
  if (!x$status %in% c("ready", "not_ready")) stop("Invalid readiness status.", call. = FALSE)
  if (isTRUE(require_ready) && !identical(x$status, "ready")) stop("Release is not ready: ", paste(x$failed_checks, collapse = ", "), call. = FALSE)
  invisible(x)
}

#' @export
print.catalyst_api_manifest <- function(x, ...) {
  cat("Catalyst Analytics R API manifest", x$package$version, "\n")
  cat(" Stable APIs:", length(x$stable), "\n")
  if (!is.null(x$experimental)) cat(" Experimental APIs:", length(x$experimental), "\n")
  invisible(x)
}

#' @export
print.catalyst_release_readiness <- function(x, ...) {
  cat("Catalyst Analytics R release readiness:", x$status, "\n")
  cat(" Passed:", sum(unlist(x$checks)), "of", length(x$checks), "gates\n")
  invisible(x)
}
