# Catalyst Analytics R

Catalyst Analytics R is the reproducible sustainability-analysis layer of the Sustainable Catalyst platform. It combines governed data intake, versioned indicator definitions, scenario modeling, comparative analysis, uncertainty, stress testing, visualization, and portable evidence bundles.

The repository also includes a WordPress companion. The browser tool does not execute R, but its dataset, indicator, quality, and trace records map to the public R contracts.

## v0.5.0 - Data Intake and Indicator Registry

Version 0.5.0 adds the governed data layer required before model calibration and broader sustainability accounting:

- CSV and JSON data import
- Versioned `catalyst_dataset` contracts
- Source, publisher, license, citation, and retrieval metadata
- Dataset fingerprints and file checksums
- Tidy time-series and entity-key validation
- Missing-value, duplicate-row, duplicate-key, and time-order flags
- Geographic, sector, currency, and price-year metadata
- Field-level units and a linear unit-conversion registry
- Transformation-history records
- Versioned `catalyst_indicator` definitions
- Built-in per-capita, carbon-intensity, cumulative-emissions, adjusted-net-savings, and natural-capital indicators
- Custom indicator registration
- Grouped indicator calculations
- Formula, unit, source-field, and calculation trace records
- Reproducible data-analysis export bundles
- WordPress data-intake and indicator-registry demo

## Versions

- Repository and R package: **0.5.0**
- Dataset contract: **1.0.0**
- Indicator registry contract: **1.0.0**
- Data-analysis export: **1.0.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- Uncertainty schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- WordPress demo plugin: **1.4.0**
- Browser data export: **1.4.0**

## Data-intake quickstart

```r
path <- system.file(
  "extdata", "data", "sample_country_timeseries.csv",
  package = "catalystanalyticsr"
)

dataset <- read_catalyst_data(
  path,
  id = "regional-sustainability",
  title = "Regional sustainability time series",
  time_field = "year",
  entity_fields = "region",
  required_fields = c("year", "region", "gdp", "population", "emissions"),
  units = list(
    year = "year",
    gdp = "currency_index",
    population = "person_index",
    emissions = "tCO2e_index"
  )
)

print(dataset)
data_quality_report(dataset)
dataset_manifest(dataset)
```

## Indicator registry quickstart

```r
list_catalyst_indicators()

carbon <- calculate_indicator(dataset, "carbon_intensity")
savings <- calculate_indicator(dataset, "adjusted_net_savings")
regional_emissions <- calculate_indicator(
  dataset,
  "cumulative_emissions",
  group_by = "region"
)

carbon$values
indicator_trace(carbon)
```

Register a custom indicator with an explicit formula and calculation callback:

```r
savings_rate <- new_catalyst_indicator(
  id = "savings_rate_observed",
  version = "1.0.0",
  title = "Observed savings rate",
  description = "Gross savings divided by GDP.",
  formula = "gross_savings / gdp",
  required_fields = c("gross_savings", "gdp"),
  unit = "fraction",
  direction = "higher_better",
  aggregation = "rowwise",
  source = list(type = "derived"),
  calculation = function(data, dataset, na_rm) data$gross_savings / data$gdp
)

register_catalyst_indicator(savings_rate)
calculate_indicator(dataset, "savings_rate_observed")
```

## Data-analysis export

```r
export_data_analysis(
  dataset,
  indicators = c(
    "carbon_intensity",
    "adjusted_net_savings",
    "cumulative_emissions"
  ),
  group_by = "region",
  dir = "outputs",
  analysis_id = "regional-indicator-review"
)
```

The bundle contains source records, dataset metadata, quality flags, transformation history, indicator definitions, calculated values, calculation traces, checksums, and a machine-readable manifest.

## Scenario and uncertainty analysis

The v0.2.0-v0.4.0 analytical contracts remain available:

```r
baseline <- scenario_from_json("examples/scenario_input.json")
policy <- scenario_from_json("examples/uncertainty_input.json")
comparison <- compare_scenarios(run_scenarios(list(baseline, policy)))
ensemble <- run_uncertainty(policy, n = 500, sampling = "latin_hypercube", seed = 42)
```

Existing scenario bundles now include registered indicator definitions alongside indicator values.

## WordPress demo

Install `dist/catalyst-analytics-r-demo-v1.4.0.zip` and use:

```text
[catalyst_analytics_r_demo]
```

The public interface parses pasted CSV records, reports quality flags, calculates a selected governed indicator, displays its formula and required fields, and exports a data-and-indicator trace. It does not verify the truth, license, geographic comparability, currency basis, or methodological suitability of user-supplied data.

## Repository structure

```text
R/                                  R package functions and contracts
man/                                R package documentation
tests/testthat/                     R behavioral and numerical tests
tests_py/                           Static repository contract tests
inst/extdata/data/                  Packaged CSV, JSON, and source fixtures
inst/extdata/scenarios/             Canonical scenario fixtures
wordpress/catalyst-analytics-r-demo WordPress data-intake demo
schemas/                            Dataset, indicator, scenario, and export schemas
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
R CMD check --no-manual catalystanalyticsr_0.5.0.tar.gz
```

## Boundaries

Catalyst Analytics R provides transparent exploratory and decision-support analysis. Data import does not establish source validity, licensing rights, unit compatibility, causal identification, or fitness for a particular decision. Outputs are not forecasts, compliance determinations, autonomous decisions, or professional advice.
