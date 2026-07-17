# Model Registry

The model registry separates analytical identity from function names and package release numbers.

## Model identity

A registered model is addressed as `id@version`, for example `khncpa@1.0.0`. Multiple versions can coexist. Omitting the version retrieves the latest registered semantic version.

## Required interface

A model must declare state names, defaults, policy and parameter defaults, units, canonical flow mappings, indicator mappings, numerical methods, callbacks, validators, and metadata.

The shared integrator calls:

```text
derivative(t, state, policy, params)
flows(t, state, policy, params)
build_params(overrides, initial_state)
```

## Canonical flows

Every model maps raw outputs to the canonical flows used by package infrastructure:

- gdp
- consumption
- savings
- education
- abatement
- emissions
- depletion
- damages

Adjusted Net Savings is then calculated consistently from savings, education, depletion, and damages.

## Registration behavior

`register_catalyst_model()` rejects duplicate id/version pairs unless `overwrite = TRUE`. Registration is process-local in v0.2.0; serializable model manifests provide the durable contract record.
