# Release Contract

## Canonical versions

- Repository release: **0.3.0**
- R package: **0.3.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- Comparative input schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- Model manifest schema: **1.0.0**
- Legacy browser input schema: **1.0.0**
- Browser comparison input schema: **1.1.0**
- WordPress demo plugin: **1.2.0**
- Browser comparison export schema: **1.2.0**

The WordPress plugin follows an independent monotonic version line. Compatibility is declared in `catalyst_analytics_r_manifest.json`.

## Required release checks

```bash
python3 -m pip install pytest jsonschema
python3 scripts/check_release.py
```

When R is installed:

```bash
Rscript scripts/check_r_sources.R
R CMD build .
R CMD check --no-manual catalystanalyticsr_0.3.0.tar.gz
```

## Required comparative contracts

A v0.3.0 release is invalid unless:

- At least two canonical scenarios can execute through `run_scenarios()`.
- Baseline selection is deterministic and rejects ambiguous multiple baselines.
- Comparison metrics exist in every completed run and have consistent directions.
- Absolute and percentage deltas are preserved.
- Rankings respect higher-better and lower-better directions.
- Targets and thresholds preserve operators and observed values.
- Trade-off tables preserve improved, worsened, and tied metrics.
- Pareto diagnostics preserve non-dominated scenarios and dominance relationships.
- Comparison bundles contain canonical scenarios, trajectories, tables, plots, JSON, and checksums.
- The WordPress demo performs a real baseline-versus-policy comparison.
- Browser exports contain two canonical scenarios and explicitly deny numerical parity.
- All JSON fixtures validate against their schemas.
- All exported R functions have documentation aliases.
- No placeholder tests, non-ASCII R source, malformed JSON, JavaScript errors, PHP errors, caches, or version mismatches remain.
