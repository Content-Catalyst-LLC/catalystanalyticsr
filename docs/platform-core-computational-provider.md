# Platform Core Computational Provider

Catalyst Analytics R 2.2.0 is a Workspace-hosted R provider for Platform Core 3.1+. Core owns provider registration, analytical request semantics, result bindings, provenance references, and research-object integration. Workspace executes the R runtime. Analytics R supplies the analytical methods and provider-side contract.

## Flow

`Core request -> Workspace execution envelope -> Workspace R runtime -> Catalyst Analytics R -> Core result envelope -> Core provenance/evidence/visualization bindings`

The package never turns Platform Core into an R executor, and it does not provide a standalone network transport.
