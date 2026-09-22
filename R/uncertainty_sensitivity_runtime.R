.uncertainty_sensitivity_contract_ref <- function() "sc.analytics-r.uncertainty-sensitivity-runtime.v1"

.uncertainty_sensitivity_methods <- function() {
  c("monte_carlo", "latin_hypercube", "morris", "sobol")
}

#' Uncertainty and sensitivity runtime manifest
#'
#' Declares the bounded computation surface used by Workspace. Platform Core
#' owns semantic interpretation and provenance binding; Workspace owns runtime
#' execution; Catalyst Analytics R performs registered numerical methods only.
#'
#' @return A runtime manifest list.
#' @export
uncertainty_sensitivity_runtime_manifest <- function() {
  list(
    schema_version = "1.0.0",
    contract = .uncertainty_sensitivity_contract_ref(),
    provider_key = "catalystanalyticsr",
    provider_version = .catalyst_package_version(),
    runtime = "r",
    execution_host = "workspace",
    methods = list(
      monte_carlo = list(kind = "ensemble", registered_method = "run_uncertainty", sampling = "monte_carlo"),
      latin_hypercube = list(kind = "ensemble", registered_method = "run_uncertainty", sampling = "latin_hypercube"),
      morris = list(kind = "screening", registered_method = "morris_sensitivity", estimator = "elementary_effects"),
      sobol = list(kind = "variance_based", registered_method = "sobol_sensitivity", first_order = "saltelli_2010", total_order = "jansen_1999")
    ),
    limits = list(
      minimum_samples = 4L,
      maximum_samples = 10000L,
      maximum_structured_evaluations = 20000L,
      maximum_uncertain_targets = 64L
    ),
    integration = list(
      core_provider_contract = "sc.core.analytical-runtime-provider.v1",
      statistical_diagnostics_contract = "sc.analytics-r.statistical-diagnostics-validation.v1",
      core_minimum_release = "3.3.0",
      core_uncertainty_evidence_target_release = "3.4.0",
      workspace_validated_release = "3.9.1"
    ),
    boundary = list(
      arbitrary_function_dispatch = FALSE,
      canonical_scenario_execution_only = TRUE,
      uncertainty_does_not_establish_truth = TRUE,
      sensitivity_does_not_establish_causality = TRUE,
      sensitivity_does_not_rank_policy_preferences = TRUE,
      core_does_not_execute_provider = TRUE,
      workspace_controls_execution = TRUE,
      human_review_required = TRUE
    )
  )
}

#' Create a governed uncertainty and sensitivity runtime request
#'
#' @param scenario Canonical Catalyst scenario.
#' @param method Runtime method: monte_carlo, latin_hypercube, morris, or sobol.
#' @param n Sample count or structured base size.
#' @param seed Reproducible random seed.
#' @param metrics Terminal indicator names. `NULL` uses the default runtime set.
#' @param thresholds Optional probability rules for ensemble methods.
#' @param integration_method Optional registered scenario integration method.
#' @param morris_delta Unit-interval perturbation used by Morris screening.
#' @param max_evaluations Maximum allowed model evaluations for structured designs.
#' @param continue_on_error Whether ensemble execution records failed samples.
#' @return A validated runtime request.
#' @export
uncertainty_sensitivity_runtime_request <- function(
  scenario,
  method = c("monte_carlo", "latin_hypercube", "morris", "sobol"),
  n = 256L,
  seed = 42L,
  metrics = NULL,
  thresholds = list(),
  integration_method = NULL,
  morris_delta = 0.1,
  max_evaluations = 20000L,
  continue_on_error = TRUE
) {
  scenario <- as_catalyst_scenario(scenario)
  method <- match.arg(method)
  request <- list(
    schema_version = "1.0.0",
    request_type = "catalyst_uncertainty_sensitivity_runtime_request",
    contract = .uncertainty_sensitivity_contract_ref(),
    scenario = scenario,
    method = method,
    n = as.integer(n),
    seed = as.integer(seed),
    metrics = metrics,
    thresholds = thresholds,
    integration_method = integration_method,
    morris_delta = as.numeric(morris_delta),
    max_evaluations = as.integer(max_evaluations),
    continue_on_error = continue_on_error,
    boundary = list(
      arbitrary_function_dispatch = FALSE,
      canonical_scenario_execution_only = TRUE,
      human_review_required = TRUE
    )
  )
  validate_uncertainty_sensitivity_runtime_request(request)
  class(request) <- c("catalyst_uncertainty_sensitivity_request", "list")
  request
}

#' Validate an uncertainty and sensitivity runtime request
#'
#' @param request Runtime request.
#' @return Invisibly returns `TRUE` when valid.
#' @export
validate_uncertainty_sensitivity_runtime_request <- function(request) {
  if (!is.list(request)) stop("`request` must be a list.", call. = FALSE)
  required <- c("schema_version", "request_type", "contract", "scenario", "method", "n", "seed", "max_evaluations", "continue_on_error", "boundary")
  missing <- setdiff(required, names(request))
  if (length(missing)) stop("Runtime request is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(request$schema_version, "1.0.0") || !identical(request$contract, .uncertainty_sensitivity_contract_ref())) stop("Unsupported uncertainty runtime contract.", call. = FALSE)
  if (!request$method %in% .uncertainty_sensitivity_methods()) stop("Unsupported uncertainty runtime method.", call. = FALSE)
  n <- as.integer(request$n)
  if (length(n) != 1L || is.na(n) || n < 4L || n > 10000L) stop("`n` must be between 4 and 10000.", call. = FALSE)
  max_eval <- as.integer(request$max_evaluations)
  if (length(max_eval) != 1L || is.na(max_eval) || max_eval < 1L || max_eval > 100000L) stop("`max_evaluations` must be between 1 and 100000.", call. = FALSE)
  .assert_flag(request$continue_on_error, "continue_on_error")
  .assert_scalar_number(request$morris_delta, "morris_delta", lower = 0.001, upper = 0.5)
  scenario <- as_catalyst_scenario(request$scenario)
  specs <- Filter(function(x) isTRUE(.normalize_uncertainty_spec(x)$enabled), scenario$uncertainty)
  if (!length(specs)) stop("The scenario requires at least one enabled uncertainty specification.", call. = FALSE)
  if (length(specs) > 64L) stop("At most 64 uncertain targets are allowed in the bounded runtime.", call. = FALSE)
  evaluations <- switch(request$method,
    morris = n * (length(specs) + 1L),
    sobol = n * (length(specs) + 2L),
    n
  )
  if (evaluations > max_eval) stop(sprintf("Requested design requires %s evaluations, above max_evaluations=%s.", evaluations, max_eval), call. = FALSE)
  if (!isFALSE(request$boundary$arbitrary_function_dispatch) || !isTRUE(request$boundary$canonical_scenario_execution_only)) stop("Runtime execution boundary is invalid.", call. = FALSE)
  invisible(TRUE)
}

.usr_enabled_specs <- function(scenario) {
  scenario <- as_catalyst_scenario(scenario)
  specs <- lapply(Filter(function(x) isTRUE(.normalize_uncertainty_spec(x)$enabled), scenario$uncertainty), .normalize_uncertainty_spec)
  if (!length(specs)) stop("The scenario requires enabled uncertainty specifications.", call. = FALSE)
  for (spec in specs) validate_uncertainty_spec(spec, scenario = scenario)
  specs
}

.usr_unit_design <- function(n, d, seed, lhs = FALSE) {
  .with_reproducible_seed(seed, {
    if (!lhs) return(matrix(stats::runif(n * d), nrow = n, ncol = d))
    out <- matrix(NA_real_, nrow = n, ncol = d)
    for (j in seq_len(d)) out[, j] <- (sample.int(n) - stats::runif(n)) / n
    out
  })
}

.usr_design_to_samples <- function(specs, design, sample_offset = 0L) {
  if (!is.matrix(design) || ncol(design) != length(specs)) stop("Design matrix does not match uncertainty specifications.", call. = FALSE)
  frame <- data.frame(sample_id = sample_offset + seq_len(nrow(design)), stringsAsFactors = FALSE)
  for (j in seq_along(specs)) {
    values <- .sample_uncertainty_distribution(specs[[j]], pmin(pmax(design[, j], .Machine$double.eps), 1 - .Machine$double.eps))
    frame[[specs[[j]]$target]] <- values
  }
  frame
}

.usr_resolve_metrics <- function(scenario, metrics, integration_method = NULL) {
  if (!is.null(metrics)) {
    if (!is.character(metrics) || !length(metrics) || any(!nzchar(metrics)) || anyDuplicated(metrics)) stop("`metrics` must contain unique indicator names.", call. = FALSE)
    return(metrics)
  }
  baseline <- run_catalyst_scenario(scenario, method = integration_method, include_phase_plane = FALSE, include_sensitivity = FALSE)
  .default_uncertainty_metrics(baseline)
}

.usr_evaluate_samples <- function(scenario, samples, metrics, integration_method = NULL, continue_on_error = FALSE) {
  rows <- list(); failures <- list()
  for (i in seq_len(nrow(samples))) {
    realization <- .scenario_from_uncertainty_sample(scenario, samples, i)
    result <- tryCatch(run_catalyst_scenario(realization, method = integration_method, include_phase_plane = FALSE, include_sensitivity = FALSE), error = function(e) e)
    if (inherits(result, "error")) {
      failures[[length(failures) + 1L]] <- data.frame(sample_id = samples$sample_id[i], message = conditionMessage(result), stringsAsFactors = FALSE)
      if (!continue_on_error) stop(sprintf("Structured sensitivity sample %s failed: %s", samples$sample_id[i], conditionMessage(result)), call. = FALSE)
      next
    }
    rows[[length(rows) + 1L]] <- .uncertainty_metric_rows(result, samples$sample_id[i], metrics)
  }
  list(
    results = if (length(rows)) do.call(rbind, rows) else data.frame(sample_id = integer(), metric = character(), value = numeric(), unit = character(), direction = character(), stringsAsFactors = FALSE),
    failures = if (length(failures)) do.call(rbind, failures) else data.frame(sample_id = integer(), message = character(), stringsAsFactors = FALSE)
  )
}

.usr_metric_vector <- function(results, sample_ids, metric) {
  rows <- results[results$metric == metric, c("sample_id", "value"), drop = FALSE]
  idx <- match(sample_ids, rows$sample_id)
  if (anyNA(idx)) stop("Structured sensitivity design is missing model outputs.", call. = FALSE)
  as.numeric(rows$value[idx])
}

#' Morris elementary-effects sensitivity screening
#'
#' @param scenario Canonical Catalyst scenario.
#' @param n Number of independent base trajectories.
#' @param seed Reproducible seed.
#' @param metrics Terminal indicator names.
#' @param delta Unit-interval perturbation.
#' @param integration_method Optional registered scenario integration method.
#' @param max_evaluations Evaluation budget.
#' @return A governed Morris sensitivity result.
#' @export
morris_sensitivity <- function(scenario, n = 32L, seed = 42L, metrics = NULL, delta = 0.1, integration_method = NULL, max_evaluations = 20000L) {
  scenario <- as_catalyst_scenario(scenario)
  specs <- .usr_enabled_specs(scenario); d <- length(specs); n <- as.integer(n)
  .assert_scalar_number(delta, "delta", lower = 0.001, upper = 0.5)
  if (n < 4L || n * (d + 1L) > max_evaluations) stop("Morris design exceeds the bounded evaluation budget.", call. = FALSE)
  metrics <- .usr_resolve_metrics(scenario, metrics, integration_method)
  base_u <- .usr_unit_design(n, d, seed, lhs = TRUE)
  base_u <- pmin(base_u, 1 - delta)
  base_samples <- .usr_design_to_samples(specs, base_u, 0L)
  base_eval <- .usr_evaluate_samples(scenario, base_samples, metrics, integration_method, FALSE)$results
  effects <- list(); all_results <- list(base_eval)
  next_offset <- n
  for (j in seq_len(d)) {
    plus_u <- base_u; plus_u[, j] <- pmin(1, plus_u[, j] + delta)
    plus_samples <- .usr_design_to_samples(specs, plus_u, next_offset)
    plus_eval <- .usr_evaluate_samples(scenario, plus_samples, metrics, integration_method, FALSE)$results
    all_results[[length(all_results) + 1L]] <- plus_eval
    for (metric in metrics) {
      y0 <- .usr_metric_vector(base_eval, base_samples$sample_id, metric)
      y1 <- .usr_metric_vector(plus_eval, plus_samples$sample_id, metric)
      x0 <- base_samples[[specs[[j]]$target]]; x1 <- plus_samples[[specs[[j]]$target]]
      denom <- x1 - x0
      ee <- ifelse(abs(denom) > sqrt(.Machine$double.eps), (y1 - y0) / denom, NA_real_)
      valid <- is.finite(ee)
      effects[[length(effects) + 1L]] <- data.frame(
        target = specs[[j]]$target, metric = metric,
        mu = if (any(valid)) mean(ee[valid]) else NA_real_,
        mu_star = if (any(valid)) mean(abs(ee[valid])) else NA_real_,
        sigma = if (sum(valid) > 1L) stats::sd(ee[valid]) else NA_real_,
        n_effects = sum(valid), method = "morris_elementary_effects", stringsAsFactors = FALSE
      )
    }
    next_offset <- next_offset + n
  }
  structure(list(
    schema_version = "1.0.0", contract = .uncertainty_sensitivity_contract_ref(), method = "morris",
    scenario_ref = scenario$id, sensitivity = do.call(rbind, effects),
    design = list(trajectories = n, targets = d, delta = delta, evaluations = n * (d + 1L), seed = as.integer(seed)),
    provenance = list(package_version = .catalyst_package_version(), created_at = .utc_now()),
    boundary = list(sensitivity_does_not_establish_causality = TRUE, no_automatic_parameter_importance_verdict = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_uncertainty_sensitivity_result", "list"))
}

#' Sobol first-order and total-order sensitivity analysis
#'
#' @param scenario Canonical Catalyst scenario.
#' @param n Base sample size.
#' @param seed Reproducible seed.
#' @param metrics Terminal indicator names.
#' @param integration_method Optional registered scenario integration method.
#' @param max_evaluations Evaluation budget.
#' @return A governed Sobol sensitivity result.
#' @export
sobol_sensitivity <- function(scenario, n = 128L, seed = 42L, metrics = NULL, integration_method = NULL, max_evaluations = 20000L) {
  scenario <- as_catalyst_scenario(scenario)
  specs <- .usr_enabled_specs(scenario); d <- length(specs); n <- as.integer(n)
  if (n < 4L || n * (d + 2L) > max_evaluations) stop("Sobol design exceeds the bounded evaluation budget.", call. = FALSE)
  metrics <- .usr_resolve_metrics(scenario, metrics, integration_method)
  A <- .usr_unit_design(n, d, seed, lhs = FALSE)
  B <- .usr_unit_design(n, d, seed + 104729L, lhs = FALSE)
  samples_a <- .usr_design_to_samples(specs, A, 0L)
  samples_b <- .usr_design_to_samples(specs, B, n)
  eval_a <- .usr_evaluate_samples(scenario, samples_a, metrics, integration_method, FALSE)$results
  eval_b <- .usr_evaluate_samples(scenario, samples_b, metrics, integration_method, FALSE)$results
  sensitivity <- list(); offset <- 2L * n
  for (j in seq_len(d)) {
    AB <- A; AB[, j] <- B[, j]
    samples_ab <- .usr_design_to_samples(specs, AB, offset)
    eval_ab <- .usr_evaluate_samples(scenario, samples_ab, metrics, integration_method, FALSE)$results
    for (metric in metrics) {
      ya <- .usr_metric_vector(eval_a, samples_a$sample_id, metric)
      yb <- .usr_metric_vector(eval_b, samples_b$sample_id, metric)
      yab <- .usr_metric_vector(eval_ab, samples_ab$sample_id, metric)
      variance <- stats::var(c(ya, yb))
      if (!is.finite(variance) || variance <= .Machine$double.eps) {
        first <- total <- NA_real_
      } else {
        first <- mean(yb * (yab - ya)) / variance
        total <- mean((ya - yab)^2) / (2 * variance)
      }
      sensitivity[[length(sensitivity) + 1L]] <- data.frame(
        target = specs[[j]]$target, metric = metric,
        first_order = first, total_order = total,
        variance = variance, n = n,
        first_order_estimator = "saltelli_2010", total_order_estimator = "jansen_1999",
        stringsAsFactors = FALSE
      )
    }
    offset <- offset + n
  }
  structure(list(
    schema_version = "1.0.0", contract = .uncertainty_sensitivity_contract_ref(), method = "sobol",
    scenario_ref = scenario$id, sensitivity = do.call(rbind, sensitivity),
    design = list(base_samples = n, targets = d, evaluations = n * (d + 2L), seed = as.integer(seed)),
    provenance = list(package_version = .catalyst_package_version(), created_at = .utc_now()),
    boundary = list(sensitivity_does_not_establish_causality = TRUE, indices_are_estimates = TRUE, no_automatic_parameter_importance_verdict = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_uncertainty_sensitivity_result", "list"))
}

#' Build a Core-ready uncertainty and sensitivity evidence bundle
#'
#' @param result A catalyst uncertainty run or structured sensitivity result.
#' @param analysis_ref Optional analysis reference.
#' @param source_refs Source/evidence references.
#' @param limitations Human-readable limitations.
#' @return A governed evidence bundle.
#' @export
uncertainty_sensitivity_evidence_bundle <- function(result, analysis_ref = NULL, source_refs = character(), limitations = character()) {
  if (!inherits(result, "catalyst_uncertainty_run") && !inherits(result, "catalyst_uncertainty_sensitivity_result")) stop("Unsupported uncertainty/sensitivity result.", call. = FALSE)
  if (!is.null(analysis_ref)) .assert_single_string(analysis_ref, "analysis_ref")
  method <- if (inherits(result, "catalyst_uncertainty_run")) result$meta$sampling else result$method
  summary <- if (inherits(result, "catalyst_uncertainty_run")) result$summary else data.frame()
  sensitivity <- if (inherits(result, "catalyst_uncertainty_run")) result$sensitivity else result$sensitivity
  bundle <- structure(list(
    schema_version = "1.0.0",
    evidence_type = "catalyst_uncertainty_sensitivity_evidence",
    contract = .uncertainty_sensitivity_contract_ref(),
    analysis_ref = analysis_ref,
    method = method,
    summary = summary,
    sensitivity = sensitivity,
    source_refs = unname(as.character(source_refs)),
    limitations = unname(as.character(limitations)),
    provenance = list(provider_key = "catalystanalyticsr", provider_version = .catalyst_package_version(), runtime = "r", execution_host = "workspace", created_at = .utc_now()),
    boundary = list(
      uncertainty_is_evidence_not_truth = TRUE,
      sensitivity_does_not_establish_causality = TRUE,
      no_automatic_policy_preference = TRUE,
      no_automatic_scientific_validity_certification = TRUE,
      human_review_required = TRUE
    )
  ), class = c("catalyst_uncertainty_sensitivity_evidence", "list"))
  validate_uncertainty_sensitivity_evidence_bundle(bundle)
  bundle
}

#' Validate an uncertainty and sensitivity evidence bundle
#'
#' @param bundle Evidence bundle.
#' @return Invisibly returns `TRUE` when valid.
#' @export
validate_uncertainty_sensitivity_evidence_bundle <- function(bundle) {
  if (!is.list(bundle)) stop("`bundle` must be a list.", call. = FALSE)
  required <- c("schema_version", "evidence_type", "contract", "method", "summary", "sensitivity", "source_refs", "limitations", "provenance", "boundary")
  missing <- setdiff(required, names(bundle)); if (length(missing)) stop("Evidence bundle is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(bundle$schema_version, "1.0.0") || !identical(bundle$contract, .uncertainty_sensitivity_contract_ref())) stop("Unsupported uncertainty evidence contract.", call. = FALSE)
  if (!bundle$method %in% .uncertainty_sensitivity_methods()) stop("Unsupported evidence method.", call. = FALSE)
  if (!isTRUE(bundle$boundary$uncertainty_is_evidence_not_truth) || !isTRUE(bundle$boundary$sensitivity_does_not_establish_causality) || !isTRUE(bundle$boundary$human_review_required)) stop("Uncertainty evidence boundary is invalid.", call. = FALSE)
  invisible(TRUE)
}

#' Execute the bounded uncertainty and sensitivity runtime
#'
#' @param request Runtime request created by `uncertainty_sensitivity_runtime_request()`.
#' @return A Core-ready uncertainty/sensitivity evidence bundle.
#' @export
run_uncertainty_sensitivity_runtime <- function(request) {
  validate_uncertainty_sensitivity_runtime_request(request)
  scenario <- as_catalyst_scenario(request$scenario)
  result <- switch(request$method,
    monte_carlo = run_uncertainty(scenario, n = request$n, sampling = "monte_carlo", seed = request$seed, metrics = request$metrics, thresholds = request$thresholds, method = request$integration_method, continue_on_error = request$continue_on_error),
    latin_hypercube = run_uncertainty(scenario, n = request$n, sampling = "latin_hypercube", seed = request$seed, metrics = request$metrics, thresholds = request$thresholds, method = request$integration_method, continue_on_error = request$continue_on_error),
    morris = morris_sensitivity(scenario, n = request$n, seed = request$seed, metrics = request$metrics, delta = request$morris_delta, integration_method = request$integration_method, max_evaluations = request$max_evaluations),
    sobol = sobol_sensitivity(scenario, n = request$n, seed = request$seed, metrics = request$metrics, integration_method = request$integration_method, max_evaluations = request$max_evaluations)
  )
  uncertainty_sensitivity_evidence_bundle(result)
}

#' Serialize uncertainty/sensitivity evidence to JSON
#'
#' @param x Runtime evidence bundle.
#' @param pretty Pretty-print JSON.
#' @return JSON string.
#' @export
uncertainty_sensitivity_to_json <- function(x, pretty = TRUE) {
  validate_uncertainty_sensitivity_evidence_bundle(x)
  jsonlite::toJSON(unclass(x), auto_unbox = TRUE, null = "null", na = "null", dataframe = "rows", pretty = pretty)
}

#' Deserialize uncertainty/sensitivity evidence from JSON
#'
#' @param json JSON string.
#' @return A validated evidence bundle.
#' @export
uncertainty_sensitivity_from_json <- function(json) {
  .assert_single_string(json, "json")
  x <- jsonlite::fromJSON(json, simplifyVector = FALSE)
  class(x) <- c("catalyst_uncertainty_sensitivity_evidence", "list")
  validate_uncertainty_sensitivity_evidence_bundle(x)
  x
}

#' @export
print.catalyst_uncertainty_sensitivity_result <- function(x, ...) {
  cat("<catalyst_uncertainty_sensitivity_result>\n")
  cat("  method: ", x$method, "\n", sep = "")
  cat("  scenario: ", x$scenario_ref, "\n", sep = "")
  if (!is.null(x$design$evaluations)) cat("  evaluations: ", x$design$evaluations, "\n", sep = "")
  invisible(x)
}
