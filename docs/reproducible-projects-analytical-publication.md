# Reproducible Projects and Analytical Publication

Catalyst Analytics R v0.9.0 introduces a governed analytical project as the durable container for work that must remain reproducible, reviewable, portable, and publishable.

## Project contract

A project records:

- project identity, question, owner, scope, and tags;
- canonical scenarios and governed datasets;
- exact model manifests and parameter sets;
- analytical run records with input and output hashes;
- software environment and dependency versions;
- indicator artifacts and registered figures;
- interpretation notes and human review decisions;
- immutable snapshots and publication history.

## Publication formats

`export_project_publication()` can create JSON, CSV indexes, Markdown, standalone HTML, Quarto source, copied figure artifacts, file-integrity manifests, and a ZIP bundle. Quarto source is produced without requiring Quarto to be installed or executed.

## Platform handoffs

The Decision Studio handoff preserves alternatives, result summaries, uncertainty and warning boundaries, interpretation, and review records. The Knowledge Library handoff preserves models, datasets, sources, assumptions, parameter sets, hashes, environment, methodology, interpretation, and publication boundaries.

## Review boundary

Reproducibility is evidence about the analytical process. It is not evidence that a model is externally valid, causally identified, compliant, appropriate for a specific decision, or professionally approved.
