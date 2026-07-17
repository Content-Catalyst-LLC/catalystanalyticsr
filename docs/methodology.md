# Catalyst Analytics R Methodology

Catalyst Analytics R exists to make sustainable-development analytics more reproducible and reviewable.

## Operating flow

```text
question → assumptions → scenario → model → indicators → output → interpretation → review
```

## Core principles

1. **Assumptions must be visible.** Scenario controls, parameters, and initial conditions should be explicit.
2. **Methods must be reproducible.** Outputs should be generated from code, not hand-edited.
3. **Indicators need interpretation boundaries.** Indicators simplify reality and should not be treated as automatic truth.
4. **Uncertainty should be named.** Scenario outputs depend on model structure and input choices.
5. **Human judgment remains responsible.** Tools support review; they do not replace it.

## Model boundaries

The R package and browser demo are educational and decision-support oriented. They do not certify compliance, forecast outcomes, or provide professional advice.

## Climate and natural-capital accounting - v0.6.0

Gross emissions and removals are represented separately; net emissions are their arithmetic difference. Period-total observations are accumulated by summation. Rate observations are integrated with the trapezoidal rule against ordered numeric or date-like time values.

Kaya decomposition uses the identity:

`emissions = population * (GDP / population) * (energy / GDP) * (emissions / energy)`

Additive LMDI contributions use the logarithmic mean of baseline and comparison emissions. The contribution sum is tested against the observed emissions change and the residual remains visible.

Natural-capital accounting uses:

`closing = opening + regeneration + restoration + additions - extraction - degradation - damages`

When an observed closing stock is provided, the difference from the accounting identity is retained as a reconciliation error.

## Inclusive wealth and distribution - v0.7.0

Produced, human, and natural capital use a common stock-and-flow identity. Declared shadow prices convert stocks into a common analytical value basis. Inclusive wealth is reported in total and per-capita terms.

Adjusted Net Savings adds education and health investment to gross savings and deducts produced-capital depreciation, resource depletion, pollution damages, and climate damages.

Distributional analysis reports weighted quantiles, Gini, Palma, top-10 and bottom-40 shares, group summaries, and social-floor exposure. Composite scores expose their weights, directions, bounds, normalized components, and sensitivity to alternative weights.
