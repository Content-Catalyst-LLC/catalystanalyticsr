# Canonical Scenario Contract

The canonical scenario is the portable analytical input record for Catalyst Analytics R.

## Identity and model resolution

Every scenario declares a stable lowercase `id`, a human-readable `title`, a role, and an exact `{model id, model version}` pair. Execution fails when that model version is not registered.

## Time

The contract stores start, end, optional regular step, unit, and the complete ordered time vector. The values are authoritative; start, end, and step are consistency checks.

## Analytical inputs

- `initial_state`: values required by the model state contract
- `policy`: static policy controls
- `parameters`: model parameter overrides
- `constraints`: analytical boundaries such as an emissions budget

Function-valued R policies remain available to lower-level package calls, but canonical scenarios intentionally require serializable static values.

## Context and provenance

Units, geography, sectors, currency, sources, assumptions, uncertainty records, review status, and metadata travel with the scenario. Empty collections are represented as arrays; empty parameter and constraint maps are represented as JSON objects.

## Fingerprints

`scenario_fingerprint()` hashes compact canonical JSON. The fingerprint changes when any governed scenario field changes, including assumptions and review metadata.

## Migrations

`migrate_catalyst_scenario()` supports legacy R schema `0.1.0` and the browser input contract. Unsupported schema versions fail explicitly rather than being guessed.
