# Catalyst Analytics R

Catalyst Analytics R is the reproducible statistical, scenario-modeling, uncertainty-analysis, sustainability-accounting, model-governance, and analytical-publication engine for the Sustainable Catalyst platform.

**Current release:** `1.4.0`  
**WordPress companion:** `2.4.0`  
**Shortcode:** `[catalyst_analytics_r_demo]`


## Public API and platform handoffs

Version 1.6.0 adds collaborative institutional review and governance while retaining the transport-neutral `/v1` API manifest, governed request and response envelopes, in-process dispatch for validation and discovery, and first-party handoffs to Site Intelligence, Research Lab, Workbench, Catalyst Canvas, Decision Studio, and Knowledge Library. The host platform remains responsible for HTTP transport, authentication, authorization, rate limiting, and durable operations. The new governance layer records analyst, reviewer, approver, and publisher roles; structured comments; change requests; approvals; signed analytical releases; restricted access; audit history; retention; and archival controls.

## v1.4.0 econometrics and policy evaluation

- Governed regression specifications with classical, HC1, and clustered uncertainty
- Unit, time, and two-way fixed-effects panel analysis
- Difference-in-differences and dynamic event studies
- Interrupted time-series and synthetic-control workflows
- Explicit causal assumptions, diagnostics, policy-effect summaries, and publication bundles
- WordPress companion v2.4.0 with explicit causal and non-R execution boundaries

## v1.3.0 optimization and policy pathway design

- Constrained single- and multi-objective optimization
- Grid and reproducible random-search candidate generation
- Feasible-policy regions, target-seeking scenarios, and Pareto frontiers
- Cost-effectiveness and marginal-abatement analysis
- Staged adaptive pathways, decision gates, and evidence triggers
- Robustness and normalized regret across futures
- Portable optimization and pathway publication bundles
- WordPress companion v2.3.0 with an explicit non-authoritative browser boundary

## v1.2.0 regional, sector, and portfolio analytics

- Governed geography and sector scope records
- Multi-region and multi-sector portfolio members
- Weighted indicator aggregation and regional ranking
- Regional carbon-budget allocation and overshoot diagnostics
- Sector output, emissions, and intensity transition pathways
- Reusable workspace portfolio libraries and portable export bundles


## v1.1.0 saved workspaces and scenario libraries

Catalyst Analytics R now provides a persistent workspace layer for multiple projects and reusable analytical records.

```r
workspace <- catalyst_workspace("transition-workspace", "Transition Workspace")
workspace <- workspace_add_project(workspace, project)
workspace <- workspace_clone_scenario(
  workspace, "baseline", "transition-copy",
  new_scenario_id = "transition-copy", role = "intervention"
)
workspace <- workspace_snapshot(workspace, "review-candidate")
export_workspace(workspace, "outputs")
```

- Multiple governed projects in one workspace
- Active-project selection
- Reusable scenario and parameter libraries
- Policy packages with validated references
- Consolidated run history and project comparison
- Workspace snapshots and restoration
- Complete JSON and ZIP workspace portability

## v1.0.0 reproducible projects and analytical publication

The package now preserves a complete analytical project rather than only individual model exports. A `catalyst_project` can contain canonical scenarios, governed datasets, model manifests, parameter sets, run records, result summaries, input and output hashes, software environments, indicators, plots, interpretation notes, review decisions, snapshots, and publication history.

```r
project <- catalyst_project(
  "transition-evidence",
  "Transition Evidence Project",
  description = "Compare a baseline and transition pathway.",
  owner = "Sustainable Catalyst"
)

project <- project_add_scenario(project, scenario)
project <- project_add_run(project, run, "baseline-run", scenario_ids = scenario$id)
project <- project_add_note(project, "interpretation-1", "Results remain conditional on the declared model.")
project <- project_snapshot(project, "publication-candidate")

export_project_publication(project, "outputs")
```

## v1.0.0 capabilities

- Governed analytical project structure
- Stable project, scenario, dataset, parameter-set, input, and output hashes
- Run history with warnings, errors, environment, and review status
- Software, R, operating-system, locale, timezone, and dependency capture
- Interpretation notes and human review records
- Immutable project snapshots
- JSON, CSV, Markdown, HTML, Quarto, and ZIP publication outputs
- Registered PNG, SVG, PDF, and other figure artifacts
- Decision Studio analytical handoffs
- Knowledge Library methodology and reproducibility handoffs
- Browser project-publication companion with explicit non-R parity boundary

## Existing analytical foundation

- Canonical scenarios and model registry
- Comparative scenario engine
- Monte Carlo, Latin hypercube, sensitivity, and stress testing
- Governed data intake and indicator registry
- Climate, carbon, natural-capital, inclusive-wealth, human-development, and distribution accounting
- Calibration, historical and holdout validation, solver benchmarks, stability tests, and model governance

## Repository layout

```text
R/                                  Analytical and project implementation
man/                                R documentation
inst/extdata/                       Governed fixtures
schemas/                            Machine-readable contracts
examples/                           Example inputs
outputs/                            Example exports
wordpress/catalyst-analytics-r-demo WordPress browser companion
tests/ and tests_py/                R and repository contracts
scripts/                            Release validation
```

## Validation

```bash
python3 scripts/check_release.py
Rscript scripts/check_r_sources.R
R CMD build .
R CMD check --no-manual catalystanalyticsr_1.4.0.tar.gz
```

## Boundary

A reproducible project can show exactly what was run, with which inputs, model, software environment, assumptions, warnings, interpretation, and review record. Reproducibility does not by itself establish external validity, causal identification, regulatory compliance, professional fitness, or approval for a decision.


## v1.0 stable production contract

Use `catalyst_api_manifest()` to inspect stable APIs, `catalyst_compatibility_manifest()` for contract support, and `catalyst_release_readiness()` to create a reviewable production gate record. See `docs/production-readiness.md`.

## Econometrics and Policy Evaluation (v1.4.0)

Build governed regressions, panel models, difference-in-differences, event studies, interrupted time series, and synthetic controls. Estimates retain robust or clustered uncertainty, diagnostics, explicit causal assumptions, review status, and portable publication evidence.
