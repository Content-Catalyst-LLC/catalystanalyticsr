# Migration from v1.3.0 to v1.4.0

v1.4.0 is additive. Existing scenarios, workspaces, policy optimizations, and pathways remain valid.

New workspaces include a nullable `policy_evaluations` library. Older workspace JSON records are normalized to an empty library during import.

Use `regression_spec()` and `fit_policy_regression()` for governed associations. Use design-specific functions for causal evaluation, and record assumptions with `causal_assumption()`.
