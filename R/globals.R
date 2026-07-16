if (getRversion() >= "2.15.1") utils::globalVariables(c(
  "x", "dx", "y", "dy", "xend", "yend",
  "value", "scenario", "param", "state"
))

#' Internal constants for catalystanalyticsr
#'
#' Returns stable package constants used by examples, validation, and release
#' checks. Most users will not need to call this function directly.
#'
#' @param dummy Unused; retained for backwards compatibility.
#' @return A named list of internal constants.
#' @keywords internal
#' @export
#'
#' @examples
#' catalyst_globals()
catalyst_globals <- function(dummy = NULL) {
  list(
    required_state_names = c("K", "H", "N", "C", "P", "A"),
    required_traj_long_cols = c("t", "scenario", "metric", "value"),
    model_id = "khncpa",
    model_contract_version = "0.1.4",
    demo_export_schema_version = "1.0.0"
  )
}
