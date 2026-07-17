# Climate, Carbon, and Natural-Capital Accounting

## Analytical sequence

1. Validate a source dataset.
2. Normalize gross emissions, removals, net emissions, gas categories, source categories, units, time, and entities.
3. Declare whether observations are period totals or rates.
4. Declare the GWP or CO2-equivalent basis.
5. Apply an explicit carbon budget to each accounting group.
6. Calculate cumulative emissions and budget status.
7. Inspect target-year, lock-in, and stranded-pathway signals.
8. Decompose gross-emissions change with the Kaya identity when population, GDP, and energy are available.
9. Reconcile natural-capital opening and closing stocks with documented additions and losses.
10. Evaluate declared sustainability boundaries.
11. Export the complete accounting record for human review.

## Accounting boundary

A technically correct calculation does not make the declared boundary scientifically or institutionally appropriate. Organizational scope, geographic scope, gas coverage, Scope 1/2/3 treatment, land-use treatment, GWP basis, time horizon, carbon-budget allocation, and natural-capital measurement method must be reviewed outside the numeric engine.

## Carbon budget interpretation

A carbon budget in Catalyst Analytics R is a declared analytical constraint. The package does not select a global budget, translate temperature goals, allocate a global budget to an organization or region, or determine legal compliance.

## Natural-capital interpretation

Natural-capital stocks and flows may be physical, indexed, or monetary, but units cannot be mixed without a documented transformation. The default examples use synthetic indices and should not be treated as valuations.

## Boundary status

- `within`: outside the warning margin and on the admissible side.
- `warning`: on the admissible side but within the declared warning margin.
- `breached`: outside the declared boundary.
- `unit_mismatch`: observed and declared units differ.
- `unknown`: no finite matching value was available.
