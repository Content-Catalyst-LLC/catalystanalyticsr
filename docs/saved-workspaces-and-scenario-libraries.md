# Saved Workspaces and Scenario Libraries

Catalyst Analytics R v1.1.0 adds a persistent workspace layer above the v1.0 project contract. A workspace can hold multiple independent `catalyst_project` records while maintaining reusable scenario, parameter-set, and policy-package libraries.

## Workspace lifecycle

1. Create a workspace with `catalyst_workspace()`.
2. Add projects with `workspace_add_project()`.
3. Retrieve or switch the active project with `workspace_get_project()` and `workspace_set_active_project()`.
4. Reuse scenarios and parameter sets through the workspace libraries.
5. Clone a scenario without mutating its source record.
6. Review consolidated run history and project comparisons.
7. Create version snapshots with `workspace_snapshot()` and restore a prior state with `workspace_restore_snapshot()`.
8. Export the complete workspace as JSON, CSV indexes, Markdown, integrity records, and ZIP.

## Reusable libraries

Scenario entries retain the complete canonical scenario and its fingerprint. Parameter sets retain model identity, assumptions, values, and a stable hash. Policy packages reference library identifiers instead of copying hidden state.

## Persistence boundary

The R package persists only when `workspace_to_json()` or `export_workspace()` is called. The WordPress companion is an educational browser mapping and does not provide server-side persistence. Human review, model validation, and publication approval remain separate responsibilities.
