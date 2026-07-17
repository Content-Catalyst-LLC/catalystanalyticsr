# Online Data and Indicator Demo

The WordPress plugin exposes the shortcode:

```text
[catalyst_analytics_r_demo]
```

## v1.4.0 behavior

The public interface now demonstrates the v0.5.0 data-intake and indicator contracts. Users can paste tidy CSV records, declare source and license metadata, validate required fields and entity/time keys, select a registered indicator, inspect the definition and trace, and export the governed browser record.

The interface provides:

- CSV parsing with required-field checks
- Missing-value, duplicate-row, and duplicate-key diagnostics
- Dataset, source, license, currency, time, and entity metadata
- Versioned built-in indicator definitions
- Rowwise and grouped indicator calculations
- Indicator formula, unit, direction, and required-field display
- Result chart and table
- Calculation trace and canonical JSON export

## Export mapping

The browser export includes:

- Browser-engine and repository compatibility metadata
- Dataset contract version 1.0.0
- Indicator contract version 1.0.0
- Source and license records
- Quality summary and flags
- Selected indicator definition
- Calculated values and trace metadata
- Interpretation boundaries

The browser export schema is 1.4.0 and declares compatibility with repository version 0.5.0.

## Analytical boundary

The browser tool validates and calculates a limited public indicator registry. It does not execute arbitrary R functions, import remote data, or replace the R package's governed dataset, registry, export, and review workflows. Use the browser interface for explanation and preliminary inspection; use the R package for reproducible analysis and publication bundles.
