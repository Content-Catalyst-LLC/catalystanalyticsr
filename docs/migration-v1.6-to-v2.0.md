# Migration from v1.6.0 to v2.0.0

v2.0.0 is additive for stable analytical records. Existing projects and workspaces remain valid at contract version 1.0.0 and can be indexed with `platform_add_project()` or `platform_add_workspace()`.

1. Create a platform with `connected_sustainability_platform()`.
2. Add existing workspaces and projects.
3. Register evidence, model, and indicator records.
4. Add decision, publication, governance, handoff, and workflow records as needed.
5. Validate the graph and inspect lineage.
6. Export a connected-platform bundle for institutional review.

The browser companion version advances to 3.0.0. It maps the connected contract but does not execute R or provide durable storage.
