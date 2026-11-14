# Contributing to ATIAF
Thanks for contributing. The project is MIT-licensed. Use GitHub Issues for bug reports, sensor product examples, scientific index corrections, translations and feature proposals.

1. Check `AGENTS.md`, `PROJECT_STATE.md`, `PROJECT_SPECIFICATION.md` and recent numbered reports.
2. Open an Issue describing reproducible input conditions, expected output, actual output, sensor/product/version and allowed-to-share sample (do not upload private scene data or credentials).
3. For a new index: provide **original scientific citation/DOI**, unique internal ID, alternate acronym if reused elsewhere, formula, unit, wavelength/band roles, required product level, constants, compatibility rules and small independent reference test.
4. Keep calculations pure and tested separately from ArcPy and QGIS; inspect all NoData, scaling, QA, georeferencing and target CRS.
5. Follow bilingual localization: add matching Arabic/English tooltips, help, documentation and errors. Do not embed Arabic labels inside English UI.
6. Preserve original products and existing results; test interrupted/resumed runs.
7. Open a PR with test command/output, evidence tier, license review, doc updates and screenshots of native UI if relevant. `completion-evidence` applies.
8. Do not bulk redistribute Index DataBase records or relicense third-party code. Verify specific dependencies.

See [Arabic contribution guide](CONTRIBUTING_AR.md).
