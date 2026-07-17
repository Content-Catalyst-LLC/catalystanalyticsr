if (getRversion() >= "2.15.1") utils::globalVariables(c(
  "x", "dx", "y", "dy", "xend", "yend",
  "value", "scenario", "param", "state", "t", "final_value", "scenario_id",
  "x_value", "y_value", "non_dominated", "absolute_delta"
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
    model_contract_version = "1.0.0",
    scenario_schema_version = "1.0.0",
    comparison_schema_version = "1.0.0",
    uncertainty_schema_version = "1.0.0",
    demo_export_schema_version = "1.3.0"
  )
}

utils::globalVariables(c("sample_id", "median", "p10", "p90", "estimate", "target", "absolute_effect"))
