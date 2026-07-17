# Comparative Scenario Engine

## Purpose

The v0.3.0 comparative engine evaluates multiple governed scenarios without collapsing their identities, roles, assumptions, model versions, or provenance.

## Execution contract

`run_scenarios()` accepts canonical scenarios and returns a `catalyst_scenario_set` containing:

- Canonical scenario records
- Named `catalyst_run` results
- Scenario roles and model versions
- Scenario fingerprints
- Completion status
- Structured execution errors

By default, phase-plane and local-sensitivity calculations are disabled for batch runs so comparative execution remains focused and efficient.

## Baseline selection

`compare_scenarios()` selects the baseline using this order:

1. The explicit `baseline` argument
2. The single completed scenario whose role is `baseline`
3. The first completed scenario when no baseline role exists

Multiple baseline roles require explicit selection.

## Metrics and direction

Only indicators available in every completed run may be compared. Each metric must have one consistent direction:

- `higher_better`
- `lower_better`
- `contextual`

Deltas are always calculated as:

```text
scenario terminal value - baseline terminal value
```

The direction determines whether that delta is classified as improved or worsened.

## Targets and thresholds

Targets and thresholds may be supplied as named numeric values or explicit rule records:

```r
targets = list(ans = 0)
thresholds = list(emissions = list(value = 0.25, operator = "<="))
```

When no operator is given, higher-better metrics use `>=` and lower-better metrics use `<=`.

## Rankings

Scenarios receive a per-metric rank. Lower values rank first for lower-better metrics; higher values rank first for higher-better metrics. Ties use the minimum shared rank.

## Trade-offs

Each non-baseline scenario is classified as:

- `dominates_baseline`
- `dominated_by_baseline`
- `tradeoff`
- `equivalent_or_contextual`

The table preserves the specific improved, worsened, and tied metrics rather than reducing the comparison to one opaque score.

## Pareto diagnostics

The engine orients every metric so larger values represent preferable outcomes, then calculates pairwise dominance and iterative Pareto layers.

A scenario is non-dominated when no other scenario is at least as good on every selected metric and strictly better on at least one.

Pareto status is descriptive, not a recommendation. Stakeholders must still decide how to value competing outcomes.

## Export contract

`export_scenario_comparison()` writes:

- Scenario index
- Canonical scenario JSON records
- Per-scenario trajectories
- Terminal values
- Baseline deltas
- Rankings
- Scorecard
- Targets and thresholds
- Trade-off classifications
- Pareto front and dominance relationships
- Comparison plots
- Comparison JSON
- Checksummed manifest

The comparison export schema is `1.0.0`.
