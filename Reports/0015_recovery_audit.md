# Report 0015 — Recovery audit

- Plan: PLAN-0015 r1, Active. Date: 2026-11-14.
- Baseline: main, 08954fc. No commit created during this audit.
- Preserved user inputs: two root PNGs and four untracked ArcGIS `.pyt.xml` files.
- Reviewed root contract, EN/AR specification and roadmap, decisions, plan/report indexes, report 0014, scientific/resource registries, actual adapters/engines/tests and approved skill files/references.

## Observed checks

All Python commands below use an explicit installed interpreter because the WindowsApps `python` alias cannot start.

| Command | Observed result | Scope |
|---|---|---|
| ArcGIS Python `tools/validate_package.py` | exit 0; 26 candidates, 19 planned sensors, structural PASS | T0 only |
| ArcGIS Python `tools/bootstrap_skills.py` | exit 0; existing approved checkout 2a0a9a23618e40218484ec8ae5848a481df51f1a; 10 mandatory skills present | No download/update or remote script execution |
| ArcGIS Python `development_journal.py verify --project .` | 28 records valid | History integrity |
| Standalone Python `-m unittest discover tests` | 99 tests, OK | T1 fixtures/static |
| QGIS `python-qgis.bat tests/native_qgis/test_qgis_provider.py` | 5 tests, OK | Native provider and synthetic spectral raster execution, not real products/UI |
| ArcGIS Python `-u -c "print('before arcpy',flush=True); import arcpy; print(arcpy.GetInstallInfo(),flush=True)"` | prints before arcpy; process exit -1073741819 | FAILED native import; Pro execution blocked |
| Journal append | first sandboxed attempt WinError 5 on atomic rename; retried with approved escalation, record 0029 created | Gap disclosed, history preserved |

Standalone runtime: Python 3.14.7; NumPy 2.5.3; Rasterio 1.5.2; pyproj 3.8.0; Shapely 2.1.2. No environment package installation.

## Confirmed source defects

- `atiaf_core` is a facade importing implementation in `atyaf_core`; nested aliases do not establish one module identity.
- ArcGIS output folder precedes map checkbox. Thermal/urban exposes no calculation selection. Several sensor selectors are empty or unused.
- Selected CRS is validated but not passed to engines. Several AOI/mosaic options are ignored. Output destination equal to input nests an extra scene directory.
- Catalog imports are inside one all-or-nothing scientific dependency guard; one missing dependency empties the visible selection list.
- Interfaces combine Arabic/English despite the accepted separate-language requirement. QGIS spectral default selects NDVI automatically.
- Old tests largely assert declarations and one synthetic spectral execution; passing them cannot establish six usable tools or release readiness.
- Scientific registry candidates remain unverified while README/state claim broad stable support. Real product T3 and clean-install T4 not independently observed.

## Science, licenses and next action

No scientific formula/data imported. Original code remains MIT; approved skills are read-only MIT guidance. Supplied images inspected and authorized by the user for branding; banner is an illustration, not test evidence. IDB remains reference-only. Implement repairs under PLAN-0015; add behavioral regressions and bilingual operational help. Preserve reports 0001–0014 as historical claims, corrected by this report. Keep native Pro, real product, clean installation and map/RTL GUI checks explicitly unverified until observed.
