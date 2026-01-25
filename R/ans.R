#' Adjusted Net Savings (ANS)
#'
#' Computes a simple Adjusted Net Savings proxy:
#' gross savings + education expenditure - resource depletion - pollution damages.
#'
#' @param gross_savings Numeric gross savings.
#' @param edu_expenditure Numeric education expenditure.
#' @param resource_depletion Numeric natural resource depletion.
#' @param pollution_damage Numeric pollution damages.
#'
#' @return Numeric adjusted net savings.
#' @export
#'
#' @examples
#' ans(gross_savings = 100, edu_expenditure = 10, resource_depletion = 15, pollution_damage = 5)
ans <- function(gross_savings, edu_expenditure, resource_depletion, pollution_damage) {
  inputs <- list(gross_savings, edu_expenditure, resource_depletion, pollution_damage)
  if (!all(vapply(inputs, is.numeric, logical(1)))) {
    stop("All inputs must be numeric.")
  }
  
  if (any(edu_expenditure < 0, na.rm = TRUE) ||
      any(resource_depletion < 0, na.rm = TRUE) ||
      any(pollution_damage < 0, na.rm = TRUE)) {
    stop("Expenditure, depletion, and damage values cannot be negative.")
  }
  
  gross_savings + edu_expenditure - resource_depletion - pollution_damage
}

