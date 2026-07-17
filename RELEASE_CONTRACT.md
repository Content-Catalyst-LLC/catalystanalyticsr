# Release Contract

## Canonical versions

- Repository release: **0.5.0**
- R package: **0.5.0**
- Dataset contract: **1.0.0**
- Indicator registry contract: **1.0.0**
- Data-analysis export: **1.0.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- Uncertainty schema: **1.0.0**
- Stress-test schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- WordPress demo plugin: **1.4.0**
- Browser data export: **1.4.0**

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
R CMD check --no-manual catalystanalyticsr_0.5.0.tar.gz
```

## Dataset contract

A v0.5.0 release is invalid unless:

- CSV and JSON inputs produce governed `catalyst_dataset` objects.
- Dataset identifiers, fields, source records, units, and required fields validate before analysis.
- Entity/time keys identify duplicate records.
- Missing cells, duplicate rows, time order, and frequency remain visible in the quality report.
- Source publisher, license, retrieval date, citation, and file checksum can be preserved.
- Geography, sector, currency, and price-year metadata remain attached to the dataset.
- Every transformation adds an operation, description, fields, parameters, actor, and timestamp.
- Dataset fingerprints are deterministic for unchanged contracts and records.
- Unit conversions are explicit, dimensioned, and recorded in transformation history.

## Indicator registry contract

- Every indicator has a stable id, semantic version, title, description, formula, required fields, unit, direction, aggregation, source, targets, and calculation callback.
- Registry lookup may resolve an exact version and may not silently overwrite an existing id/version.
- Calculations reject absent or non-numeric required fields.
- Rowwise calculations return one result per input row.
- Aggregate calculations return one result per declared group.
- Every calculation preserves the dataset fingerprint, source record, field units, formula, indicator version, sample size, grouping, missing-cell count, and timestamp.
- Existing model exports include matching registered indicator definitions when available.

## Browser boundary

- The WordPress demo performs real CSV parsing, structural quality checks, and formula calculations.
- Browser exports declare repository compatibility, dataset and indicator contract versions, and the selected definition.
- Browser outputs state that source validity and unit compatibility are unverified.
- The browser does not claim causal identification, compliance, professional advice, or R-runtime parity.

## Repository integrity

- All JSON fixtures validate against their schemas.
- All exported R functions have documentation aliases.
- R source is ASCII portable and lexically balanced.
- JavaScript and PHP syntax checks pass.
- No placeholder tests, caches, `.Rcheck` directories, generated package archives, or version mismatches remain.
