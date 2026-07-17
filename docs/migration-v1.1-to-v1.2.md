# Migration from v1.1.0 to v1.2.0

v1.2.0 is additive across the stable 1.x API.

- Existing scenarios, projects, and workspaces remain valid.
- Workspace libraries may now include an optional `regional_portfolios` collection.
- Existing workspace JSON files without that collection are normalized to an empty list during import.
- New regional portfolio contracts use schema version 1.0.0.
- WordPress companion compatibility advances from plugin 2.1.0 to 2.2.0.
