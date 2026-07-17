# Changelog

## 0.8.0 - Calibration, Validation, and Model Governance

### R CMD check repair 3

- Updated the remaining v0.7.0 export-manifest expectations to v0.8.0.
- Added pre-optimization validation for calibration targets.
- Calibration now rejects unsupported sections and missing parameter, policy, or initial-state fields deterministically.
- Added regression coverage for syntactically valid but unregistered calibration targets.

### R CMD check serialization repair 2

- Replaced the terminal JSON fallback with a non-throwing, class-aware descriptor.
- Added explicit handling for raw, complex, pairlist, and excessive-depth values.
- Added regression coverage for unsupported S4 objects and special R value types.
- Preserved recursive sanitization for Catalyst records without invoking unsafe default character coercion.


### R CMD check repair

- Added recursive JSON sanitization for nested Catalyst S3 records, dates, timestamps, factors, language objects, functions, environments, matrices, and data-frame columns.
- Corrected model-validation and governance exports so `jsonlite` never receives unsupported custom S3 classes.
- Replaced ambiguous one-row data-frame coercion in solver benchmarks, stability assessment, and initial-state extraction with explicit per-metric scalar extraction.
- Added regression coverage for governed JSON serialization and finite numerical benchmark evidence.

- Added bounded model calibration through `stats::optim`.
- Added calibration/holdout partitioning, error metrics, and residual diagnostics.
- Added solver/time-step benchmarks, stability tests, invariants, and boundary checks.
- Added model cards, parameter cards, assumptions, limitations, reviewers, approvals, and lifecycle transitions.
- Added integrated validation/governance exports and browser companion v1.7.0.

## 0.7.0 - Inclusive Wealth, Human Development, and Distribution

- Added produced-, human-, and natural-capital stock-and-flow accounts with reconciliation and declared shadow prices.
- Added inclusive-wealth totals, capital composition, per-capita wealth, and intergenerational trajectories.
- Added Adjusted Net Savings decomposition and human-development dimension indices.
- Added weighted distribution, social-floor, Gini, Palma, and group-share diagnostics.
- Added transparent composite-score definitions, normalization trace, and weight sensitivity.
- Added integrated inclusive-development exports, schemas, fixtures, documentation, and WordPress demo v1.6.0.

## 0.6.0 - Climate, Carbon, and Natural-Capital Accounting

- Added governed greenhouse-gas inventories with gross emissions, removals, net emissions, source, unit, GWP basis, and scope records.
- Added period-total and rate-based carbon-budget pathways with overshoot, recovery, lock-in, target-year, and stranded-pathway diagnostics.
- Added additive LMDI Kaya identity decomposition with numerical reconciliation.
- Added natural-capital stock-and-flow accounts covering regeneration, restoration, additions, extraction, degradation, damages, and closing-stock reconciliation.
- Added sustainability-boundary definitions, warning margins, unit checks, assessments, summaries, and plots.
- Added climate-accounting orchestration, terminal indicators, export bundles, schemas, examples, fixtures, and regression tests.
- Added climate-specific built-in indicators for net emissions, removal share, energy intensity, and natural-capital balance.
- Upgraded the WordPress demo to v1.5.0 with carbon pathways, Kaya drivers, natural-capital reconciliation, boundary signals, and governed JSON export.

## 0.5.0 - Data Intake and Indicator Registry

### R CMD check repair

- Updated stale package and bundle-schema expectations in the export tests.
- Qualified `stats::setNames()` and `stats::reorder()` calls and registered the comparative delta plotting binding.
- Corrected the stress-test exporter to use the comparative bundle API.
- Completed uncertainty and stress-test Rd argument documentation.

- Added governed CSV and JSON data import with versioned dataset contracts.
- Added source, license, citation, geography, sector, currency, price-year, unit, checksum, and transformation metadata.
- Added missing-value, duplicate-row, duplicate-key, time-order, and frequency quality diagnostics.
- Added a linear unit-conversion registry and traceable dataset transformations.
- Added versioned indicator definitions, registry discovery, custom registration, grouped calculation, and formula/source/unit trace records.
- Added reproducible data-analysis bundles and indicator definitions to scenario exports.
- Added dataset, indicator, data-analysis, and browser export schemas and fixtures.
- Upgraded the WordPress demo to v1.4.0 with CSV intake, quality review, indicator calculation, and governed JSON export.

## 0.4.0 - Uncertainty, Sensitivity, and Stress Testing

- Added canonical uncertainty specifications and strict distribution validation.
- Added Monte Carlo and Latin hypercube sampling with reproducible seeds.
- Added ensemble intervals, threshold probabilities, local and global sensitivity, stress cases, plots, and reproducible exports.
- Upgraded the WordPress demo to v1.3.0 with uncertainty bands and probability summaries.

## 0.3.0 — Comparative Scenario Engine

- Added governed multi-scenario execution.
- Added baseline-aware deltas, rankings, scorecards, targets, thresholds, trade-offs, and Pareto diagnostics.
- Added comparative plots and reproducible comparison bundles.
- Added comparison JSON schemas, examples, and contract tests.
- Upgraded the WordPress demo to v1.2.0 with baseline-versus-policy comparison.

## 0.2.0 - Canonical Scenario Contract and Model Registry

- Added the versioned `catalyst_scenario` contract and JSON schema 1.0.0.
- Added scenario construction, validation, JSON import/export, stable fingerprints, and execution.
- Added legacy R scenario and browser-input migration to the canonical contract.
- Added the governed `catalyst_model` interface, registry, discovery, exact version lookup, and serializable manifests.
- Registered KH-NC-PA model version 1.0.0 with state, flow, unit, parameter, policy, and indicator contracts.
- Refactored the shared numerical integrator to execute registered model callbacks.
- Added deterministic canonical, browser mapping, model manifest, and RK4 numerical fixtures.
- Added tolerance-based numerical regression tests and custom-model registry tests.
- Added scenario and model provenance to export bundles.
- Updated the WordPress demo to v1.1.0 with canonical scenario exports and `mapped_contract` parity status.
- Added scenario, model, browser-input, and browser-export schema validation to the release suite.

## 0.1.4 — Repository Integrity and Package Contract Repair

- Repaired duplicate functions and duplicated documentation blocks.
- Replaced placeholder tests with behavioral package tests.
- Added shared input validation and stricter model parameter contracts.
- Corrected export metadata, parameter, policy, and file-inventory outputs.
- Added versioned scenario-input and browser-export schemas.
- Moved raw package JSON resources to `inst/extdata`.
- Added repository release checks and expanded CI.
- Updated the WordPress demo to v1.0.1 with an explicit conceptual-parity boundary.
- Corrected the deterministic demo test to compare numeric trajectories while preserving distinct scenario labels.
- Removed non-ASCII characters from R source and added an ASCII portability contract.
- Added `.Rbuildignore` exclusions for repository-only directories and generated caches.
- Disabled pytest cache creation during release checks.

## 2026-07-01

### Added
- WordPress demo plugin with shortcode `[catalyst_analytics_r_demo]`.
- Browser-based scenario comparison demo.
- JSON export support for demo outputs.
- Scenario JSON schema.
- Sample scenario input and example output.
- Documentation for methodology, reproducibility, exports, and WordPress use.
- Python brief generator for exported scenario records.
- CI workflow for lightweight repository validation.

### Updated
- README repositioned around Catalyst Analytics R as the reproducible analytics layer of Sustainable Catalyst.
- Repository structure clarified around R package, online demo, schemas, docs, and tests.

### Notes
- The browser demo is intentionally simplified and does not run the R package in WordPress.
- The R package remains the source for deeper reproducible analytics.
