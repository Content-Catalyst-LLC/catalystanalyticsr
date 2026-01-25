#' @title Print a Catalyst run (friendly summary)
#' @description S3 method for printing a \code{catalyst_run} object.
#' @param x A \code{catalyst_run} object.
#' @param ... Unused.
#' @return Invisibly returns \code{x}.
#' @export
#' @examples
#' x <- catalyst_demo()
#' print(x)
print.catalyst_run <- function(x, ...) {
  fmt <- function(v, d = 3) {
    if (is.null(v) || length(v) == 0 || !is.finite(v)) return(NA_character_)
    format(round(v, d), nsmall = d, trim = TRUE)
  }
  
  tw <- x$trajectory_wide
  if (!is.data.frame(tw) || nrow(tw) < 1) {
    cat("<catalyst_run: (no trajectory data)>\n")
    return(invisible(x))
  }
  
  t0 <- tw[1, , drop = FALSE]
  tN <- tw[nrow(tw), , drop = FALSE]
  
  scenario <- if ("scenario" %in% names(tw)) as.character(t0$scenario) else "(unknown)"
  t_start <- if ("t" %in% names(tw)) t0$t else 0
  t_end   <- if ("t" %in% names(tw)) tN$t else (nrow(tw) - 1)
  
  cat("Catalyst Analytics R -- Scenario Run\n")
  cat("Scenario:", scenario, "\n")
  cat("Time:", t_start, "->", t_end, "  (steps:", nrow(tw), ")\n\n")
  
  cat("Key outcomes (model units / indices)\n")
  show <- function(label, col) {
    if (!col %in% names(tw)) return()
    cat(sprintf("  %-18s %8s -> %8s\n", label, fmt(t0[[col]]), fmt(tN[[col]])))
  }
  show("GDP (gdp)", "gdp")
  show("Emissions", "emissions")
  show("Adjusted Net Savings", "ans")
  show("Natural capital (N)", "N")
  show("Atmospheric carbon (C)", "C")
  
  if (is.data.frame(x$scorecard)) {
    cat("\nScorecard (percent change)\n")
    sc <- x$scorecard
    pick <- c("gdp", "emissions", "ans")
    sc <- sc[sc$metric %in% pick, , drop = FALSE]
    if (nrow(sc) > 0) {
      for (i in seq_len(nrow(sc))) {
        nm <- sc$metric[i]
        pc <- sc$pct_change[i]
        pc_txt <- if (is.finite(pc)) sprintf("%+.1f%%", 100 * pc) else "NA"
        cat(sprintf("  %-18s %s\n", nm, pc_txt))
      }
    }
  }
  
  if (!is.null(x$carbon_budget)) {
    cb <- x$carbon_budget
    cat("\nEmissions budget check\n")
    status <- if (isTRUE(cb$within_budget)) "WITHIN budget [OK]" else "OVER budget [!]"
    cat("  Status:", status, "\n")
    if (!is.null(cb$cumulative_emissions)) cat("  Cumulative emissions:", fmt(cb$cumulative_emissions), "\n")
    if (!is.null(cb$budget))              cat("  Total allowed cumulative emissions:", fmt(cb$budget), "\n")
    if (!is.null(cb$remaining))           cat("  Remaining:", fmt(cb$remaining), "\n")
  }
  
  cat("\nTips\n")
  cat('  * plot(x) shows a plot (try plot(x, which = "trajectory"))\n')
  cat("  * catalyst_glossary() explains variables + units\n")
  cat("  * catalyst_export(x, dir=..., run_id=...) writes CSV/PNG outputs\n")
  
  invisible(x)
}

#' @title Summary of a Catalyst run
#' @description S3 method for summarizing a \code{catalyst_run} object.
#' @param object A \code{catalyst_run} object.
#' @param ... Unused.
#' @export
#' @title Summary of a Catalyst run
#' @description S3 method for summarizing a \code{catalyst_run} object.
#' @param object A \code{catalyst_run} object.
#' @param ... Unused.
#' @return Invisibly returns \code{object}.
#' @export
#' @examples
#' x <- catalyst_demo()
#' summary(x)
#' @examples
#' x <- catalyst_demo()
#' summary(x)
summary.catalyst_run <- function(object, ...) {
  print(object)
  
  cat("\nOutputs\n")
  if (is.data.frame(object$trajectory_wide)) {
    cat("  * trajectory_wide:", nrow(object$trajectory_wide), "rows,", ncol(object$trajectory_wide), "cols\n")
  }
  if (is.data.frame(object$trajectory_long)) {
    cat("  * trajectory_long:", nrow(object$trajectory_long), "rows,", ncol(object$trajectory_long), "cols\n")
  }
  if (is.data.frame(object$sdg_indicators)) {
    cat("  * sdg_indicators:", nrow(object$sdg_indicators), "rows\n")
  }
  if (is.data.frame(object$scorecard)) {
    cat("  * scorecard:", nrow(object$scorecard), "rows\n")
  }
  if (is.data.frame(object$phase_plane)) {
    cat("  * phase_plane:", nrow(object$phase_plane), "rows\n")
  }
  if (is.data.frame(object$sensitivities)) {
    cat("  * sensitivities:", nrow(object$sensitivities), "rows\n")
  }
  if (is.list(object$plots)) {
    cat("  * plots:", paste(names(object$plots), collapse = ", "), "\n")
  }
  
  invisible(object)
}

#' @title Plot a Catalyst run
#' @description S3 method for plotting a \code{catalyst_run} object.
#' @param x A \code{catalyst_run} object.
#' @param which Which plot to display. One of \code{"trajectory"}, \code{"sdg_dashboard"},
#'   \code{"phase_plane"}, \code{"sensitivity_heatmap"}, or \code{"all"}.
#' @param ... Passed through (unused currently).
#' @export
#' @return Invisibly returns the selected ggplot object (or a list of plots when `which = "all"`).
#' @title Plot a Catalyst run
#' @description S3 method for plotting a \code{catalyst_run} object.
#' @param x A \code{catalyst_run} object.
#' @param which Which plot to display. One of \code{"trajectory"}, \code{"sdg_dashboard"},
#'   \code{"phase_plane"}, \code{"sensitivity_heatmap"}, or \code{"all"}.
#' @param ... Passed through (unused currently).
#' @return Invisibly returns the selected ggplot object (or a list of plots when `which = "all"`).
#' @export
#' @examples
#' \dontrun{
#' x <- catalyst_demo()
#' plot(x, which = "trajectory")
#' }
#' @examples
#' x <- catalyst_demo()
#' plot(x, which = "trajectory")
plot.catalyst_run <- function(
    x,
    which = c("trajectory", "sdg_dashboard", "phase_plane", "sensitivity_heatmap", "all"),
    ...
) {
  which <- match.arg(which)
  
  if (!is.list(x$plots)) stop("This run has no `plots` list.")
  
  if (which == "all") {
    for (nm in names(x$plots)) {
      plt <- x$plots[[nm]]
      if (inherits(plt, "ggplot")) print(plt)
    }
    return(invisible(x$plots))
  }
  
  plt <- x$plots[[which]]
  if (is.null(plt)) stop(sprintf("Plot '%s' not found in x$plots.", which))
  if (!inherits(plt, "ggplot")) stop(sprintf("x$plots[['%s']] is not a ggplot.", which))
  
  print(plt)
  invisible(plt)
}


