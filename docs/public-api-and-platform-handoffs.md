# Public API and Sustainable Catalyst Handoffs

Catalyst Analytics R v1.5.0 introduces a versioned, transport-neutral public API contract and first-party handoffs for the Sustainable Catalyst platform.

## API boundary

The package defines request and response envelopes, endpoint discovery, schema versions, and in-process dispatch. It does not run an HTTP server, store credentials, implement rate limiting, or grant platform permissions. Those controls belong to the host application.

## Supported endpoint families

- Health and contract discovery
- Model and indicator registry discovery
- Scenario validation and execution
- Project and workspace manifests
- Platform handoff construction

## First-party handoffs

- **Site Intelligence:** approved data snapshots, sources, licenses, scopes, and requested indicators
- **Research Lab:** calibration, uncertainty, batch-simulation, and benchmark compute jobs
- **Workbench:** formulas, calculators, parameter sets, units, and indicators
- **Catalyst Canvas:** objectives, stakeholders, assumptions, constraints, and evidence gaps
- **Decision Studio:** alternatives, analytical evidence, uncertainty, interpretations, and reviews
- **Knowledge Library:** methodology, data sources, assumptions, reproducibility, citations, and review records

Every handoff is a review artifact. Receiving products must validate the contract, preserve provenance, surface limitations, and require a human decision before publication or action.
