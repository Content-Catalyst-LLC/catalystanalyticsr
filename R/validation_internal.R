.assert_flag <- function(x, arg) {
  if (!is.logical(x) || length(x) != 1L || is.na(x)) {
    stop(sprintf("`%s` must be TRUE or FALSE.", arg), call. = FALSE)
  }
  invisible(x)
}

.assert_single_string <- function(x, arg, allow_empty = FALSE) {
  ok <- is.character(x) && length(x) == 1L && !is.na(x)
  if (ok && !allow_empty) ok <- nzchar(trimws(x))
  if (!ok) {
    qualifier <- if (allow_empty) "a single string" else "a single non-empty string"
    stop(sprintf("`%s` must be %s.", arg, qualifier), call. = FALSE)
  }
  invisible(x)
}

.assert_scalar_number <- function(x, arg, finite = TRUE, lower = -Inf, upper = Inf) {
  ok <- is.numeric(x) && length(x) == 1L && !is.na(x)
  if (ok && finite) ok <- is.finite(x)
  if (ok) ok <- x >= lower && x <= upper
  if (!ok) {
    stop(sprintf("`%s` must be a single numeric value in [%s, %s].", arg, lower, upper), call. = FALSE)
  }
  invisible(x)
}

.validate_times <- function(times) {
  if (!is.numeric(times) || length(times) < 2L || any(!is.finite(times))) {
    stop("`times` must be a finite numeric vector with length >= 2.", call. = FALSE)
  }
  if (is.unsorted(times, strictly = TRUE)) {
    stop("`times` must be strictly increasing.", call. = FALSE)
  }
  invisible(times)
}

.validate_state <- function(x, arg = "x0") {
  required <- .khncpa_required_states()
  if (!is.numeric(x) || is.null(names(x))) {
    stop(sprintf("`%s` must be a named numeric vector.", arg), call. = FALSE)
  }
  if (anyDuplicated(names(x))) {
    stop(sprintf("`%s` cannot contain duplicate state names.", arg), call. = FALSE)
  }
  if (!all(required %in% names(x))) {
    stop(sprintf("`%s` must include names: K, H, N, C, P, A.", arg), call. = FALSE)
  }
  state <- x[required]
  if (any(!is.finite(state))) {
    stop(sprintf("`%s` state values must be finite.", arg), call. = FALSE)
  }
  nonnegative <- c("K", "H", "N", "P", "A")
  if (any(state[nonnegative] < 0)) {
    stop(sprintf("`%s` values K, H, N, P, and A cannot be negative.", arg), call. = FALSE)
  }
  invisible(state)
}

.validate_policy <- function(policy) {
  if (!is.list(policy)) stop("`policy` must be a list.", call. = FALSE)
  required <- c("s", "e", "a")
  if (!all(required %in% names(policy))) {
    stop("`policy` must include values named s, e, and a.", call. = FALSE)
  }
  for (nm in required) {
    value <- policy[[nm]]
    if (!is.function(value)) {
      if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) {
        stop(sprintf("Policy `%s` must be a finite numeric scalar or function.", nm), call. = FALSE)
      }
    }
  }
  invisible(policy)
}

.validate_params <- function(params) {
  if (is.null(params)) return(invisible(list()))
  if (!is.list(params)) stop("`params` must be a list.", call. = FALSE)
  if (length(params) > 0L && (is.null(names(params)) || any(!nzchar(names(params))))) {
    stop("Every entry in `params` must be named.", call. = FALSE)
  }
  invisible(params)
}

.catalyst_package_version <- function() {
  installed <- tryCatch(
    as.character(utils::packageVersion("catalystanalyticsr")),
    error = function(e) NULL
  )
  if (!is.null(installed)) return(installed)

  description <- file.path(getwd(), "DESCRIPTION")
  if (file.exists(description)) {
    value <- tryCatch(read.dcf(description, fields = "Version")[1, 1], error = function(e) NULL)
    if (!is.null(value) && nzchar(value)) return(as.character(value))
  }
  "dev"
}

.safe_json_value <- function(x) {
  if (is.function(x)) return("<function>")
  if (is.atomic(x) || is.null(x)) return(x)
  if (is.data.frame(x)) return(x)
  if (is.list(x)) return(lapply(x, .safe_json_value))
  as.character(x)
}

.named_list_table <- function(x) {
  if (is.null(x) || !is.list(x) || length(x) == 0L) return(NULL)
  nms <- names(x)
  if (is.null(nms)) return(NULL)
  data.frame(
    name = nms,
    value = vapply(x, function(value) {
      if (is.function(value)) return("<function>")
      if (length(value) == 0L) return("")
      paste(as.character(value), collapse = ",")
    }, character(1)),
    type = vapply(x, function(value) {
      if (is.function(value)) "function" else typeof(value)
    }, character(1)),
    stringsAsFactors = FALSE
  )
}
