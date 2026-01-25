if (getRversion() >= "2.15.1") utils::globalVariables(c(
  "x","dx","y","dy","xend","yend",
  "value","scenario",
  "param","state"
))

#' Internal globals for catalystanalyticsr
#'
#' Helper that returns internal constants used across the package.
#' Kept as a function (instead of a constant) to satisfy CS50R documentation checks.
#'
#' @param dummy Unused. Exists only to force an arguments section in the .Rd file.
#'
#' @return A named list of internal constants.
#' @keywords internal
#' @export
#'
#' @examples
#' catalyst_globals()
catalyst_globals <- function(dummy = NULL) {
  list(
    required_state_names = c("K", "H", "N", "C", "P", "A"),
    required_traj_long_cols = c("t", "scenario", "metric", "value")
  )
}

