# Catalyst Analytics R

Catalyst Analytics R is the reproducible analytics layer for the Sustainable Catalyst platform. It provides an R package for sustainable-development scenario modeling, indicator computation, carbon-budget review, adjusted-net-savings style reasoning, plots, and export bundles.

The repository also includes a WordPress demo plugin so the public Catalyst Analytics R page can show a browser-based exploratory scenario tool without requiring a server-side R runtime.

## What this repository supports

- Scenario simulation with R package functions.
- Adjusted Net Savings style indicator logic.
- Carbon-budget comparison.
- SDG-style indicator summaries.
- Plotting and export bundles.
- Browser-based WordPress demo: `[catalyst_analytics_r_demo]`.
- JSON export schema for shareable scenario records.
- Documentation for methodology, reproducibility, and review.

## Repository structure

```text
R/                                  R package functions
man/                                R package documentation
tests/testthat/                     R package tests
wordpress/catalyst-analytics-r-demo WordPress shortcode demo plugin
docs/                               Methodology and implementation docs
schemas/                            JSON schema for exported demo records
inst/extdata/                       Packaged sample scenario inputs
examples/                           Example scenario records
outputs/                            Example outputs
python/                             Lightweight brief generator
.github/workflows/                  CI checks
```

## WordPress demo

Install the plugin from `wordpress/catalyst-analytics-r-demo` or upload the generated zip from `dist/catalyst-analytics-r-demo.zip`.

Use this shortcode on the Catalyst Analytics R page:

```text
[catalyst_analytics_r_demo]
```

The demo lets visitors adjust a simplified sustainable-development scenario and review:

- Produced capital trajectory
- Human capital trajectory
- Natural capital trajectory
- Cumulative emissions
- Adjusted-savings style estimate
- Emissions budget status
- Composite scenario score
- JSON export

The browser demo is educational and exploratory. It uses a simplified browser engine with conceptual—not numerical—parity to the R package. It is not a forecast, compliance tool, or substitute for professional analysis.

## Release versions

- Repository and R package: **0.1.4**
- WordPress demo plugin: **1.0.1**
- Browser export schema: **1.0.0**

See `RELEASE_CONTRACT.md` and `docs/releases/v0.1.4.md`.

## R package quickstart

```r
# From package root
# install.packages(c("ggplot2", "jsonlite", "testthat", "devtools"))

devtools::load_all()

run <- catalyst_demo()

run
summary(run)

plot(run)
plot(run, which = "sdg_dashboard")
plot(run, which = "phase_plane")
plot(run, which = "sensitivity_heatmap")

catalyst_glossary()

catalyst_export(
  run,
  dir = "demo_out",
  run_id = "video_demo",
  zip = FALSE,
  overwrite = TRUE
)
```

## Methodology

Catalyst Analytics R follows the Sustainable Catalyst methodology:

```text
question → assumptions → scenario → model → indicators → output → interpretation → review
```

The goal is not to produce certainty. The goal is to make assumptions visible, calculations reproducible, outputs exportable, and interpretation reviewable.

## Boundaries

Catalyst Analytics R is an educational, open-source, decision-support package. It does not provide legal, financial, investment, engineering, environmental, compliance, scientific, or professional advice. Outputs depend on data quality, assumptions, model design, and interpretation.

## License

MIT. See `LICENSE`.
