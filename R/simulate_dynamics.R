#' Simulate dynamics
#'
#' Runs the KH-NC-PA model over `times` and returns wide and optional long
#' trajectories for analysis, plotting, and export.
#'
#' @param times Numeric vector of time points.
#' @param x0 Named numeric vector of initial state (K,H,N,C,P,A).
#' @param policy List of policy controls (s,e,a).
#' @param params List of parameter overrides.
#' @param model Dynamics model. Currently only "khncpa" is supported.
#' @param method Integration method ("rk4" or "euler").
#' @param scenario Non-empty scenario label.
#' @param return_long Logical. If TRUE, also return a long trajectory.
#' @return A list with `trajectory_wide`, optional `trajectory_long`, and `meta`.
#' @export
#'
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = TRUE)
#' head(res$trajectory_wide)
simulate_dynamics <- function(
  times,
  x0,
  policy = list(s = 0.20, e = 0.05, a = 0.00),
  params = list(),
  model = "khncpa",
  method = c("rk4", "euler"),
  scenario = "baseline",
  return_long = TRUE
) {
  method <- match.arg(method)
  model <- match.arg(model, "khncpa")
  .validate_times(times)
  x0 <- .validate_state(x0, "x0")
  .validate_policy(policy)
  .validate_params(params)
  .assert_single_string(scenario, "scenario")
  .assert_flag(return_long, "return_long")

  required_states <- .khncpa_required_states()
  p <- .khncpa_build_params(params, x0)

  n <- length(times)
  states <- matrix(NA_real_, nrow = n, ncol = length(required_states))
  colnames(states) <- required_states
  states[1, ] <- as.numeric(x0[required_states])

  Y <- emissions <- depletion <- damages <- savings <- education <-
    consumption <- abatement <- ans_series <- rep(NA_real_, n)

  record_flows <- function(i, time) {
    fl <- .khncpa_flows_from_state(time, states[i, ], policy, p)
    Y[i] <<- fl$Y
    emissions[i] <<- fl$emissions
    depletion[i] <<- fl$depletion
    damages[i] <<- fl$damages
    savings[i] <<- fl$savings
    education[i] <<- fl$education
    consumption[i] <<- fl$consumption
    abatement[i] <<- fl$a
    ans_series[i] <<- ans(fl$savings, fl$education, fl$depletion, fl$damages)
  }
  record_flows(1L, times[1L])

  for (i in seq_len(n - 1L)) {
    t <- times[i]
    h <- times[i + 1L] - times[i]
    xi <- states[i, ]

    xnext <- if (method == "euler") {
      k1 <- .khncpa_deriv(t, xi, policy, p)
      xi + h * k1
    } else {
      k1 <- .khncpa_deriv(t, xi, policy, p)
      k2 <- .khncpa_deriv(t + h / 2, xi + (h / 2) * k1, policy, p)
      k3 <- .khncpa_deriv(t + h / 2, xi + (h / 2) * k2, policy, p)
      k4 <- .khncpa_deriv(t + h, xi + h * k3, policy, p)
      xi + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    }

    if (any(!is.finite(xnext))) {
      stop(sprintf("Non-finite state generated at time %s.", times[i + 1L]), call. = FALSE)
    }
    states[i + 1L, ] <- as.numeric(xnext)
    record_flows(i + 1L, times[i + 1L])
  }

  trajectory_wide <- data.frame(
    t = times,
    scenario = scenario,
    K = states[, "K"],
    H = states[, "H"],
    N = states[, "N"],
    C = states[, "C"],
    P = states[, "P"],
    A = states[, "A"],
    gdp = Y,
    consumption = consumption,
    savings = savings,
    education = education,
    abatement = abatement,
    emissions = emissions,
    depletion = depletion,
    damages = damages,
    ans = ans_series,
    stringsAsFactors = FALSE
  )

  meta <- list(
    package_version = .catalyst_package_version(),
    model = model,
    model_contract_version = catalyst_globals()$model_contract_version,
    integration_method = method,
    scenario = scenario,
    time_start = times[1L],
    time_end = times[n],
    time_steps = n,
    initial_state = as.list(x0[required_states]),
    params = p,
    policy = policy
  )

  if (!return_long) {
    return(list(trajectory_wide = trajectory_wide, meta = meta))
  }

  metric_cols <- c(
    "gdp", "consumption", "ans", "emissions", "damages", "depletion",
    "K", "H", "N", "C", "P", "A"
  )
  units <- c(
    gdp = "index", consumption = "index", ans = "index",
    emissions = "tCO2e_index", damages = "index", depletion = "index",
    K = "index", H = "index", N = "index", C = "index",
    P = "people_index", A = "index"
  )
  trajectory_long <- do.call(rbind, lapply(metric_cols, function(metric) {
    data.frame(
      t = trajectory_wide$t,
      scenario = trajectory_wide$scenario,
      metric = metric,
      value = trajectory_wide[[metric]],
      unit = unname(units[[metric]]),
      stringsAsFactors = FALSE
    )
  }))
  rownames(trajectory_long) <- NULL

  list(
    trajectory_wide = trajectory_wide,
    trajectory_long = trajectory_long,
    meta = meta
  )
}
