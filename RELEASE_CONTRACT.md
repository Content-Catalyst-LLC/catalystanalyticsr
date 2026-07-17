# Release Contract

## Canonical versions

- Repository release: **0.2.0**
- R package: **0.2.0**
- Canonical scenario schema: **1.0.0**
- KH-NC-PA model: **1.0.0**
- Model manifest schema: **1.0.0**
- Browser input compatibility schema: **1.0.0**
- WordPress demo plugin: **1.1.0**
- Browser export schema: **1.1.0**

The WordPress plugin follows an independent monotonic version line. Compatibility is declared in `catalyst_analytics_r_manifest.json`.

## Required release checks

```bash
python3 -m pip install pytest jsonschema
python3 scripts/check_release.py
```

When R is installed, the release also requires:

```bash
Rscript scripts/check_r_sources.R
R CMD build .
R CMD check --no-manual catalystanalyticsr_0.2.0.tar.gz
```

## Required contracts

A v0.2.0 release is invalid unless:

- The canonical scenario schema and packaged examples validate.
- The KH-NC-PA model manifest validates.
- The browser input and export compatibility records validate.
- Every canonical scenario resolves an exact registered model version.
- JSON round trips preserve scenario fingerprints.
- Legacy R and browser records migrate to schema 1.0.0.
- The numerical reference trajectory passes within its declared tolerance.
- Export bundles preserve scenario and model provenance.
- All exported R functions have documentation aliases.
- No placeholder tests, duplicate functions, non-ASCII R source, malformed JSON, JavaScript syntax errors, PHP syntax errors, generated caches, or version mismatches remain.
