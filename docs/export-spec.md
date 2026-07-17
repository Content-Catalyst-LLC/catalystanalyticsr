# Export Bundle Specification

Catalyst export bundles use manifest schema `1.1.0`.

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
