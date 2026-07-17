# Catalyst Analytics R

Catalyst Analytics R is the reproducible sustainability-analysis layer of the Sustainable Catalyst platform. It provides governed scenario records, versioned analytical models, vector-dynamics simulation, sustainability indicators, carbon-budget review, comparative analysis, visualization, and portable evidence bundles.

The repository also includes a WordPress demo plugin. The browser tool uses simplified equations, but its inputs and exports are mapped to the canonical R scenario and comparison contracts.

## v0.4.0 — Comparative Scenario Engine

Version 0.4.0 adds governed uncertainty, sensitivity, and stress testing to the comparative analytical system:

- Batch execution with `run_scenarios()`
- Baseline, intervention, counterfactual, and exploratory roles
- Automatic or explicit baseline selection
- Common-indicator validation across runs
- Absolute and percentage deltas
- Direction-aware improvement and deterioration status
- Per-metric rankings
- Targets and thresholds with explicit operators
- Comparative scorecards
- Trade-off classification
- Pareto-frontier and dominance diagnostics
- Overlaid trajectory, terminal-value, delta, and trade-off plots
- Reproducible comparison export bundles
- Baseline-versus-policy WordPress demo

## Versions

- Repository and R package: **0.4.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- WordPress demo plugin: **1.3.0**
- Browser uncertainty export: **1.3.0**

## Comparative quickstart

```r
baseline <- catalyst_scenario(
  title = "Reference baseline",
  id = "reference-baseline",
  role = "baseline",
  times = 0:20,
  policy = list(s = 0.18, e = 0.03, a = 0.01),
  parameters = list(emissions_intensity = 0.30, regen = 0.02)
)

policy <- catalyst_scenario(
  title = "Transition policy",
  id = "transition-policy",
  role = "intervention",
  times = 0:20,
  policy = list(s = 0.24, e = 0.07, a = 0.10),
  parameters = list(emissions_intensity = 0.12, regen = 0.05)
)

runs <- run_scenarios(list(baseline, policy))
comparison <- compare_scenarios(
  runs,
  metrics = c("gdp", "emissions", "ans", "natural_capital"),
  targets = list(ans = 0),
  thresholds = list(emissions = list(value = 0.25, operator = "<="))
)

scenario_deltas(comparison)
scenario_rankings(comparison)
scenario_scorecard(comparison)
pareto_diagnostics(comparison)
plot_scenario_comparison(comparison, "emissions", "trajectory")
```

## Comparative export

```r
export_scenario_comparison(
  comparison,
  dir = "outputs",
  comparison_id = "reference-vs-transition"
)
```

The bundle contains canonical scenario JSON, trajectory CSV files, terminal values, deltas, rankings, scorecards, target and threshold results, trade-off tables, Pareto diagnostics, plots, a machine-readable comparison record, and a checksummed manifest.

## WordPress demo

Install `dist/catalyst-analytics-r-demo-v1.3.0.zip` and use:

```text
[catalyst_analytics_r_demo]
```

The public interface compares a baseline and policy pathway. It does not execute the R runtime and does not claim numerical parity with the R package.

## Repository structure

```text
R/                                  R package functions and contracts
man/                                R package documentation
tests/testthat/                     R behavioral and numerical tests
tests_py/                           Static repository contract tests
inst/extdata/                       Packaged scenario and model fixtures
wordpress/catalyst-analytics-r-demo WordPress comparative demo
schemas/                            Scenario, model, comparison, and browser schemas
examples/                           Example inputs
outputs/                            Example exports
docs/                               Methodology and release documentation
scripts/                            Release validation
```

## Validation

```bash
python3 -m pip install pytest jsonschema
python3 scripts/check_release.py
Rscript scripts/check_r_sources.R
R CMD build .
R CMD check --no-manual catalystanalyticsr_0.4.0.tar.gz
```

## Boundaries

Catalyst Analytics R provides transparent exploratory and decision-support analysis. Its outputs are not forecasts, compliance determinations, autonomous decisions, or professional advice.

## Uncertainty, sensitivity, and stress testing

```r
scenario <- scenario_from_json("examples/uncertainty_input.json")
ensemble <- run_uncertainty(
  scenario,
  n = 500,
  sampling = "latin_hypercube",
  seed = 42,
  thresholds = list(emissions = list(value = 0.2, operator = "<="))
)
uncertainty_summary(ensemble)
global_sensitivity(ensemble)
plot_tornado(ensemble, "emissions")
```

Named stress cases can combine multiple parameter, policy, state, or constraint shocks and are evaluated through the comparative scenario engine.
