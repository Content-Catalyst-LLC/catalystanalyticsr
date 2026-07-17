# Production Readiness and Stable API

Catalyst Analytics R v1.0.0 establishes the first stable production contract.

## Stability

Functions listed by `catalyst_api_manifest()` are stable for the 1.x series. Additive optional fields may be introduced in minor releases. Breaking argument, return, or schema changes require a major release or an explicit versioned migration.

## Release gates

A production release requires clean package checks, versioned schemas, documented migrations, model limitations, complete provenance, human-review boundaries, accessibility review, browser/R boundary disclosure, and security/privacy review. `catalyst_release_readiness()` records these gates but never authorizes release autonomously.

## Accessibility and browser review

The WordPress companion uses semantic headings, labeled controls, keyboard-operable buttons, visible focus states, live status regions, and text equivalents for status. It remains an educational browser companion and does not execute the R package.

## Security and privacy

The package performs local computation and file export. Projects may contain sensitive data; users must review data minimization, storage, retention, and publication scope before sharing bundles. No credential or secret should be embedded in project records.

## Compatibility

Scenario, model, comparison, uncertainty, dataset, accounting, governance, project, publication, and release-readiness contracts are versioned independently. The compatibility manifest documents supported inputs and WordPress mapping.
