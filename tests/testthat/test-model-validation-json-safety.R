test_that("model-validation S3 records are recursively JSON safe", {
  fixture <- model_validation_fixture()
  card <- model_card(
    intended_uses = "educational scenario analysis",
    prohibited_uses = "forecast",
    calibration_evidence = fixture$calibration$calibration_id,
    validation_evidence = fixture$validation$validation_id,
    limitations = list(limitation_record(
      "synthetic-only", "Synthetic evidence",
      "Not real-world validation.", severity = "high"
    )),
    status = "under_review"
  )
  governance <- model_governance_record(card, reviewers = list("Reviewer"))
  governance <- transition_model_status(
    governance, "validated_for_specified_use", "Reviewer",
    "Approved for synthetic educational use",
    approval = list(decision = "approved")
  )
  benchmark <- solver_benchmark(
    fixture$scenario, methods = "rk4",
    step_sizes = c(1, 0.5), reference_step = 0.5
  )
  stability <- stability_assessment(
    fixture$scenario, perturbation_fraction = 0.001, tolerance = 0.2
  )
  analysis <- model_validation_analysis(
    fixture$calibration, fixture$validation,
    benchmark, stability, governance
  )

  payload <- catalystanalyticsr:::.safe_json_value(list(
    specification = fixture$spec,
    calibration = fixture$calibration,
    validation = fixture$validation,
    benchmark = benchmark,
    stability = stability,
    card = card,
    governance = governance,
    analysis = analysis,
    date = as.Date("2026-07-17"),
    timestamp = as.POSIXct("2026-07-17 12:00:00", tz = "UTC")
  ))

  expect_silent(jsonlite::toJSON(
    payload,
    auto_unbox = TRUE,
    null = "null",
    na = "null",
    dataframe = "rows"
  ))
  expect_true(all(is.finite(benchmark$summary$max_absolute_terminal_error)))
  expect_true(all(is.finite(stability$perturbations$max_relative_terminal_divergence)))
})


test_that("unsupported objects use a plain JSON-safe descriptor", {
  class_name <- "catalyst_json_s4_probe"
  if (!methods::isClass(class_name)) {
    methods::setClass(class_name, slots = c(value = "numeric"))
  }
  on.exit(try(methods::removeClass(class_name), silent = TRUE), add = TRUE)
  probe <- methods::new(class_name, value = 1)
  safe <- catalystanalyticsr:::.safe_json_value(probe)

  expect_type(safe, "character")
  expect_match(safe, "^<unsupported:[^:]+:catalyst_json_s4_probe>$")
  expect_silent(jsonlite::toJSON(safe, auto_unbox = TRUE))
})

test_that("JSON safety handles raw, complex, pairlist, and deep values", {
  payload <- list(
    raw = as.raw(c(0, 15, 255)),
    complex = c(1 + 2i, 3 - 4i),
    pairlist = pairlist(alpha = 1, beta = quote(x + y))
  )
  safe <- catalystanalyticsr:::.safe_json_value(payload)

  expect_equal(safe$raw, c("00", "0f", "ff"))
  expect_equal(safe$complex[[1]], list(real = 1, imaginary = 2))
  expect_equal(safe$pairlist$alpha, 1)
  expect_silent(jsonlite::toJSON(safe, auto_unbox = TRUE, null = "null"))
})
