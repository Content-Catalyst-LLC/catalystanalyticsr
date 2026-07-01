# Contributing

Catalyst Analytics R is part of the Sustainable Catalyst open-source platform. Contributions should preserve the repository's core standards: clear assumptions, reproducible workflows, traceable outputs, and human-readable documentation.

## Good contributions

- Improve R package tests.
- Add clear example scenarios.
- Improve documentation.
- Add validation checks.
- Improve export structures.
- Fix accessibility or browser compatibility issues in the WordPress demo.
- Clarify assumptions and interpretation boundaries.

## Contribution standards

- Do not present model outputs as forecasts or guarantees.
- Keep assumptions visible.
- Preserve reproducibility.
- Avoid hidden dependencies where possible.
- Document new functions and workflows.
- Add or update tests when behavior changes.

## Local validation

```bash
Rscript -e 'devtools::test()'
python3 -m pytest tests_py
```

If R dependencies are unavailable, run the lightweight Python validation tests.
