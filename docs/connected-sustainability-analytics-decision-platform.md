# Connected Sustainability Analytics and Decision Platform

Catalyst Analytics R v2.0.0 introduces a governed analytical graph that connects the package's previously separate contracts without erasing their boundaries.

## Connected records

The platform indexes workspaces, projects, scenarios, datasets, models, indicators, evidence, decisions, governance workflows, publications, platform handoffs, and analytical workflows as versioned nodes. Directed edges preserve containment, derivation, evidence, governance, publication, and handoff relationships.

## Federated registries

Model and indicator registries remain governed by their existing contracts. The connected platform adds an evidence registry and makes all three registries discoverable through the v2 API manifest.

## Lineage

`platform_lineage()` traverses upstream, downstream, or bidirectional relationships and returns the exact nodes and edges used in the traversal. The result supports review, audit, publication provenance, and Decision Studio handoffs.

## Decision and publication boundary

A connected record can show which evidence supports a decision or publication. It cannot authorize the decision, verify organizational identity, publish an artifact, or execute a cross-product action. Those controls remain the responsibility of the host platform and human approvers.

## Compatibility

The v2.0.0 platform consumes the stable v1 scenario, project, workspace, handoff, governance, and publication contracts. The `/v1` API remains available; `/v2` adds connected-platform discovery, validation, summary, registry, and lineage operations.
