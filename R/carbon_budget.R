#' Compute Carbon Budget Consumption via Time Integration
#'
#' @param trajectory_wide A data.frame containing a time column and an emissions column.
#' @param budget Single non-negative numeric (the total carbon budget).
#' @param emissions_col Name of emissions column in `trajectory_wide`.
#' @param time_col Name of time column in `trajectory_wide`.
#' @return A list with cumulative_emissions, budget, remaining, within_budget.
#' @export
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = FALSE)
#' carbon_budget(res$trajectory_wide, budget = 1e6)
carbon_budget <- function(trajectory_wide, budget, emissions_col = "emissions", time_col = "t") {
  if (!is.data.frame(trajectory_wide)) stop("`trajectory_wide` must be a data.frame.")
  if (!is.numeric(budget) || length(budget) != 1 || !is.finite(budget) || budget < 0) {
    stop("`budget` must be a single non-negative number.")
  }
  if (!emissions_col %in% names(trajectory_wide)) {
    stop(sprintf("Column `%s` not found in `trajectory_wide`.", emissions_col))
  }
  if (!time_col %in% names(trajectory_wide)) {
    stop(sprintf("Column `%s` not found in `trajectory_wide`.", time_col))
  }

  t <- trajectory_wide[[time_col]]
  e <- trajectory_wide[[emissions_col]]

  if (!is.numeric(t) || !is.numeric(e)) stop("Time and emissions columns must be numeric.")
  if (length(t) < 2) stop("Need at least 2 rows to compute a budget integral.")
  if (is.unsorted(t, strictly = TRUE)) stop("Time column must be strictly increasing.")

  dt <- diff(t)
  cum_emissions <- sum((utils::head(e, -1) + utils::tail(e, -1)) / 2 * dt)

  remaining <- budget - cum_emissions

  list(
    cumulative_emissions = cum_emissions,
    budget = budget,
    remaining = remaining,
    within_budget = (remaining >= 0)
  )
}