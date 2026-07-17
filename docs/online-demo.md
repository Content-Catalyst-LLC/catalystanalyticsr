# Online Comparative Demo

The WordPress plugin exposes the shortcode:

```text
[catalyst_analytics_r_demo]
```

## v1.3.0 behavior

The demo now performs a real baseline-versus-policy comparison using simplified browser-side equations. Users can edit shared starting conditions and budget assumptions, then configure separate baseline and intervention policy controls.

The interface provides:

- Two independently named scenarios
- Shared horizon, initial conditions, and emissions budget
- Overlaid metric trajectories
- Terminal baseline and policy values
- Absolute and percentage deltas
- Direction-aware improved, worsened, or tied status
- Trade-off classification
- Simplified two-scenario non-dominance status
- Comparison notes
- JSON download and copyable summary

## Export mapping

The browser export includes:

- Browser comparison input
- Two canonical scenario records using scenario schema 1.0.0
- Comparison deltas
- Trade-off classification
- Simplified Pareto status
- Budget status for both scenarios
- Both trajectories
- Interpretation boundaries

The browser export schema is 1.3.0 and declares compatibility with repository version 0.4.0.

## Numerical boundary

The browser equations are not the R KH-NC-PA implementation. The relationship is `mapped_comparison_contract`, not numerical parity. Use the browser tool for public explanation and preliminary exploration. Use the R package for reproducible model execution, rankings, target and threshold evaluation, and full Pareto diagnostics.
