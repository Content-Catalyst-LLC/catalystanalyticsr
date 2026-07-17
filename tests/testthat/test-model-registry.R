test_that("built-in model is discoverable and versioned", {
  models <- list_catalyst_models()
  expect_true(any(models$id == "khncpa" & models$version == "1.0.0"))

  model <- get_catalyst_model("khncpa", "1.0.0")
  expect_s3_class(model, "catalyst_model")
  expect_identical(model$required_states, c("K", "H", "N", "C", "P", "A"))
  expect_true(all(c("gdp", "emissions", "ans") %in% names(model$indicator_map)))

  manifest <- catalyst_model_manifest(model)
  expect_equal(manifest$schema_version, "1.0.0")
  expect_equal(manifest$id, "khncpa")
  expect_equal(manifest$version, "1.0.0")
})

test_that("custom registered models execute through the shared integrator", {
  custom <- new_catalyst_model(
    id = "registry-test",
    version = "1.0.0",
    title = "Registry test model",
    required_states = "X",
    default_state = c(X = 2),
    default_parameters = list(rate = 0),
    default_policy = list(control = 0),
    state_units = c(X = "index"),
    flow_map = c(
      gdp = "Y", consumption = "consumption", savings = "savings",
      education = "education", abatement = "abatement", emissions = "emissions",
      depletion = "depletion", damages = "damages"
    ),
    flow_units = c(
      gdp = "index", consumption = "index", savings = "index", education = "index",
      abatement = "share", emissions = "index", depletion = "index", damages = "index"
    ),
    indicator_map = list(
      state = list(source = "X", unit = "index", direction = "higher_better")
    ),
    derivative = function(t, state, policy, params) c(X = params$rate),
    flows = function(t, state, policy, params) list(
      Y = state[["X"]], consumption = state[["X"]], savings = 0,
      education = 0, abatement = policy$control, emissions = 0,
      depletion = 0, damages = 0
    ),
    build_params = function(params, initial_state) utils::modifyList(list(rate = 0), params),
    validate_state = function(x) {
      if (!is.numeric(x) || is.null(names(x)) || !"X" %in% names(x)) stop("state")
      c(X = as.numeric(x[["X"]]))
    },
    validate_policy = function(x) {
      if (!is.list(x) || is.null(x$control)) stop("policy")
      invisible(x)
    },
    validate_params = function(x) {
      if (!is.list(x)) stop("params")
      invisible(x)
    }
  )
  register_catalyst_model(custom, overwrite = TRUE)
  result <- simulate_dynamics(0:3, c(X = 2), model = "registry-test", params = list(rate = 1))
  expect_equal(result$trajectory_wide$X, 2:5)
  expect_equal(result$meta$model_version, "1.0.0")

  scenario <- catalyst_scenario(
    title = "Registered custom scenario",
    id = "registered-custom-scenario",
    model = "registry-test",
    model_version = "1.0.0",
    times = 0:2,
    initial_state = c(X = 2),
    parameters = list(rate = 1),
    metadata = list(created_at = "2026-07-16T00:00:00Z")
  )
  run <- run_catalyst_scenario(
    scenario,
    include_phase_plane = FALSE,
    include_sensitivity = FALSE
  )
  expect_equal(run$trajectory_wide$X, 2:4)
  expect_equal(unique(run$sdg_indicators$indicator), "state")
})
