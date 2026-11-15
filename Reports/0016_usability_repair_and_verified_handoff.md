# Report 0016 — Usability repair and verified handoff

- Plan: [PLAN-0015 r1](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md).
- Date: 2026-11-15; work began 2026-11-14.
- Overall status: **PARTIAL — keep plan Active**. Verified implementation and synthetic/native checks are delivered; full GUI, real-product and clean-machine acceptance remain unverified.
- Git: `main`, baseline `08954fc1add9b4bdb0b2b5645cebde35cba21235`; local uncommitted changes. No new commit, push, release or website publication.
- Supersedes the stable/production-ready interpretation of reports 0010–0014; those historical reports and their numbered plans were preserved.

## What changed and why

1. **One real core:** moved the implementation from `atyaf_core/` into `atiaf_core/`, replacing the previous I facade/Y implementation split. All current imports and package discovery use I. The old facade is preserved as a nonexecuted historical text snapshot under `documentation/project/history/`. Old Y imports/CLI commands require migration; no second host-specific engine is implied.
2. **Thin native adapters and visible calculations:** `ArcGIS Pro Tools/atiaf_arcgis.py`, English `ATIAF.pyt`, separate Arabic `ATIAF_AR.pyt`, and `QGIS Tools/atiaf/algorithms/common.py` use the shared tool contract and workflow. Calculation metadata loads without NumPy/Rasterio, so a missing science dependency cannot empty the controls. Every tool has its own explicit, initially unselected choices. Native parameter checks confirm sensor first and output folder last. Pro has individual checkboxes/search; QGIS has its native multiple-selection control.
3. **Actual option routing:** sensor/level mismatch, empty selection and unsafe conditions stop before outputs. QA, available saturation flags, raw DN validity, grid alignment, selected CRS, polygon AOI, compatible same-day mosaic, output destination and explicit expert JSON reach processing. Geographic/foot-based output and unknown source CRS are rejected. Potential automatic double scaling of floating rasters is blocked. Urban analysis now saves the selected derived products. Temporal comparison requires one compatible scene per ordered epoch.
4. **Retained results:** default output no longer nests a scene inside itself. Spectral products use `Results/Spectral_Indices/<category>/<method>/`. Versioned raster names, private temporary writes for continuous and derived rasters, cancellation checks and manifests preserve prior products. Repeated runs recompute; no unverified cache-hit claim. Hotspot zero remains a valid non-hotspot value, with NoData 255.
5. **Reports and science boundaries:** separate `report.en.html` and RTL `report.ar.html` add source-band calibration provenance, requested calculations/CRS and scientific definitions. Product-profile constants are not falsely described as extracted metadata keys. Missing TVDI dry/wet edges, SUHI references, historical baselines, emissivity/variant review and ASTER TIR semantics remain gated. Low-level source presence is not native product support.
6. **Documentation and identity:** renamed docs to `documentation/`; grouped specifications, decisions, roadmaps and starter prompt in `documentation/project/`; updated the root contract and current links. Supplied logo precedes supplied banner in both READMEs, root `index.html` and `documentation/index.html`. Original PNGs remain intact; hashes match integrated copies. Generated EN/AR HTML help explains installation, tool calculations, expert mapping, output folders, science gates and troubleshooting. The portal has 42 searchable/filterable calculation cards.
7. **Packaging and diagnosis:** built a self-contained QGIS ZIP containing the original MIT core, JSON definitions and supplied icon, plus a core wheel. Environment helpers now diagnose without silently installing binary wheels into GIS environments. Diagnostics explicitly distinguish imports/syntax from science/native validation. Version is `1.0.1.dev0`, development status Alpha. Headless dependency constraints and measured runtime evidence are recorded; remote CI is configured but was not run.

## Changed file groups

- `atiaf_core/`: relocated engines; new `tool_contract.py`, `workflow.py`, `execution_context.py`, `reporting.py`, `data/calculations.json`, `raster/safe_io.py`; windowed I/O, workspace, masks/ranges, selected urban outputs and CLI corrections.
- `ArcGIS Pro Tools/`: toolbox entry points, thin adapter, installation guidance and read-only environment helper. Native ArcGIS also generated additional `.pyt.xml` metadata. Original untracked PNG/XML inputs were preserved; no satellite imagery was downloaded or distributed.
- `QGIS Tools/atiaf/`: common adapter, thin algorithm classes, plugin lifecycle/path fixes, icon and development metadata restricted to the tested 4.2 branch.
- `documentation/`, root READMEs/index, scientific/runtime support and resource registries, `AGENTS.md`, `pyproject.toml`, `CHANGELOG.md`.
- `tests/`: migrated imports plus meaningful workflow regressions, native Pro and expanded QGIS checks, isolated package checks. `tools/`: builders, browser/link/package checks and corrected diagnostics. CI configuration updated.
- Numbered report 0015, this report, evidence, active plan/indexes, state and canonical journal.

## Commands and observed results

Executable abbreviations below are exact installed paths, not evidence that the WindowsApps `python` alias works in this execution context:

```powershell
$PY = 'C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe'
$QGIS = 'C:/Program Files/QGIS 4.2.3/bin/python-qgis.bat'
$PRO = 'C:/Program Files/ArcGIS/Pro/bin/Python/scripts/propy.bat'
```

| Exact command | Observed outcome | Evidence / scope |
|---|---|---|
| `& $PY -m unittest discover tests` | exit 0; 124 tests OK | [Final captured output](evidence/PLAN-0015/final_after_layout_and_diagnostics.json); T1 synthetic/static/regression checks |
| `& $QGIS tests/native_qgis/test_qgis_provider.py` | exit 0; 8 tests OK | Same captured output; six algorithms actually execute synthetic scenes; native output CRS/layer readback, selection rejection and event-queued layer registration |
| `& $PRO -u tests/native_arcgis/test_arcgis_workflow.py` | exit 0; 6 tests OK, 5.542 s after imports | [Raw final output](evidence/PLAN-0015/native_arcgis_final.txt); all six tools execute synthetic scenes, native parameter/Arabic labels, actual CRS/readback and rejection paths |
| `& $PY tools/build_qgis_plugin.py` | ZIP built locally, offline | Previous generated builds retained in `dist/build-01` through `build-05`; current named ZIP refreshed |
| `& $PY -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | wheel built locally | No dependency/network installation into GIS environments |
| `& $PY tools/test_built_packages.py` | exit 0; wheel/ZIP core bytes match source; isolated wheel install/import passed | [Captured output](evidence/PLAN-0015/final_after_layout_and_diagnostics.json); temporary target, existing machine dependencies, not clean-machine proof |
| `& $QGIS tests/native_qgis/test_packaged_plugin.py` | exit 0; relocated ZIP core, six algorithms and native synthetic NDVI readback passed | Same captured output; archive works outside repository source location |
| `& $PY tools/build_documentation.py` | offline portal and EN/AR HTML generated | No CDN/network dependency introduced |
| `& 'C:/Program Files/nodejs/node.exe' tools/test_documentation.mjs` | exit 0; desktop/mobile allPass true | [Desktop JSON](evidence/PLAN-0015/portal-desktop.json), [mobile JSON](evidence/PLAN-0015/portal-mobile.json), [desktop screenshot](evidence/PLAN-0015/portal-desktop.png), [mobile screenshot](evidence/PLAN-0015/portal-mobile.png) |
| `& $PY tools/validate_package.py` | structural JSON/link checks passed | Two exact immutable report-0009 old-path links are explicitly resolved as historical migrations; current links use new locations |
| `& $PY tools/verify_installation.py` | exit 0; dependencies/imports/syntax checked | Final output explicitly says native/real-product/clean-install validation is not established by this diagnostic |
| `& $PY .agent_resources/GIS-Development-Skills/scripts/security_audit.py --root .agent_resources/GIS-Development-Skills --archive dist/ATIAF-QGIS-1.0.1.dev0.zip --format text` | exit 0; 35 skills, 0 heuristic findings | Skills/archive preflight only, not a comprehensive application security audit; external scanners NOT RUN |

Measured runtimes: standalone Python 3.14.7, NumPy 2.5.3, Rasterio 1.5.2, Shapely 2.1.2, pyproj 3.8.0, GeoPandas 1.2.0; SciPy absent. QGIS 4.2.3 with Python **3.12.15** and GDAL 3.13.3 corrects older Python 3.12.9 claims. ArcGIS Pro 3.6 build 59527, vendor runtime via propy. See [measured environments](../development_resources/tested_environments.json).

## Failures and corrections observed during this repair

- Initial sandboxed ArcPy import crashed with `-1073741819`; the activated vendor runtime in the authorized execution context imported successfully and later native tests passed. This does not prove every user's environment is configured.
- The first canonical journal append failed on atomic rename with WinError 5. Authorized retry recorded step 0029; the chain then verified. No old canonical record was rewritten.
- Initial regressions exposed old expectations of mixed-language labels and old document paths. Updated tests assert separate locales and explicitly documented historical migrations.
- Initial browser execution in the restricted process context failed. Authorized headless execution then exposed a test-page relative asset path error and test-proof text affecting screenshots. Those harness errors were corrected. Final device emulation measures actual 1400/390 widths, not merely requested screenshot dimensions.
- A final diagnostic still described imported indices as validated. That residual misleading text was corrected and regression checked. [Earlier captured output](evidence/PLAN-0015/final_checks.json) is retained; [corrected output](evidence/PLAN-0015/final_after_layout_and_diagnostics.json) supersedes it.
- ArcGIS emitted a GDAL CF-1 standard-name database warning. Tested GeoTIFF operations passed; CF-1 lookup functionality is unverified.

## Science, licenses and security scope

No new scientific algorithm or bulk external catalog was imported. Existing candidate registries remain unverified proposals; [runtime support](../scientific_library/runtime_support.json) separately records exposed/gated methods and individually observed native synthetic calculations. No complete IDB data, proprietary code, credentials or imagery was added. New original code remains MIT. User-supplied branding is used under the explicit project request, with [asset provenance](../documentation/assets/manifest.json). The banner is an illustration, not output evidence.

Approved guidance was explicitly read from `.agent_resources/GIS-Development-Skills` at SHA `2a0a9a23618e40218484ec8ae5848a481df51f1a`: journal, DoneProof, GIS router, remote sensing, ArcGIS toolbox, QGIS plugin, Arabic i18n, CRS, processing, data-flow diagnostics, security and visual assets, with relevant references. Existing bootstrap/source/remote/MIT checks passed. No upstream skills repository was modified or bulk plugins installed.

Native APIs were checked against primary documentation: [Esri Python toolbox parameters](https://doc.esri.com/en/arcgis-pro/latest/arcpy/geoprocessing_and_python/defining-parameters-in-a-python-toolbox.html), [Esri Parameter properties](https://doc.esri.com/en/arcgis-pro/latest/arcpy/classes/parameter.html), [QGIS enumeration parameters](https://api.qgis.org/api/classQgsProcessingParameterEnum.html) and [Chrome device metrics](https://chromedevtools.github.io/devtools-protocol/tot/Emulation/). These references guide API use; execution evidence is the actual checks above.

## Acceptance and remaining work

| Criterion | Status | Practical boundary |
|---|---|---|
| C1: one canonical I implementation and thin host adapters | VERIFIED | Source and wheel/ZIP identity; old Y imports require migration |
| C2: complete visible native order/calculation/language interaction | PARTIAL | Native parameter loading and execution passed; full GUI click-through/RTL visual acceptance incomplete; QGIS standard enum does not grey each incompatible row |
| C3: real option routing, scientific preflight and preserved outputs | PARTIAL | Verified synthetic/native routes, rejection, reprojection, clipping, masks, reruns, cancellation and expert mapping; real products, full CRS suitability/operation provenance, all large-scene limits and full concurrency/recovery remain unverified |
| C4: organized bilingual documentation and discoverable moved references | VERIFIED | Offline portal/help and current links; historical links explicitly mapped; original specifications/history preserved |
| C5: supplied logo before banner, intact local assets | VERIFIED | Matching hashes, actual browser decoding/order, desktop/mobile visual readback |
| C6: honest claims, tests, report/index/state/journal handoff | VERIFIED | Corrected development status and explicit unrun acceptance; final closure checks in canonical journal and plan-bound proof |

**NOT RUN:** real downloaded L1/L2 product acceptance, clean-machine GIS installation, remote CI, external SAST/vulnerability scanners and complete native GUI/map-render acceptance. Physical Escape stopped live Computer Use; subsequent browser checks used an isolated headless test process and did not control the user's windows. QGIS native event-loop layer registration was checked; visual rendering is distinct.

Temporal comparison is currently one scene per epoch; incompatible/cross-date mosaics are gated. Cache reuse is not claimed. Some analyses remain array-based with a size guard. Full projected CRS area-of-use and exact datum-operation provenance/accuracy, concurrent cumulative-index writing and comprehensive crash/resume need additional work. Existing models using removed parameter names need reconfiguration. Close/refresh old dialogs and restart a host if cached imports retain an old version.

## Handoff

Keep PLAN-0015 in Active. Start the next acceptance batch from this report and the canonical state/journal: inspect the native EN/AR dialogs and actual user click path; then use legally held local real L1/L2 products, independently check calibration/QA/CRS/NoData/statistics, test a clean GIS installation and concurrency/interruption recovery. Record each new batch in the next unique report; do not call the roadmap or release complete from the current evidence.

Local packages: `dist/ATIAF-QGIS-1.0.1.dev0.zip` (SHA-256 `c7d4baa3238a02b6ec42c7b36814773a3bb46d8a5a2e6f420068ef6d4fb028c5`) and `dist/atiaf-1.0.1.dev0-py3-none-any.whl` (`c0837a41ecbbf9d7e9f3ce4249a19bf1374914b1f772fdb6f797ea937f7219c0`). They are local development artifacts, not published releases.

## ملخص عربي

وُحّد المحرك باسم `atiaf_core`، وصُححت خيارات الأدوات الست وترتيبها ومسارات الحفظ وربط المسقط والقص والجودة والحسابات بالتنفيذ الفعلي. أصبح التوثيق داخل `documentation` والمواصفات داخل `project`، مع اللوجو فوق البانر في README وصفحات البداية. نجح 124 اختبارًا و8 اختبارات QGIS و6 اختبارات ArcGIS Pro على بيانات صناعية، وفُحصت الحزم والبوابة محليًا. **هذه ليست شهادة اعتماد لكل مرئية حقيقية أو إصدارًا مستقرًا**؛ الخطة تظل نشطة إلى حين إكمال قبول الواجهة والمنتجات الحقيقية والتثبيت النظيف والاختبارات المتبقية.
