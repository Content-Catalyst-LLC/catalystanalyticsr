#' Run a complete Catalyst Analytics scenario
#'
#' This is the "front door" for the package: one function that runs the model,
#' produces tidy outputs, makes plots, and returns a single structured result.
#'
#' @param times Numeric vector of times.
#' @param x0 Named numeric vector of initial states (K,H,N,C,P,A).
#' @param policy List of policy controls (s,e,a).
#' @param params List of model parameters.
#' @param scenario Scenario label.
#' @param method Integration method.
#' @param emissions_budget Optional single numeric budget for total allowed cumulative emissions (same units as the model's `emissions`). If provided, carbon_budget() is computed.
#' @param carbon_budget_value Deprecated alias for `emissions_budget` (kept for backwards compatibility).
#' @param include_phase_plane Logical. If TRUE, compute a phase plane.
#' @param include_sensitivity Logical. If TRUE, compute Jacobian sensitivities.
#'
#' @return A list with class "catalyst_run".
#' @export
#' @examples
#' times <- seq(0, 10, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' x <- catalyst_run(times, x0, include_phase_plane = FALSE, include_sensitivity = FALSE)
#' plot(x, which = "trajectory")
catalyst_run <- function(
  times,
  x0,
  policy = list(s = 0.20, e = 0.05, a = 0.00),
  params = list(),
  scenario = "baseline",
  method = c("rk4", "euler"),
  emissions_budget = NULL,
  carbon_budget_value = NULL,
  include_phase_plane = TRUE,
  include_sensitivity = TRUE
) {
  method <- match.arg(method)

  res <- simulate_dynamics(
    times = times,
    x0 = x0,
    policy = policy,
    params = params,
    method = method,
    scenario = scenario,
    return_long = TRUE
  )

  # Tidy indicator layer
  sdg <- sdg_indicators(res$trajectory_wide)

  # Carbon budget check (optional)
  if (!is.null(emissions_budget) && !is.null(carbon_budget_value)) {
    stop("Provide only one of `emissions_budget` or `carbon_budget_value` (legacy alias).")
  }
  if (is.null(emissions_budget)) emissions_budget <- carbon_budget_value

  cb <- NULL
  if (!is.null(emissions_budget)) {
    cb <- carbon_budget(res$trajectory_wide, budget = emissions_budget)
  }

  # Phase plane + overlay (optional)
  pp <- NULL
  if (isTRUE(include_phase_plane)) {
    state0 <- as.numeric(res$trajectory_wide[1, c("K", "H", "N", "C", "P", "A")])
    names(state0) <- c("K", "H", "N", "C", "P", "A")
    pp <- phase_plane(
      x_var = "K",
      y_var = "C",
      x_range = c(min(res$trajectory_wide$K, na.rm = TRUE), max(res$trajectory_wide$K, na.rm = TRUE)),
      y_range = c(min(res$trajectory_wide$C, na.rm = TRUE), max(res$trajectory_wide$C, na.rm = TRUE)),
      n = 15,
      t = times[1],
      state_fixed = state0,
      policy = policy,
      params = params,
      normalize = TRUE
    )
  }

  # Sensitivity Jacobian (optional)
  sens <- NULL
  if (isTRUE(include_sensitivity)) {
    state0 <- as.numeric(res$trajectory_wide[1, c("K", "H", "N", "C", "P", "A")])
    names(state0) <- c("K", "H", "N", "C", "P", "A")
    sens <- sensitivity_jacobian(
      state = state0,
      params = params,
      t = times[1],
      policy = policy
    )
  }

  # Friendly scorecard (start/end + deltas)
  make_score <- function(df, cols) {
    if (!is.data.frame(df) || nrow(df) < 1) return(NULL)
    start <- df[1, , drop = FALSE]
    end <- df[nrow(df), , drop = FALSE]
    out <- list()
    k <- 1
    for (nm in cols) {
      if (!nm %in% names(df)) next
      s <- as.numeric(start[[nm]])
      e <- as.numeric(end[[nm]])
      out[[k]] <- data.frame(
        metric = nm,
        start = s,
        end = e,
        change = e - s,
        pct_change = if (is.finite(s) && s != 0) (e - s) / s else NA_real_,
        stringsAsFactors = FALSE
      )
      k <- k + 1
    }
    if (length(out) == 0) return(NULL)
    do.call(rbind, out)
  }
  scorecard <- make_score(res$trajectory_wide, c("gdp","emissions","ans","N","C"))


  # Plots
  plots <- list(
    trajectory = plot_trajectory(res$trajectory_long, metrics = c("gdp", "emissions", "ans")),
    sdg_dashboard = plot_sdg_dashboard(sdg)
  )
  if (!is.null(pp)) {
    plots$phase_plane <- plot_phase_plane(pp, trajectory_wide = res$trajectory_wide)
  }
  if (!is.null(sens)) {
    plots$sensitivity_heatmap <- plot_sensitivity_heatmap(sens)
  }

  out <- list(
    trajectory_wide = res$trajectory_wide,
    trajectory_long = res$trajectory_long,
    sdg_indicators = sdg,
    carbon_budget = cb,
    scorecard = scorecard,
    phase_plane = pp,
    sensitivities = sens,
    meta = res$meta,
    plots = plots
  )
  class(out) <- "catalyst_run"
  out
}

# end of catalyst_run() ...

#' Run a stable demo with dummy data
#'
#' @param seed Integer seed for reproducibility.
#' @param budget_mode Budget behavior: "auto" (default), "pass" (within budget),
#'   "fail" (over budget), or "custom" (use emissions_budget).
#' @param headroom Fractional slack used when budget_mode is "auto"/"pass"/"fail".
#' @param emissions_budget Optional numeric budget (required when budget_mode = "custom").
#' @return A "catalyst_run" object.
#' @examples
#' x <- catalyst_demo()
#' print(x)
#' plot(x, which = "trajectory")
#' @export
#' @examples
#' x <- catalyst_demo()
#' print(x)
#' plot(x, which = "trajectory")
catalyst_demo <- function(
  seed = 42L,
  budget_mode = c("auto", "pass", "fail", "custom"),
  headroom = 0.05,
  emissions_budget = NULL
) {
  # Deterministic model, but keeping a seed makes the demo reproducible
  # if you later add randomized dummy inputs (e.g., shocks, noise).
  set.seed(as.integer(seed))

  times <- seq(0, 20, by = 1)
  x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)

  # Compute a baseline cumulative emissions level so the default budget is meaningful
  base <- simulate_dynamics(times, x0, return_long = FALSE)
  cum_e <- carbon_budget(base$trajectory_wide, budget = 1e12)$cumulative_emissions

  budget_mode <- match.arg(budget_mode)

  budget <- emissions_budget
  if (is.null(budget)) {
    if (budget_mode %in% c("auto", "pass")) {
      budget <- cum_e * (1 + headroom)
    } else if (budget_mode == "fail") {
      budget <- cum_e * (1 - headroom)
    } else {
      stop("For budget_mode = 'custom', please supply emissions_budget = ...")
    }
  }

  catalyst_run(
    times = times,
    x0 = x0,
    emissions_budget = budget,
    include_phase_plane = TRUE,
    include_sensitivity = TRUE
  )
}
