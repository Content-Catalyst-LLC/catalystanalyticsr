# Release Contract

## Canonical versions

- Repository release: **0.1.4**
- R package: **0.1.4**
- WordPress demo plugin: **1.0.1**
- Browser export schema: **1.0.0**
- KH-NC-PA model contract: **0.1.4**

The WordPress plugin uses an independent, monotonic version line. Compatibility is declared in `catalyst_analytics_r_manifest.json` rather than inferred from matching version strings.

## Required release checks

```bash
python3 -m pip install pytest jsonschema
python3 scripts/check_release.py
```

When R is installed, the release also requires:

```bash
R CMD build .
R CMD check --no-manual catalystanalyticsr_0.1.4.tar.gz
```

A release is invalid if placeholder tests, duplicate exported functions, stale export fields, malformed JSON, JavaScript syntax errors, PHP syntax errors, or version mismatches are present.

The built source package must exclude `.github`, `.pytest_cache`, repository-only integration directories, and local check artifacts through `.Rbuildignore`. All files under `R/` must use ASCII characters.
