# Catalyst Analytics R

Catalyst Analytics R is the reproducible statistical, scenario-modeling, uncertainty-analysis, sustainability-accounting, model-governance, and analytical-publication engine for the Sustainable Catalyst platform.

**Current release:** `1.0.0`  
**WordPress companion:** `1.8.0`  
**Shortcode:** `[catalyst_analytics_r_demo]`

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
R CMD check --no-manual catalystanalyticsr_1.0.0.tar.gz
```

## Boundary

A reproducible project can show exactly what was run, with which inputs, model, software environment, assumptions, warnings, interpretation, and review record. Reproducibility does not by itself establish external validity, causal identification, regulatory compliance, professional fitness, or approval for a decision.


## v1.0 stable production contract

Use `catalyst_api_manifest()` to inspect stable APIs, `catalyst_compatibility_manifest()` for contract support, and `catalyst_release_readiness()` to create a reviewable production gate record. See `docs/production-readiness.md`.
