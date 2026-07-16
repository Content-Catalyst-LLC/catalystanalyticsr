#!/usr/bin/env Rscript
files <- c(
  list.files("R", pattern = "\\.R$", full.names = TRUE),
  list.files("tests", pattern = "\\.R$", full.names = TRUE, recursive = TRUE)
)
if (!length(files)) stop("No R source files found.")
for (file in files) {
  tryCatch(
    parse(file = file, keep.source = TRUE),
    error = function(e) stop(sprintf("R parse failed for %s: %s", file, conditionMessage(e)), call. = FALSE)
  )
}
cat(sprintf("R source parse passed for %d files.\n", length(files)))
