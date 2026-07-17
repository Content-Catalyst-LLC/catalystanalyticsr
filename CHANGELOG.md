# Changelog

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
