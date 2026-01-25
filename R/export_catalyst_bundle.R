#' Export a Catalyst results bundle (CSVs + plots)
#'
#' Writes a small, reproducible folder of outputs from a `catalyst_run` object.
#'
#' @param results A `catalyst_run` object (as returned by [catalyst_run()] or [catalyst_demo()]).
#' @param dir Output directory (bundle will be created inside here).
#' @param run_id Label used for folder/file names.
#' @param zip Logical. If TRUE, also create a zip file.
#' @param overwrite Logical. If TRUE, overwrite existing outputs.
#' @param open Logical. If TRUE (macOS), open the output folder in Finder.
#' @param quiet Logical. If TRUE, suppress messages.
#'
#' @return Invisibly returns a character vector of paths written.
#' @export
#'
#' @examples
#' \dontrun{
#' x <- catalyst_demo()
#' export_catalyst_bundle(x, dir = tempdir(), run_id = "demo", zip = FALSE, quiet = TRUE)
#' }
export_catalyst_bundle <- function(
  results,
  dir,
  run_id = NULL,
  zip = TRUE,
  overwrite = FALSE,
  open = FALSE,
  quiet = FALSE
) {
  if (!is.list(results)) stop("`results` must be a list.")
  if (!is.character(dir) || length(dir) != 1) stop("`dir` must be a single path string.")

  if (is.null(run_id)) {
    run_id <- format(Sys.time(), "%Y%m%d_%H%M%S")
  }
  if (!is.character(run_id) || length(run_id) != 1) stop("`run_id` must be a single string.")

  out_dir <- file.path(dir, paste0("bundle_", run_id))
  if (dir.exists(out_dir)) {
    if (!overwrite) stop("Output bundle already exists. Set `overwrite = TRUE` to replace.")
    unlink(out_dir, recursive = TRUE, force = TRUE)
  }
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

  # Helper to write data frames
  write_df <- function(name, df) {
    if (!is.data.frame(df)) return(NULL)
    path <- file.path(out_dir, paste0(name, ".csv"))
    utils::write.csv(df, path, row.names = FALSE)
    path
  }

  # Coerce certain list outputs into a one-row data.frame for export.
  as_one_row_df <- function(x) {
    if (is.null(x)) return(NULL)
    if (is.data.frame(x)) return(x)
    if (is.list(x) && !is.data.frame(x)) {
      # Turn a named list into a one-row data.frame.
      nms <- names(x)
      if (is.null(nms)) return(NULL)
      return(as.data.frame(x, stringsAsFactors = FALSE))
    }
    NULL
  }

  written <- c(
    write_df("trajectory_wide", results$trajectory_wide),
    write_df("trajectory_long", results$trajectory_long),
    write_df("sdg_indicators", results$sdg_indicators),
    write_df("phase_plane", results$phase_plane),
    write_df("sensitivities", results$sensitivities),
    write_df("carbon_budget", as_one_row_df(results$carbon_budget)),
    write_df("scorecard", results$scorecard),
    write_df("kaya", results$kaya),
    write_df("params", if (is.data.frame(results$params)) results$params else NULL)
  )
  written <- written[!is.na(written)]

  # Save plots if present
  if (is.list(results$plots)) {
    for (nm in names(results$plots)) {
      plt <- results$plots[[nm]]
      if (inherits(plt, "ggplot")) {
        img_path <- file.path(out_dir, paste0(nm, ".png"))
        save_plot(plt, img_path)
        written <- c(written, img_path)
      }
    }
  }

  # Manifest (JSON)
  pkg_version <- tryCatch(as.character(utils::packageVersion("catalystanalyticsr")), error = function(e) "dev")
  manifest <- list(
    package = "catalystanalyticsr",
    version = pkg_version,
    run_id = run_id,
    created_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
    files = basename(written)
  )
  manifest_path <- file.path(out_dir, "manifest.json")
  jsonlite::write_json(manifest, manifest_path, auto_unbox = TRUE, pretty = TRUE)

  # Friendly message (optional)
  if (!isTRUE(quiet)) {
    message("Bundle written to: ", out_dir)
  }

  # Optionally open the folder (macOS)
  if (isTRUE(open) && identical(Sys.info()[["sysname"]], "Darwin")) {
    try(system2("open", shQuote(out_dir)), silent = TRUE)
  }

  # Optionally zip the bundle
  if (isTRUE(zip)) {
    zip_path <- file.path(dir, paste0("bundle_", run_id, ".zip"))
    if (file.exists(zip_path) && !overwrite) {
      stop("Zip file already exists. Set `overwrite = TRUE` to replace.")
    }
    if (file.exists(zip_path)) file.remove(zip_path)
    old <- getwd()
    on.exit(setwd(old), add = TRUE)
    setwd(dir)
    utils::zip(zipfile = basename(zip_path), files = basename(out_dir))
    return(invisible(list(bundle_dir = out_dir, zip_path = zip_path, manifest = manifest)))
  }

  invisible(list(bundle_dir = out_dir, manifest = manifest))
}