# Catalyst Analytics R

Catalyst Analytics R is the reproducible sustainability-analysis layer of the Sustainable Catalyst platform. It combines governed data intake, versioned indicators, scenario modeling, comparative analysis, uncertainty, climate and carbon accounting, natural-capital accounting, visualization, and portable evidence bundles.

The repository includes a WordPress companion. The browser tool does not execute R, but its inventory, carbon-pathway, Kaya, natural-capital, boundary, and review records map to the public R contracts.

## v0.6.0 - Climate, Carbon, and Natural-Capital Accounting

Version 0.6.0 turns the earlier carbon-budget and natural-capital concepts into governed accounting modules:

- Normalized greenhouse-gas inventories
- Gross emissions, removals, and net emissions
- Period-total and rate-based accounting
- Declared GWP and CO2-equivalent basis
- Carbon-budget pathways and remaining-budget trajectories
- Overshoot and recovery timing
- Target-year, lock-in, and stranded-pathway diagnostics
- Additive LMDI Kaya decomposition
- Natural-capital opening and closing stocks
- Regeneration, restoration, additions, extraction, degradation, and damages
- Reconciliation errors and stock-and-flow summaries
- At-or-below, at-or-above, and inside-range sustainability boundaries
- Warning margins and unit-mismatch detection
- Auditable climate-accounting export bundles
- WordPress climate-accounting companion

## Versions

- Repository and R package: **0.6.0**
- Emissions-inventory contract: **1.0.0**
- Climate-accounting contract: **1.0.0**
- Natural-capital contract: **1.0.0**
- Sustainability-boundary contract: **1.0.0**
- Dataset contract: **1.0.0**
- Indicator registry contract: **1.0.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- Uncertainty schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- WordPress demo plugin: **1.5.0**
- Browser climate export: **1.5.0**

## Climate-accounting quickstart

```r
path <- system.file(
  "extdata", "climate", "sample_climate_accounting.csv",
  package = "catalystanalyticsr"
)

dataset <- read_catalyst_data(
  path,
  id = "sample-climate-accounting-data",
  title = "Synthetic climate-accounting data",
  time_field = "year",
  entity_fields = "region",
  required_fields = c(
    "year", "region", "emissions", "removals",
    "energy", "gdp", "population"
  ),
  units = list(
    emissions = "MtCO2e",
    removals = "MtCO2e",
    energy = "PJ",
    gdp = "currency_index",
    population = "million_persons"
  )
)

inventory <- as_emissions_inventory(
  dataset,
  emissions_field = "emissions",
  removals_field = "removals",
  energy_field = "energy",
  gdp_field = "gdp",
  population_field = "population",
  gwp_basis = "AR6 GWP100 synthetic CO2e fixture"
)

carbon <- carbon_budget_pathway(
  inventory,
  budget = 300,
  target_year = 2030,
  target_net_emissions = 0
)

carbon_pathway_summary(carbon)
kaya_decomposition(inventory)
```

## Natural-capital account

```r
natural <- natural_capital_from_dataset(
  dataset,
  opening_field = "opening_stock",
  regeneration_field = "regeneration",
  restoration_field = "restoration",
  additions_field = "additions",
  extraction_field = "extraction",
  degradation_field = "degradation",
  damages_field = "damages",
  closing_field = "closing_stock",
  unit = "natural_capital_index"
)

validate_natural_capital_account(natural)
natural_capital_summary(natural)
```

## Boundary assessment

```r
boundaries <- list(
  boundary_definition(
    id = "cumulative-carbon-budget",
    title = "Cumulative net-emissions budget",
    indicator = "cumulative_net_emissions",
    unit = "MtCO2e",
    upper = 300
  ),
  boundary_definition(
    id = "natural-capital-floor",
    title = "Natural-capital closing-stock floor",
    indicator = "natural_capital_closing_stock",
    unit = "natural_capital_index",
    direction = "at_or_above",
    lower = 1000
  )
)

analysis <- climate_accounting(
  inventory,
  budget = 300,
  natural_capital = natural,
  boundaries = boundaries,
  target_year = 2030,
  target_net_emissions = 0,
  analysis_id = "sample-climate-accounting"
)

climate_accounting_summary(analysis)
```

## Reproducible export

```r
export_climate_accounting(
  analysis,
  dir = "outputs",
  prefix = "sample-climate-accounting"
)
```

The bundle contains normalized inventory records, emissions summaries, carbon pathways, budget diagnostics, Kaya levels and contributions, natural-capital accounts, boundary definitions and results, terminal indicators, methodology metadata, checksums, and a review brief.

## Data, indicator, scenario, and uncertainty layers

The earlier governed analytical contracts remain available:

```r
quality <- data_quality_report(dataset)
registered <- list_catalyst_indicators()
net <- calculate_indicator(dataset, "net_emissions")

baseline <- scenario_from_json("examples/scenario_input.json")
policy <- scenario_from_json("examples/uncertainty_input.json")
comparison <- compare_scenarios(run_scenarios(list(baseline, policy)))
ensemble <- run_uncertainty(policy, n = 500, sampling = "latin_hypercube", seed = 42)
```

## WordPress demo

Install `dist/catalyst-analytics-r-demo-v1.5.0.zip` and use:

```text
[catalyst_analytics_r_demo]
```

The public interface creates a deterministic educational emissions pathway, tracks a declared budget, computes a Kaya decomposition, reconciles a natural-capital account, evaluates declared boundaries, and exports a governed JSON record. It does not verify source inventories, select or allocate a scientifically defensible carbon budget, determine a GWP basis, value natural capital, establish compliance, or execute R.

## Repository structure

```text
R/                                  R package functions and contracts
man/                                R package documentation
tests/testthat/                     R behavioral and numerical tests
tests_py/                           Static repository contract tests
inst/extdata/climate/               Climate-accounting CSV and source fixtures
inst/extdata/data/                  General data fixtures
inst/extdata/scenarios/             Canonical scenario fixtures
wordpress/catalyst-analytics-r-demo WordPress browser companion
schemas/                            Dataset, scenario, climate, and export schemas
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
R CMD check --no-manual catalystanalyticsr_0.6.0.tar.gz
```

## Boundaries

Catalyst Analytics R provides transparent exploratory and decision-support analysis. Source and organizational boundaries, gas coverage, GWP basis, carbon-budget allocation, temporal interpretation, natural-capital measurement and valuation, and indicator suitability require human review. Outputs are not forecasts, compliance determinations, autonomous decisions, or professional advice.
