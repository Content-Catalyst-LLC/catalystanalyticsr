# Export Bundle Specification

Catalyst run export bundles use manifest schema `1.2.0`. Specialized comparison, uncertainty, and data-analysis bundles have their own versioned manifests.

## Core files

Depending on the run, a bundle may contain:

- `trajectory_wide.csv`
- `trajectory_long.csv`
- `sdg_indicators.csv`
- `carbon_budget.csv`
- `scorecard.csv`
- `phase_plane.csv`
- `sensitivities.csv`
- `parameters.csv`
- `policy.csv`
- `run_metadata.json`
- `scenario.json`
- Plot PNG files
- `manifest.json`

## Manifest provenance

The manifest records package version, model id, exact model version, model contract version, requested and normalized run ids, scenario schema version, scenario fingerprint, creation time, files, sizes, and checksums.

`scenario.json` is written only when the run contains a canonical scenario object.

## Comparative scenario bundles - v0.3.0

`export_scenario_comparison()` creates a `comparison_<id>` directory and optional ZIP archive.

Required contents include:

- `scenario_index.csv`
- `terminal_values.csv`
- `deltas.csv`
- `rankings.csv`
- `scorecard.csv`
- `tradeoffs.csv`
- `pareto_front.csv`
- `dominance.csv`
- `rules.csv`
- `rule_results.csv`
- `comparison.json`
- `manifest.json`
- `scenarios/<scenario-id>.json`
- `trajectories/<scenario-id>.csv`
- `plots/<metric>_trajectory.png`
- `plots/<metric>_terminal.png`

The manifest records the package version, baseline id, model version, scenario and metric counts, relative file paths, byte sizes, and MD5 checksums.


## Data-analysis bundles - v0.5.0

`export_data_analysis()` creates a `data_analysis_<id>` directory and optional ZIP archive.

Contents include:

- `data.csv`
- `dataset_manifest.json`
- `source.json`
- `quality_flags.csv`
- `transformations.json`
- `indicator_values.csv` when indicators are calculated
- `indicator_definitions.json`
- `indicator_trace.json`
- `manifest.json`

The manifest records the package version, dataset fingerprint, source id, dimensions, quality-flag count, indicator versions, output-row counts, file sizes, and MD5 checksums. The bundle explicitly records that source quality and unit compatibility require human review and that the result does not constitute a causal claim or autonomous decision.

## Climate-accounting bundles - v0.6.0

`export_climate_accounting()` writes:

- `inventory_manifest.json`
- `emissions_inventory.csv`
- `emissions_summary.csv`
- `carbon_pathway.csv`
- `carbon_diagnostics.csv`
- `terminal_values.csv`
- `kaya_levels.csv` and `kaya_contributions.csv` when available
- `natural_capital_account.csv` and summary when available
- `boundary_definitions.json` and `boundary_assessment.csv` when available
- `manifest.json`
- `brief.md`

The manifest declares contract versions, source fingerprints, accounting basis, included modules, overshoot and stranded-pathway counts, human-review boundaries, and file checksums.

## Inclusive-development bundles - v0.7.0

`export_inclusive_development()` writes:

- `inclusive-development.json`
- `inclusive-wealth.csv`
- `capital-account-summary.csv`
- `adjusted-net-savings.csv`
- `human-development.csv`
- `distribution-analysis.json`
- `distribution-groups.csv`
- `intergenerational-analysis.json`
- `intergenerational-trajectory.csv`
- `composite-score.json`
- `composite-scores.csv`
- `composite-components.csv`
- `inclusive-development-brief.md`
- `manifest.json`
- optional ZIP bundle

The export retains capital reconciliation, shadow prices, population, savings additions and deductions, development goalposts, distribution weights, social floors, composite definitions, contribution trace, and weight sensitivity.
