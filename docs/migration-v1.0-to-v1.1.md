# Migration from v1.0.0 to v1.1.0

v1.1.0 is additive. Existing scenario, project, publication, model, data, accounting, validation, and release-readiness contract versions remain supported.

Projects do not need conversion. Create a workspace and add existing projects:

```r
workspace <- catalyst_workspace("institutional-workspace", "Institutional Workspace")
workspace <- workspace_add_project(workspace, project)
workspace_to_json(workspace, "workspace.json")
```

`workspace_add_project(..., index_contents = TRUE)` copies project scenarios and parameter sets into reusable libraries without changing the original project.

The WordPress companion advances from v2.0.0 to v2.1.0. Its export maps the workspace contract but does not execute R or store the workspace on the WordPress server.
