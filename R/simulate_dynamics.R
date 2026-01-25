#' Simulate dynamics
#'
#' One-step wrapper that runs the KH-NC-PA model over `times` and returns
#' both wide and long trajectories for plotting/export.
#'
#' @param times Numeric vector of time points.
#' @param x0 Named numeric vector of initial state (K,H,N,C,P,A).
#' @param policy List of policy controls (s,e,a).
#' @param params List of parameter overrides.
#' @param model Which dynamics model to run. Currently only "khncpa" is supported.
#' @param method Integration method ("rk4" or "euler").
#' @param scenario Scenario label.
#' @param return_long Logical. If TRUE, also return a long version.
#'
#' @return A list with `trajectory_wide`, and if `return_long=TRUE`, `trajectory_long`, plus `meta`.
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

  if (!is.numeric(times) || length(times) < 2) {
    stop("`times` must be a numeric vector with length >= 2.")
  }
  if (is.unsorted(times, strictly = TRUE)) {
    stop("`times` must be strictly increasing.")
  }
  if (!is.numeric(x0) || is.null(names(x0))) {
    stop("`x0` must be a named numeric vector.")
  }

  required_states <- .khncpa_required_states()
  if (!all(required_states %in% names(x0))) {
    stop("`x0` must include names: K, H, N, C, P, A.")
  }

  p <- .khncpa_build_params(params, x0)

  # Integration loop
  n <- length(times)
  states <- matrix(NA_real_, nrow = n, ncol = length(required_states))
  colnames(states) <- required_states
  states[1, ] <- as.numeric(x0[required_states])

  # Derived series
  Y <- rep(NA_real_, n)
  emissions <- rep(NA_real_, n)
  depletion <- rep(NA_real_, n)
  damages <- rep(NA_real_, n)
  savings <- rep(NA_real_, n)
  education <- rep(NA_real_, n)
  consumption <- rep(NA_real_, n)
  abatement <- rep(NA_real_, n)
  ans_series <- rep(NA_real_, n)

  # Evaluate flows at initial time
  fl0 <- .khncpa_flows_from_state(times[1], states[1, ], policy, p)
  Y[1] <- fl0$Y
  emissions[1] <- fl0$emissions
  depletion[1] <- fl0$depletion
  damages[1] <- fl0$damages
  savings[1] <- fl0$savings
  education[1] <- fl0$education
  consumption[1] <- fl0$consumption
  abatement[1] <- fl0$a
  ans_series[1] <- ans(savings[1], education[1], depletion[1], damages[1])

  for (i in 1:(n - 1)) {
    t <- times[i]
    h <- times[i + 1] - times[i]
    xi <- as.list(states[i, ])

    if (method == "euler") {
      k1 <- .khncpa_deriv(t, xi, policy, p)
      xnext <- states[i, ] + h * k1
    } else {
      k1 <- .khncpa_deriv(t, xi, policy, p)
      k2 <- .khncpa_deriv(t + h/2, as.list(states[i, ] + (h/2) * k1), policy, p)
      k3 <- .khncpa_deriv(t + h/2, as.list(states[i, ] + (h/2) * k2), policy, p)
      k4 <- .khncpa_deriv(t + h,   as.list(states[i, ] + h * k3), policy, p)
      xnext <- states[i, ] + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
    }

    states[i + 1, ] <- as.numeric(xnext)

    # Derived flows at t_{i+1}
    fl <- .khncpa_flows_from_state(times[i + 1], states[i + 1, ], policy, p)
    Y[i + 1] <- fl$Y
    emissions[i + 1] <- fl$emissions
    depletion[i + 1] <- fl$depletion
    damages[i + 1] <- fl$damages
    savings[i + 1] <- fl$savings
    education[i + 1] <- fl$education
    consumption[i + 1] <- fl$consumption
    abatement[i + 1] <- fl$a
    ans_series[i + 1] <- ans(savings[i + 1], education[i + 1], depletion[i + 1], damages[i + 1])
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
    ans = ans_series
  )

  if (!return_long) {
    return(list(
      trajectory_wide = trajectory_wide,
      meta = list(model = model, params = p, policy = policy)
    ))
  }

  # Long format for plotting/export (no extra dependencies)
  metric_cols <- c("gdp", "consumption", "ans", "emissions", "damages", "depletion", "K", "H", "N", "C", "P", "A")
  long_list <- lapply(metric_cols, function(m) {
    data.frame(
      t = trajectory_wide$t,
      scenario = trajectory_wide$scenario,
      metric = m,
      value = trajectory_wide[[m]],
      unit = NA_character_,
      stringsAsFactors = FALSE
    )
  })
  trajectory_long <- do.call(rbind, long_list)

  # Simple unit hints (customize later)
  units <- list(
    gdp = "index",
    consumption = "index",
    ans = "index",
    emissions = "tCO2e_index",
    damages = "index",
    depletion = "index",
    K = "index",
    H = "index",
    N = "index",
    C = "index",
    P = "people_index",
    A = "index"
  )
  trajectory_long$unit <- unname(unlist(units[trajectory_long$metric]))

  list(
    trajectory_wide = trajectory_wide,
    trajectory_long = trajectory_long,
    meta = list(model = model, params = p, policy = policy)
  )
}