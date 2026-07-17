# Catalyst Analytics R

Catalyst Analytics R is the reproducible statistical, scenario-modeling, uncertainty-analysis, and sustainability-accounting engine for the Sustainable Catalyst platform.

**Current release:** `0.7.0`  
**WordPress companion:** `1.6.0`  
**Shortcode:** `[catalyst_analytics_r_demo]`

## v0.7.0 capabilities

- Produced-, human-, and natural-capital stock-and-flow accounts
- Declared shadow prices and reconciliation errors
- Inclusive wealth and per-capita wealth
- Adjusted Net Savings decomposition
- Human-development dimension indices
- Weighted distribution and social-floor diagnostics
- Intergenerational wealth comparison
- Transparent composite scores and weight sensitivity
- Reproducible JSON, CSV, Markdown, manifest, and ZIP exports

## Existing analytical foundation

- Canonical scenarios and model registry
- Comparative scenario engine
- Monte Carlo, Latin hypercube, sensitivity, and stress testing
- Governed CSV/JSON intake and indicator registry
- Emissions inventories, carbon budgets, Kaya decomposition, natural-capital accounts, and sustainability boundaries

## Example

```r
produced <- capital_account("produced", 500, investment = 55, depreciation = 20, closing_stock = 535)
human <- capital_account("human", 400, investment = 36, depreciation = 12, closing_stock = 424, shadow_price = 1.2)
natural <- capital_account("natural", 300, investment = 12, depletion = 8, damages = 6, closing_stock = 298, shadow_price = 1.5)

wealth <- inclusive_wealth_account(produced, human, natural, population = 5)
ans <- adjusted_net_savings_decomposition(80, 20, 22, 14, 8, 5, 6, gni = 1000)
hdi <- human_development_indicators(72, 13, 9, 16000)
```

## Repository layout

```text
R/                                  Analytical implementation
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
R CMD check --no-manual catalystanalyticsr_0.7.0.tar.gz
```

## Boundary

Capital stocks, shadow prices, human-capital measurement, goalposts, social floors, distribution weights, intergenerational discount rates, and composite weights require explicit human review. Outputs are exploratory decision support, not forecasts, compliance determinations, autonomous decisions, or professional advice.
