# Changelog

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
