# Release Contract

## Canonical versions

- Repository release: **0.6.0**
- R package: **0.6.0**
- Emissions-inventory contract: **1.0.0**
- Climate-accounting contract: **1.0.0**
- Natural-capital contract: **1.0.0**
- Sustainability-boundary contract: **1.0.0**
- Dataset contract: **1.0.0**
- Indicator registry contract: **1.0.0**
- Data-analysis export: **1.0.0**
- Canonical scenario schema: **1.0.0**
- Comparative scenario schema: **1.0.0**
- Uncertainty schema: **1.0.0**
- Stress-test schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- WordPress demo plugin: **1.5.0**
- Browser climate export: **1.5.0**

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
R CMD check --no-manual catalystanalyticsr_0.6.0.tar.gz
```

## Emissions-inventory contract

A v0.6.0 release is invalid unless:

- Gross emissions and removals are finite and non-negative.
- Net emissions reconcile to gross emissions less removals.
- Entity and time fields retain their documented dataset source.
- Emissions units, accounting basis, GWP basis, source categories, gas categories, and boundaries remain visible.
- Optional population, GDP, and energy fields are positive before Kaya decomposition.
- Inventory manifests preserve dataset fingerprints and source records.

## Carbon-accounting contract

- Period-total pathways use cumulative sums; rate-based pathways use trapezoidal integration.
- Carbon budgets are finite, non-negative, and explicit for every accounting group.
- Every pathway records cumulative gross emissions, cumulative removals, cumulative net emissions, remaining budget, budget share, and status.
- Overshoot, recovery, target-year values, post-target positive emissions, lock-in share, and stranded-pathway signals remain inspectable.
- Kaya identity levels reconstruct gross emissions within numerical tolerance.
- Additive LMDI contributions reconcile to the observed emissions change within numerical tolerance.

## Natural-capital contract

- Opening and closing stocks are finite and non-negative.
- Regeneration, restoration, additions, extraction, degradation, and damages are finite and non-negative.
- Expected closing stock equals opening stock plus additions less losses.
- Observed closing stocks expose a reconciliation error.
- Production validation rejects accounts outside the declared tolerance.

## Sustainability-boundary contract

- Boundaries declare an indicator, unit, direction, bound, warning margin, source, and status.
- At-or-below, at-or-above, and inside-range definitions validate their required limits.
- Assessment detects breaches, warning margins, missing values, and unit mismatches.
- Boundary status is an analytical signal, not a compliance determination.

## Browser boundary

- The WordPress demo performs real deterministic pathway, Kaya, natural-capital, and boundary calculations.
- Browser exports declare repository compatibility and every climate contract version.
- Browser outputs state that source review, budget allocation, GWP basis, and natural-capital valuation remain unresolved.
- The browser does not claim R-runtime numerical parity, scientific validation, compliance, or autonomous decision authority.

## Repository integrity

- All JSON fixtures validate against their schemas.
- All exported R functions have documentation aliases and documented arguments.
- R source is ASCII portable and lexically balanced.
- JavaScript and PHP syntax checks pass.
- No placeholder tests, caches, `.Rcheck` directories, generated package archives, or version mismatches remain.
