# Catalyst Analytics R v1.5.0 Release Contract

The release is valid only when:

- `DESCRIPTION`, the repository manifest, public API manifest, and WordPress compatibility record identify repository version 1.5.0.
- WordPress companion version 2.5.0 maps to repository 1.5.0.
- API request, response, public manifest, platform handoff, handoff export, and browser export schemas validate.
- All six first-party target products are represented.
- Every handoff requires human review and forbids autonomous publication or decision authorization.
- Existing analytical contracts remain valid.
- R source is ASCII-portable, exported functions are documented, JavaScript and PHP parse, repository tests pass, and archives are intact.
- `R CMD check --no-manual` reports no errors, warnings, or notes before commit and push.
