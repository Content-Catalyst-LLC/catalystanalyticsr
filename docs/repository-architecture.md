# Repository Architecture

Catalyst Analytics R has four governed layers.

## 1. Contract layer

- Canonical scenario schema and R object
- Model definitions and registry
- Model manifests
- Scenario migrations and browser mappings
- Numerical and compatibility fixtures

## 2. R analytical layer

- Registered-model simulation with RK4 or Euler integration
- Adjusted Net Savings
- Carbon-budget checks
- Indicator summaries
- Phase-plane and local sensitivity tools for KH-NC-PA
- Plots and portable export bundles

## 3. Data and indicator layer

- Governed CSV and JSON intake
- Dataset source, unit, geography, sector, currency, and transformation metadata
- Entity-aware time-series and duplicate-key validation
- Stable dataset fingerprints
- Versioned indicator registry and custom definitions
- Traceable indicator calculations
- Data-analysis export bundles

## 4. WordPress demo layer

The public plugin runs a lightweight JavaScript data-intake and indicator interface. It emits the documented browser data contract but does not execute arbitrary R code or replace governed R analysis.

## Separation boundary

`mapped_data_indicator_contract` means the browser and R layers share dataset, source, quality, indicator, unit, and trace concepts. It does not imply that browser execution is equivalent to arbitrary R analysis.

## Comparative scenario layer - v0.3.0

The comparative layer sits above canonical scenario execution:

```text
canonical scenarios
        |
        v
run_scenarios()
        |
        v
catalyst_scenario_set
        |
        v
compare_scenarios()
        |
        +--> deltas and rankings
        +--> targets and thresholds
        +--> trade-off classification
        +--> Pareto diagnostics
        +--> comparative plots
        +--> export_scenario_comparison()
```

The layer does not alter model equations. It compares outputs from exact model versions and preserves every scenario's canonical contract and fingerprint.


## Data and indicator layer - v0.5.0

```text
CSV or JSON records
        |
        v
read_catalyst_data() / as_catalyst_dataset()
        |
        +--> source and license records
        +--> units and scope metadata
        +--> quality diagnostics
        +--> transformation history
        +--> stable fingerprint
        |
        v
indicator registry
        |
        v
calculate_indicator(s)()
        |
        +--> values
        +--> definitions
        +--> trace metadata
        +--> export_data_analysis()
```

The layer preserves the source-to-formula-to-output chain and keeps causal or autonomous-decision claims outside the package contract.

## Climate-accounting layer - v0.6.0

- `R/emissions_inventory.R` normalizes documented emissions inventories.
- `R/carbon_accounting.R` calculates carbon pathways and Kaya decomposition.
- `R/natural_capital_accounting.R` reconciles natural-capital stocks and flows.
- `R/boundary_accounting.R` defines and evaluates sustainability boundaries.
- `R/climate_accounting.R` assembles the governed analysis object.
- `R/export_climate_accounting.R` produces portable accounting bundles.
- `schemas/catalyst_analytics_r_*climate*.schema.json` governs machine-readable exchange.

## Inclusive-development layer - v0.7.0

```text
capital stock-and-flow accounts
        |
        +--> produced capital
        +--> human capital
        +--> natural capital
        |
        v
inclusive wealth and per-capita wealth
        |
        +--> Adjusted Net Savings
        +--> human-development dimensions
        +--> distribution and social floor
        +--> intergenerational trajectory
        +--> composite score and weight sensitivity
        |
        v
inclusive_development_analysis()
        |
        v
export_inclusive_development()
```

The layer preserves valuation, weighting, normalization, and interpretation choices rather than presenting them as objective facts.
