.khncpa_as_state <- function(x) {
  # Normalize state to a named numeric vector.
  if (is.list(x)) {
    x <- unlist(x)
  }
  if (!is.numeric(x) || is.null(names(x))) {
    stop("State must be a named numeric vector (or list coercible to one).")
  }
  x
}

.khncpa_required_states <- function() c("K", "H", "N", "C", "P", "A")

.khncpa_build_params <- function(params, x0) {
  x0 <- .khncpa_as_state(x0)
  base <- list(
    alpha = 0.30,
    beta  = 0.30,
    gamma = 0.10,
    deltaK = 0.05,
    deltaH = 0.03,
    Nmax = 1.0,
    regen = 0.02,
    depletion_intensity = 0.01,
    emissions_intensity = 0.30,
    absorption = 0.10,
    C0 = as.numeric(x0[["C"]]),
    damage_scale = 0.001,
    pop_growth = 0.01,
    Pmax = NA_real_,
    tech_growth = 0.01,
    abatement_cost_scale = 0.02
  )

  if (is.null(params)) params <- list()
  if (!is.list(params)) stop("`params` must be a list.")
  utils::modifyList(base, params)
}

.khncpa_get_u <- function(policy, name, t, x) {
  if (is.null(policy) || !is.list(policy)) stop("`policy` must be a list.")
  if (!name %in% names(policy)) stop(sprintf("Missing policy value `%s`.", name))
  u <- policy[[name]]
  if (is.function(u)) return(as.numeric(u(t, x)))
  as.numeric(u)
}

.khncpa_flows_from_state <- function(t, x, policy, p) {
  x <- .khncpa_as_state(x)

  K <- max(as.numeric(x[["K"]]), 1e-12)
  H <- max(as.numeric(x[["H"]]), 1e-12)
  N <- max(as.numeric(x[["N"]]), 1e-12)
  C <- as.numeric(x[["C"]])
  P <- max(as.numeric(x[["P"]]), 1e-12)
  A <- max(as.numeric(x[["A"]]), 1e-12)

  s <- .khncpa_get_u(policy, "s", t, x)
  e <- .khncpa_get_u(policy, "e", t, x)
  a <- .khncpa_get_u(policy, "a", t, x)

  if (any(!is.finite(c(s, e, a)))) stop("Non-finite policy values encountered.")
  if (s < 0 || e < 0) stop("Policy values `s` and `e` must be >= 0.")
  if (a < 0 || a > 1) stop("Policy value `a` (abatement) must be within [0, 1].")
  if ((s + e) > 0.95) stop("Policy values `s + e` must be <= 0.95 (leave room for consumption).")

  expoP <- max(1 - p$alpha - p$beta - p$gamma, 0)
  Y <- A * (K ^ p$alpha) * (H ^ p$beta) * (N ^ p$gamma) * (P ^ expoP)

  abate_cost <- p$abatement_cost_scale * (a ^ 2) * Y
  emissions <- p$emissions_intensity * (1 - a) * Y
  depletion <- p$depletion_intensity * Y
  damages <- p$damage_scale * ((C - p$C0) ^ 2) * Y

  savings <- s * Y
  education <- e * Y
  consumption <- max((1 - s - e) * Y - abate_cost, 0)

  list(
    Y = Y,
    s = s,
    e = e,
    a = a,
    savings = savings,
    education = education,
    consumption = consumption,
    emissions = emissions,
    depletion = depletion,
    damages = damages
  )
}

.khncpa_deriv <- function(t, x, policy, p) {
  x <- .khncpa_as_state(x)
  fl <- .khncpa_flows_from_state(t, x, policy, p)

  K <- as.numeric(x[["K"]])
  H <- as.numeric(x[["H"]])
  N <- as.numeric(x[["N"]])
  C <- as.numeric(x[["C"]])
  P <- as.numeric(x[["P"]])
  A <- as.numeric(x[["A"]])

  dK <- fl$savings - p$deltaK * K - (p$abatement_cost_scale * (fl$a ^ 2) * fl$Y)
  dH <- fl$education - p$deltaH * H
  dN <- p$regen * (p$Nmax - N) - fl$depletion
  dC <- fl$emissions - p$absorption * (C - p$C0)

  if (is.na(p$Pmax)) {
    dP <- p$pop_growth * P
  } else {
    dP <- p$pop_growth * P * (1 - P / p$Pmax)
  }

  dA <- p$tech_growth * A

  c(K = dK, H = dH, N = dN, C = dC, P = dP, A = dA)
}
