# Statistical Diagnostics & Validation Contract

Catalyst Analytics R v2.2.0 adds a machine-readable evidence contract for model diagnostics, statistical assumptions, robustness checks, model comparisons, and validation evidence.

## Boundary

The contract records statistical evidence. It does **not** automatically declare a study scientifically valid, convert a p-value into a truth claim, select a preferred model, authorize a policy decision, or replace human methodological review.

The provider remains Workspace-hosted and implements `sc.core.analytical-runtime-provider.v1`. Diagnostic bundles are designed for Platform Core v3.2.0 analytical result/provenance ingestion.
