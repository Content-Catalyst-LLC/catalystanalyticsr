# Changelog

## v1.5.0 repair — WordPress compatibility test parity

- Updated the production-readiness regression test to expect WordPress companion v2.5.0.
- Added a release-contract guard that rejects stale v2.4.0 compatibility expectations.
- No package API, schema, analytical behavior, or WordPress companion code changed.


## 1.5.0

- Added a versioned public API manifest, endpoint records, request and response envelopes, and in-process dispatch.
- Added first-party handoffs for Site Intelligence, Research Lab, Workbench, Catalyst Canvas, Decision Studio, and Knowledge Library.
- Added portable handoff bundles, workspace storage, schemas, fixtures, tests, documentation, and WordPress companion v2.5.0.
- Preserved human-review, provenance, licensing, uncertainty, and non-authorization boundaries across every platform transfer.

## 1.4.0

### v1.4.0 documentation repair V2

- Rebuilt `export_policy_evaluation.Rd` as valid multiline Rd.
- Removed a stray literal `\n` token outside documentation sections.
- Added package-wide Rd integrity checks for stray escaped newlines, terminal newlines, and balanced usage blocks.

### R CMD check Rd usage repair

- Replaced escaped `\n` text in econometrics and workspace Rd usage sections with real line breaks.
- Rebuilt the econometrics usage signatures from the exported R function definitions.
- Added static regression checks for multiline, balanced, syntactically parseable usage blocks.

- Added governed regression and panel-data specifications.
- Added classical, HC1, and cluster-robust uncertainty.
- Added difference-in-differences, event studies, interrupted time series, and synthetic controls.
- Added causal-assumption records, diagnostics, policy-effect summaries, workspace libraries, publication bundles, and WordPress companion v2.4.0.


## 1.3.0 - Optimization and Policy Pathway Design

- Added governed decision variables, objectives, constraints, and optimization specifications.
- Added grid and reproducible random-search evaluation with feasible-region and Pareto diagnostics.
- Added target-seeking canonical scenarios, cost-effectiveness, and marginal-abatement analysis.
- Added adaptive stages, human decision gates, evidence triggers, pathway sequencing, and robustness/regret analysis.
- Added workspace optimization and pathway libraries, portable export bundles, schemas, fixtures, and tests.
- Added WordPress companion v2.3.0.


## 1.2.0 - Regional, Sector, and Portfolio Analytics

### v1.2.0 R CMD check repair

- Normalize omitted and JSON `null` regional portfolio `price_year` values to `NA_integer_`.
- Make regional portfolio construction and validation safely accept nullable price years.
- Add regression coverage for null, omitted, non-scalar, and out-of-range price years.

- Added governed geography and sector scopes.
- Added scoped scenario mapping and reusable regional portfolio members.
- Added weighted portfolio aggregation and multi-region ranking.
- Added regional carbon-budget pathways and sector transition diagnostics.
- Added workspace regional-portfolio libraries and portable analytics export.
- Added WordPress companion v2.2.0.

## 1.1.0 - Saved Workspaces and Scenario Libraries

### R CMD check workspace snapshot fingerprint repair

- Preserved exact in-memory snapshot state instead of eagerly flattening nested project objects.
- Added a restoration fingerprint identity that survives canonical JSON import and is cleared by the next semantic workspace change.
- Excluded restoration-only fingerprint metadata from canonical workspace JSON.
- Added regression coverage for in-memory restoration, JSON-imported restoration, and fingerprint invalidation after edits.

### R CMD check workspace null-contract repair

- Preserved `active_project_id` as an explicit named `NULL` field when the last workspace project is removed.
- Normalized missing and JSON-null active-project values during workspace import and snapshot restoration.
- Preserved omitted run results as an explicit `result: null` field so R cannot partially match `$result` to `result_summary`.
- Added regression coverage for empty-workspace JSON round trips, project removal, snapshot restoration, and lightweight workspace exports.

- Added persistent multi-project workspaces and active-project selection.
- Added reusable scenario, parameter-set, and policy-package libraries.
- Added scenario cloning, consolidated run history, and project comparison.
- Added workspace snapshots with complete state restoration.
- Added portable workspace JSON, CSV, Markdown, integrity, and ZIP bundles.
- Added workspace schemas, fixtures, documentation, and regression tests.
- Upgraded the WordPress companion to v2.1.0.

## 1.0.0 - Reproducible Sustainability Analytics Engine

- Declared the stable 1.x public API and compatibility policy.
- Added machine-readable release-readiness gates with fail-closed validation.
- Added production, accessibility, browser-boundary, security, privacy, migration, and tutorial documentation.
- Added versioned release-readiness schema, fixtures, and tests.
- Upgraded the WordPress companion to v2.0.0 with a production-contract readiness view.
- Hardened CI and installer gates so R CMD check must be clean before commit or push.


## 0.9.0 - Reproducible Projects and Analytical Publication

### R CMD check repair

- Corrected publication-manifest file counting when `jsonlite::read_json(..., simplifyVector = TRUE)` returns file records as a data frame.
- Added an explicit `file_count` and integrity scope covering all bundle files except the self-referential manifest.
- Qualified `capture.output()` through `utils` to eliminate the namespace NOTE.
- Added regression and static release checks for manifest count consistency and namespace qualification.

- Added the governed `catalyst_project` contract for scenarios, datasets, models, parameter sets, runs, indicators, plots, notes, reviews, snapshots, publications, and software environments.
- Added stable project fingerprints and run-level input/output hashes.
- Added environment capture covering R, platform, operating system, locale, timezone, and package versions.
- Added canonical project JSON import/export and machine-readable project manifests.
- Added Markdown, HTML, Quarto, CSV, JSON, figure, manifest, and ZIP publication bundles.
- Added Decision Studio analytical handoffs and Knowledge Library methodology/reproducibility packages.
- Added project, publication, handoff, and browser-export schemas and fixtures.
- Added WordPress companion v1.8.0 with project assembly, run index, integrity records, review, publication formats, and platform handoffs.

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
