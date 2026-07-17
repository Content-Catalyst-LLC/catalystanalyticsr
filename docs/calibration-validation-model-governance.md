# Calibration, Validation, and Model Governance

Catalyst Analytics R v0.8.0 separates four questions that are often incorrectly collapsed into one:

1. Can declared parameters be estimated within defensible bounds?
2. Does the calibrated model reproduce historical and reserved holdout evidence?
3. Are numerical results stable across solver choices, perturbations, invariants, and boundary conditions?
4. Has a qualified reviewer approved a clearly limited use of the model?

A good fit does not automatically approve a model. The governance contract preserves intended uses, prohibited uses, evidence, assumptions, parameter cards, limitations, reviewers, approvals, and every lifecycle transition.

## Calibration contract

`calibration_spec()` declares each estimated target, initial value, bounds, transformation, unit, objective, optimizer, and stopping controls. `calibrate_model()` preserves the estimates, fitted observations, objective value, optimizer convergence, evaluation history, and calibrated scenario.

## Validation contract

`validation_split()` creates calibration and holdout partitions. `validate_model_fit()` reports RMSE, MAE, MAPE, sMAPE, bias, R-squared, residual diagnostics, acceptance thresholds, and individual pass/fail checks.

## Numerical evidence

`solver_benchmark()` compares RK4 and Euler integrations across declared time steps. `stability_assessment()` tests small initial-state perturbations, finite/non-negative state invariants, strictly increasing time, and controlled boundary cases.

## Governance lifecycle

The supported lifecycle states are:

- `experimental`
- `under_review`
- `validated_for_specified_use`
- `deprecated`
- `archived`

Validated status requires both calibration and validation evidence. It is always bounded by the model card's intended uses, prohibited uses, assumptions, known limitations, approval scope, and reviewer record.
