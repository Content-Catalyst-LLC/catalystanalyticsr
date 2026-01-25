#' Export a Catalyst run as a portable bundle
#'
#' A convenience wrapper around [export_catalyst_bundle()] that writes key
#' outputs from a `catalyst_run` object (or compatible list) to a folder
#' @param results A `catalyst_run` object (or compatible list) returned by
#' @param dir Output directory to write into.
#' @param run_id Optional run id used to name the bundle directory.
#' @param zip Logical. If TRUE, also write a zip file.
#' @param overwrite Logical. If TRUE, overwrite existing output.
#' @param open Logical. If TRUE, open the output folder (macOS: Finder).
#' @param quiet Logical. If TRUE, suppress friendly messages.
#'
#' @return Invisibly returns paths written (and/or bundle metadata).
#' @export
#'
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- catalyst_run(times, x0, include_phase_plane = FALSE, include_sensitivity = FALSE)
#' # Write into a temp directory for the example
#' out <- catalyst_export(res, dir = tempdir(), run_id = "demo", quiet = TRUE)
#' out
catalyst_export <- function(
  results,
  dir = tempdir(),
  run_id = "demo",
  zip = TRUE,
  overwrite = FALSE,
  open = FALSE,
  quiet = FALSE
) {
  export_catalyst_bundle(
    results = results,
    dir = dir,
    run_id = run_id,
    zip = zip,
    overwrite = overwrite,
    open = open,
    quiet = quiet
  )
}
