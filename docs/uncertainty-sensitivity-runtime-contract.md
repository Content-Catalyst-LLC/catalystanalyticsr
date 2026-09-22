# Uncertainty & Sensitivity Runtime Contract

Catalyst Analytics R v2.3.0 introduces `sc.analytics-r.uncertainty-sensitivity-runtime.v1`.

The runtime is bounded and Workspace-managed. It supports canonical Catalyst scenario execution using Monte Carlo sampling, Latin hypercube sampling, Morris elementary-effects screening, and Sobol first-order/total-order sensitivity estimation. It does not accept arbitrary R functions or dynamic function names from remote callers.

## Execution boundary

Platform Core defines analytical meaning and provenance. Workspace authenticates, budgets, executes, and persists jobs. Catalyst Analytics R performs only registered numerical methods. Uncertainty estimates are evidence, not truth claims. Sensitivity estimates do not establish causality, scientific validity, or policy preference. Human interpretation remains required.

## Structured methods

- Monte Carlo and Latin hypercube use the existing governed uncertainty specifications and ensemble runner.
- Morris reports `mu`, `mu_star`, and `sigma` elementary-effect summaries by target and metric.
- Sobol reports first-order and total-order estimates using Saltelli-style first-order and Jansen total-order estimators.
- Evaluation budgets are explicit and bounded before structured execution begins.

## Integration

The provider remains compatible with `sc.core.analytical-runtime-provider.v1`, retains the statistical diagnostics contract from v2.2.0, and targets Platform Core v3.4.0 for first-class uncertainty/probabilistic evidence ingestion. Workspace v3.9.1 is the validated host baseline; production promotion from provider 2.2.0 to 2.3.0 requires the next Workspace adapter promotion.
