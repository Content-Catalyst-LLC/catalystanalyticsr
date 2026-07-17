# Catalyst Analytics R v1.0.0 Release Contract

## Versions

- Repository and R package: `1.0.0`
- WordPress companion: `2.0.0`
- Project contract: `1.0.0`
- Analytical publication contract: `1.0.0`
- Project handoff contract: `1.0.0`

## Required release gates

1. Every exported R API has an Rd alias and documented arguments.
2. Project records preserve scenarios, datasets, model versions, parameter sets, run hashes, environment, notes, reviews, snapshots, and publication status.
3. Run records preserve stable input and output hashes, warnings, errors, package version, and review status.
4. Publication bundles include project JSON, CSV indexes, Markdown, HTML, Quarto source, platform handoffs, and a file-integrity manifest.
5. Decision Studio and Knowledge Library handoffs preserve explicit human-review and use boundaries.
6. Browser companion v2.0.0 declares `mapped_project_contract_not_r_execution` and never claims R numerical parity.
7. Prior scenario, comparison, uncertainty, data, climate, inclusive-development, calibration, validation, and governance contracts remain valid.
8. `testthat`, `R CMD build`, and `R CMD check --no-manual` must complete without findings before commit or push.

## v1.0.0 repair gate

- Publication manifests must report `file_count` equal to the number of file-integrity records.
- Manifest integrity scope must be `all_bundle_files_except_manifest`; a manifest cannot safely contain its own hash.
- Environment capture must call `utils::capture.output()` explicitly.
- The project-publication regression test must count data-frame rows when `jsonlite` simplifies the file-record array.

## v1.1.0 snapshot fingerprint repair

- A restored workspace must report the fingerprint recorded by its selected snapshot.
- Canonical workspace JSON must not expose restoration-only fingerprint metadata.
- Any semantic workspace mutation must clear restored fingerprint identity.
