# Uncertainty, Sensitivity, and Stress Testing

Catalyst Analytics R v0.4.0 treats uncertainty as a governed scenario contract rather than a chart decoration.

## Supported uncertainty targets

- `parameters.<name>`
- `policy.<name>`
- `initial_state.<name>`
- `constraints.<name>`

## Sampling

`sample_uncertainty()` supports reproducible Monte Carlo and Latin hypercube designs. The supported distributions are fixed, uniform, normal, lognormal, triangular, beta, and discrete. Every ensemble records the seed, sample count, failed realizations, exact specifications, and package version.

## Analysis

`run_uncertainty()` produces terminal indicator ensembles, P2.5/P10/P50/P90/P97.5 intervals, threshold-crossing probabilities, and rank-correlation global sensitivity. `local_sensitivity()` provides central finite-difference effects and elasticities.

## Stress testing

`stress_shock()` and `stress_case()` define explicit set, add, or multiply changes to scenario targets. `run_stress_tests()` compares each named case against the governed baseline using the v0.3.0 comparative engine.

## Interpretation boundary

Probabilities describe the declared model and distributions. They are not empirical forecast probabilities unless the assumptions, calibration, and evidence support that interpretation. Failed or unstable runs must remain visible.
