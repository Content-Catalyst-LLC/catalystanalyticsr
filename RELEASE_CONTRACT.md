# Release Contract

## Canonical versions

- Repository and R package: **0.8.0**
- WordPress companion: **1.7.0**
- Wealth contract: **1.0.0**
- Human-development contract: **1.0.0**
- Distribution contract: **1.0.0**
- Composite-score contract: **1.0.0**
- Inclusive-development contract: **1.0.0**
- Browser inclusive-development export: **1.7.0**

All prior scenario, comparison, uncertainty, data, indicator, emissions, climate, natural-capital, and boundary contracts remain valid.

## Required release checks

```bash
python3 scripts/check_release.py
Rscript scripts/check_r_sources.R
R CMD build .
R CMD check --no-manual catalystanalyticsr_0.8.0.tar.gz
```

## Capital-account contract

- Opening and closing stocks are finite and non-negative.
- Investment, depreciation, depletion, and damages are non-negative.
- Revaluation is signed and explicit.
- Closing stocks reconcile to the stock-and-flow identity within tolerance.
- Shadow prices are positive and remain visible.

## Inclusive-wealth contract

- Produced, human, and natural accounts have aligned entity-time rows.
- Inclusive wealth is the sum of the three declared capital values.
- Per-capita wealth requires positive population.
- Capital shares and price basis remain visible.

## Development and distribution contract

- Adjusted Net Savings exposes every addition and deduction.
- Human-development goalposts and dimension indices remain visible.
- Distribution weights, groups, social floor, inequality measures, and group shares remain inspectable.
- Intergenerational analysis preserves time, population, per-capita wealth, discounting, and target assumptions.

## Composite-score contract

- Components, directions, weights, normalization bounds, and missing-data policy are explicit.
- Weights are normalized to one.
- Component values, normalized scores, and weighted contributions remain traceable.
- Weight sensitivity is reported before interpretation.

## Browser boundary

The WordPress companion performs deterministic educational calculations mapped to the v0.8.0 concepts. It does not execute R or verify data, capital valuations, shadow prices, social floors, survey weights, discount rates, or composite-score legitimacy.

## v0.8.0 release gate

The release must preserve calibration parameters, fitted observations, holdout metrics, residual diagnostics, solver benchmarks, stability and boundary evidence, known limitations, intended and prohibited uses, lifecycle state, reviewers, approvals, and transition history. Validated status requires both calibration and validation evidence.

## Serialization and numerical extraction repair gate

- Every model-validation export is passed through the recursive JSON sanitizer.
- Nested custom S3 records must serialize without defining ad hoc `asJSON` methods.
- Solver and stability comparisons extract named numeric scalars explicitly.
- Dates and timestamps are emitted as portable ISO-formatted strings.

## Calibration-target and version-expectation repair gate

- All export tests expect package version `0.8.0`.
- Calibration targets are validated before optimizer execution.
- Only existing `parameters.*`, `policy.*`, and `initial_state.*` fields are accepted.
- Unsupported or unregistered calibration targets fail with `Unsupported calibration target`.
