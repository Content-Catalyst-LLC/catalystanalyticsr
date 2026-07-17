# Repository Architecture

Catalyst Analytics R has three governed layers.

## 1. Contract layer

- Canonical scenario schema and R object
- Model definitions and registry
- Model manifests
- Scenario migrations and browser mappings
- Numerical and compatibility fixtures

## 2. R analytical layer

- Registered-model simulation with RK4 or Euler integration
- Adjusted Net Savings
- Carbon-budget checks
- Indicator summaries
- Phase-plane and local sensitivity tools for KH-NC-PA
- Plots and portable export bundles

## 3. WordPress demo layer

The public plugin runs a lightweight JavaScript model. It now emits the same canonical scenario structure but does not execute the R equations.

## Separation boundary

`mapped_contract` means the browser and R layers share scenario structure, control meaning, model identity, units, and provenance fields. It does not mean their trajectories are numerically identical.
