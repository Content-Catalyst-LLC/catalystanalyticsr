# Migrating from v1.4.0 to v1.5.0

v1.5.0 is additive for the public R API and existing analytical contracts.

- Existing scenarios, projects, workspaces, econometric analyses, and publication bundles remain supported.
- Workspaces gain an optional `platform_handoffs` library. Older workspace JSON is normalized to an empty library on import.
- Decision Studio and Knowledge Library handoffs retain their previous top-level fields and add the shared platform-handoff fields: `target`, `payload`, `provenance`, `review`, `boundary`, and `package_version`.
- Host applications may use the new API request and response envelopes without embedding an HTTP transport in the R package.
