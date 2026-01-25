#' A Minimal Plot Theme for Catalyst Analytics R
#'
#' @param base_size Base font size for the theme.
#' @return A ggplot2 theme object.
#' @export
#'
#' @examples
#' # Use in a ggplot
#' ggplot2::ggplot(mtcars, ggplot2::aes(mpg, wt)) +
#'   ggplot2::geom_point() +
#'   theme_catalyst()
theme_catalyst <- function(base_size = 12) {
  ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(
      panel.grid.minor = ggplot2::element_blank(),
      legend.position = "bottom",
      strip.text = ggplot2::element_text(face = "bold")
    )
}

theme_catalyst <- function(base_size = 12) {
  ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(
      panel.grid.minor = ggplot2::element_blank(),
      legend.position = "bottom",
      strip.text = ggplot2::element_text(face = "bold")
    )
}