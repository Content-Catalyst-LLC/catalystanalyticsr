# Data Intake and Indicator Registry

## Analytical path

```text
source -> records -> schema -> quality -> units -> indicator definition -> calculation -> trace -> review
```

## Data intake

Use `read_catalyst_data()` for local CSV or JSON files or `as_catalyst_dataset()` for an existing data frame. Declare the time field, entity keys, required fields, units, source, geographic scope, sector scope, and currency basis.

The quality report records missing cells, duplicate rows, duplicate entity/time keys, global time order, and inferred regularity. These checks establish structural readiness only. They do not prove source accuracy or comparability.

## Indicator definitions

Use `new_catalyst_indicator()` to define the indicator id and version, readable formula, required input fields, output unit, preferred direction, aggregation behavior, methodology references, optional targets, and calculation callback.

Built-in examples include carbon intensity, GDP and emissions per capita, cumulative emissions, adjusted net savings, and natural-capital change.

## Traceability

`calculate_indicator()` records:

- indicator id and version
- formula and required fields
- output unit and direction
- dataset id and fingerprint
- source and unit declarations
- calculation timestamp and package version
- grouping and missing-value behavior
- input and output row counts

## Export

`export_data_analysis()` writes the original records, dataset manifest, source record, quality flags, transformation history, indicator definitions, values, traces, checksums, and analysis manifest.
