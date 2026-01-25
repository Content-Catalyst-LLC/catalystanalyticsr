# Catalyst Analytics R

A sustainable-development analytics engine (R package) for the Catalyst suite.

**What it does (v0.1):**
- Simulates a simple calculus-based dynamical system (vector ODE) via RK4 or Euler
- Computes Adjusted Net Savings (ANS)
- Integrates emissions against a carbon budget
- Produces ggplot2 graphs
- Exports CSV bundles + a JSON manifest for cross-product ingestion


## Quickstart (dev)

```r
# From the package root:
# install.packages(c("ggplot2","jsonlite","testthat","devtools"))
devtools::load_all()

# One-call demo (dummy data, stable outputs)
run <- catalyst_demo()

# Friendly summary (prints automatically)
run
summary(run)

# Show plots
plot(run)                       # default: trajectory
plot(run, which = "sdg_dashboard")
plot(run, which = "phase_plane")
plot(run, which = "sensitivity_heatmap")

# See variable meanings + units
catalyst_glossary()

# Export a bundle (CSVs + PNGs + manifest.json)
catalyst_export(run, dir = "demo_out", run_id = "video_demo", zip = FALSE, overwrite = TRUE)

# (Raw export option) export just a simulation result:
times <- seq(0, 20, by = 1)
x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
raw <- simulate_dynamics(times, x0, return_long = TRUE)
export_catalyst_bundle(raw, dir = "demo_out", run_id = "raw_only", zip = FALSE, overwrite = TRUE)
```

## Video demo runbook
See `inst/demo/demo_video_runbook.R` for a 2-3 minute script you can copy/paste.

## License
MIT
