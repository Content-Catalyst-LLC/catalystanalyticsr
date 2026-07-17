# Migration from v1.2.0 to v1.3.0

v1.3.0 is additive across the stable 1.x API.

- Existing scenario, workspace, regional-portfolio, publication, and model-governance contracts remain at version 1.0.0.
- Workspaces may now contain optional `policy_optimizations` and `policy_pathways` libraries.
- Older workspace JSON remains valid; missing new libraries are normalized to empty lists on import.
- New policy optimization, policy pathway, and pathway export contracts begin at version 1.0.0.
- The WordPress companion advances from plugin 2.2.0 to 2.3.0.
- Browser optimization is a contract-mapped educational calculation and not R execution.
