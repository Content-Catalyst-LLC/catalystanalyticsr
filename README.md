# Catalyst Analytics R

Catalyst Analytics R is the reproducible analytics layer for the Sustainable Catalyst platform. It provides an R package for governed sustainability scenarios, versioned analytical models, vector-dynamics simulation, indicator computation, carbon-budget review, adjusted-net-savings reasoning, visualization, and portable export bundles.

The repository also includes a WordPress demo plugin so the public Catalyst Analytics R page can offer an exploratory browser tool without requiring a server-side R runtime.

## v0.2.0 foundation

Version 0.2.0 introduces the shared contracts required for future analytical expansion:

- Canonical `catalyst_scenario` objects with schema version `1.0.0`
- Governed `catalyst_model` definitions and an in-process model registry
- Exact model id and version resolution
- JSON scenario import, export, migration, and fingerprints
- Legacy R scenario migration from schema `0.1.0`
- Browser-input mapping to and from canonical scenarios
- Deterministic numerical reference fixtures
- Tolerance-based RK4 regression tests
- Model and scenario provenance in export bundles
- Browser exports containing a canonical scenario record

## Repository structure

```text
R/                                  R package functions and contracts
man/                                R package documentation
tests/testthat/                     R package behavior and numerical tests
tests/fixtures/                     Mapping and numerical reference fixtures
inst/extdata/scenarios/             Packaged canonical and legacy scenarios
inst/extdata/models/                Packaged model manifests
wordpress/catalyst-analytics-r-demo WordPress shortcode demo plugin
docs/                               Methodology and contract documentation
schemas/                            Canonical JSON schemas
examples/                           Example canonical and browser records
outputs/                            Example browser export
python/                             Lightweight brief generator
.github/workflows/                  CI checks
```

## Release versions

- Repository and R package: **0.2.0**
- Canonical scenario schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- Model manifest schema: **1.0.0**
- WordPress demo plugin: **1.1.0**
- Browser export schema: **1.1.0**

See `RELEASE_CONTRACT.md` and `docs/releases/v0.2.0.md`.

## Canonical scenario quickstart

```r
scenario <- catalyst_scenario(
  title = "Policy pathway",
  id = "policy-pathway",
  role = "intervention",
  times = 0:20,
  policy = list(s = 0.22, e = 0.05, a = 0.08),
  parameters = list(
    emissions_intensity = 0.07,
    regen = 0.06
  ),
  constraints = list(emissions_budget = 5)
)

validate_catalyst_scenario(scenario)
scenario_fingerprint(scenario)

json <- scenario_to_json(scenario)
restored <- scenario_from_json(json)

run <- run_catalyst_scenario(
  restored,
  include_phase_plane = FALSE,
  include_sensitivity = FALSE
)

summary(run)
plot(run)
```

## Model registry

```r
list_catalyst_models()

model <- get_catalyst_model("khncpa", "1.0.0")
print(model)

manifest <- catalyst_model_manifest(model)
```

Custom models can be defined with `new_catalyst_model()` and registered with `register_catalyst_model()`. The shared integrator resolves the model's declared states, defaults, units, flow mapping, indicator mapping, and supported numerical methods.

## Browser compatibility

The WordPress demo shortcode is:

```text
[catalyst_analytics_r_demo]
```

The browser engine remains simplified. Version 1.1.0 maps browser inputs into the canonical scenario contract and includes that record in downloaded JSON. `parity_status: mapped_contract` means the structures and assumptions are transferable; it does not claim numerical identity between the JavaScript and R equations.

## Export bundles

`catalyst_export()` writes trajectories, indicators, plots, parameters, policy controls, run metadata, a file inventory, and—when a canonical scenario was used—the complete `scenario.json` plus its fingerprint and exact model version.

```r
out <- catalyst_export(
  run,
  dir = "analysis_outputs",
  run_id = "policy-pathway",
  zip = TRUE,
  overwrite = TRUE
)
```

## Methodology

```text
question -> assumptions -> scenario -> model -> indicators -> output -> interpretation -> review
```

The goal is not to produce certainty. The goal is to make assumptions visible, contracts versioned, calculations reproducible, outputs exportable, and interpretation reviewable.

## Boundaries

Catalyst Analytics R is an educational, open-source decision-support package. It does not provide legal, financial, investment, engineering, environmental, compliance, scientific, or other professional advice. Outputs depend on data quality, assumptions, model design, numerical configuration, and interpretation.

## License

MIT. See `LICENSE`.
