test_that("composite scores expose normalization, weights, and contributions", {
  data <- data.frame(region = c("A", "B"), wealth = c(80, 60), damages = c(10, 30))
  definition <- composite_score_definition(
    "review-score", "Review score", c("wealth", "damages"),
    weights = c(0.6, 0.4), directions = c("higher", "lower"),
    lower_bounds = c(0, 0), upper_bounds = c(100, 50)
  )
  result <- calculate_composite_score(data, definition, entity_fields = "region")
  expect_s3_class(result, "catalyst_composite_score")
  expect_equal(result$scores$composite_score[1], 80)
  expect_equal(nrow(result$components), 4)
  trace <- composite_score_trace(result)
  expect_equal(sum(trace$components$weight), 1)
  expect_match(trace$formula, "normalized_component")
})

test_that("composite weight sensitivity reports score movement", {
  data <- data.frame(wealth = c(80, 60), damages = c(10, 30))
  definition <- composite_score_definition(
    "sensitivity-score", "Sensitivity score", c("wealth", "damages"),
    c(0.6, 0.4), c("higher", "lower"), c(0, 0), c(100, 50)
  )
  sensitivity <- composite_weight_sensitivity(data, definition, 0.20)
  expect_equal(nrow(sensitivity), 4)
  expect_true(all(sensitivity$max_absolute_score_change >= 0))
})

test_that("composite definitions reject hidden weighting errors", {
  expect_error(
    composite_score_definition("bad", "Bad", c("a", "b"), c(0, 0)),
    "At least one"
  )
  expect_error(
    composite_score_definition("bad", "Bad", c("a", "b"), c(1, 1), upper_bounds = c(0, 1)),
    "upper bound"
  )
})
