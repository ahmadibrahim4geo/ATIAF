# Report 0021 — Consolidated tool UX, output interpretation and native evidence

- Date: 2026-11-15. Plan: [PLAN-0015 r6](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md).
- Status: **IMPLEMENTED DEVELOPMENT BATCH / overall plan PARTIAL, ACTIVE**. Real-acquisition/field/clean-machine acceptance is not replaced by fixtures.
- Git: main; baseline 08954fc1add9b4bdb0b2b5645cebde35cba21235. All prior local changes/history/user PNGs preserved; no commit/push/publication or upstream skills edit.

## Delivered behavior

1. **Native input/manual mapping:** Input Data Folder / مجلد بيانات الإدخال; actual sensor remains separate from opt-in manual mapping. Both adapters expose native optional band-file fields and explicit platform/date/calibration provenance/scale/offset. Only available/required bands are needed: red/NIR NDVI works without blue/header; EVI rejects missing blue. QA absence requires explicit opt-out. Saved JSON import is optional; direct manual runs export reusable Manual_Band_Mapping.json in their unique report folder. Missing metadata is not guessed. Current manual profiles are Landsat C2 L2 and Sentinel-2 L2A; two manual temporal epochs remain gated.
2. **Thematic calculations:** native grouped checkboxes in both hosts, initially unchecked; calculation search removed. QGIS extends its independently installed native Processing panel with groups/conditional fields and RTL. Pro uses native categories/enabled parameters. The old QGIS INDICES enum is hidden for saved-model compatibility; old models need review. Output folder remains last; AOI/mosaic/native CRS/map behavior is shared.
3. **Temperature:** one LST control plus Celsius/Kelvin. Official L2 ST is default. Optional local NDVI-assisted RTE inversion uses existing compatible NDVI or calibrated red/NIR plus calibrated thermal radiance, explicit band Planck constants, atmosphere and emissivity/NDVI thresholds/provenance. The implementation uses an explicit local linear emissivity mixture without cavity term and masks negative NDVI; it is not represented as the full Sobrino TM5 algorithm or validated field accuracy. Missing inputs block before outputs; official ST cannot be remapped as radiance/corrected twice. Scalar atmosphere/grid/date provenance assumptions are documented. No downloads/default atmosphere.
4. **Interpretation/classification:** canonical per-method EN/AR metadata covers all 45 current catalog entries, including legacy/gated variants, and drives regenerated Markdown/HTML, portal cards and scientific reports. Explains meaning, units, conditional/theoretical ranges, contextual NDVI examples and limitations. No universal weak/moderate/strong NDVI standard claimed. Optional local NDVI classes preserve continuous output and save a separate raster, bilingual legend JSON and report with original/effective exact breaks/local justification; negatives/out-of-range/QA are excluded. No field calibration claimed.
5. **Numerical additions:** EVI2 gain 2.5/red coefficient 2.4 (Jiang 2008; corroborated by NOAA ATBD v4.0 Eq.3.6), and unadjusted NIRv (Badgley 2017). Tested with independent expected pixels and native hosts on synthetic inputs. Other candidates remain research, not imported/implemented by label alone.
6. **Distribution/docs:** development 1.0.2.dev0; current self-contained QGIS ZIP under QGIS Tools/Distribution. Core wheel is separate under dist. ZIP includes current adapter/core, icon/license and bilingual HTML help. Old packages remain; intermediate r6 builds archived under Build_History/r6_001 and dist/build-r6_001. Builder refuses overwrite. General tools/ remains developer maintenance, not user GIS algorithms. Updated guides, quick start, scientific/support/source/reference inventories, specifications/decisions and changelog reflect actual work.

## Main files

- Shared: atiaf_core/ui_schema.py, manual_input.py, interpretation.py, classification.py, catalog_additions.py; tool_contract.py, workflow.py, reporting.py, indices/registry.py, raster/workspace.py; new temperature/ndvi_retrieval.py.
- Thin adapters: ArcGIS Pro Tools/atiaf_arcgis.py; QGIS Tools/atiaf/algorithms/common.py and parameters_panel.py. No second core, no remote dependencies.
- tools/build_documentation.py, site template/generated EN/AR catalogs/HTML; new EN/AR MANUAL_BANDS and SURFACE_TEMPERATURE guides; updated current guides/READMEs. Historical discussion notes carry supersession banners rather than deletion.
- Packaging/test defaults and CI, metadata/version, Distribution guide, test_consolidated_changes.py, extended native host/package checks. Source registries distinguish runtime implementation from scientific/real-product validation.

## Exact observed checks

The installed standalone Python is `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe` (3.14.7); NumPy 2.5.3, Rasterio 1.5.2 / GDAL 3.12.2, pyproj 3.8.0, Shapely 2.1.2. Host stacks are independently installed and were not changed.

| Command from ATIAF ROOT | Observed result | Evidence |
|---|---|---|
| `<Python> tools/bootstrap_skills.py` | approved MIT source verified at 2a0a9a23618e40218484ec8ae5848a481df51f1a; actual skill/reference files read | session output; registry |
| `<Python> -m unittest discover tests` | **140 PASS**, including 16 new substantive numeric/raster/provenance/interpretation regressions | [headless.txt](evidence/PLAN-0015/r6/headless.txt) |
| `C:/Program Files/QGIS 4.2.3/bin/python-qgis.bat tests/native_qgis/test_qgis_provider.py` | **11 PASS**: native groups/manual visibility, manual NDVI/EVI2/NIRv/classes, NDVI/RTE temperature, all six workflows, queue and CRS | [native_qgis.txt](evidence/PLAN-0015/r6/native_qgis.txt) |
| `C:/Program Files/ArcGIS/Pro/bin/Python/scripts/propy.bat tests/native_arcgis/test_arcgis_workflow.py` | **8 PASS**: six native parameter/execution paths, Arabic parameter labels, grouped/manual/additional-index/classes and NDVI/RTE output readback | [native_arcgis.txt](evidence/PLAN-0015/r6/native_arcgis.txt) |
| `<Python> tools/build_documentation.py` | offline portal and EN/AR Markdown/HTML generated | observed command output |
| `<Python> tools/validate_package.py` | **PASS**, structural/JSON/local links only | observed output; final closure repeated after report/index update |
| `<Python> tools/build_qgis_plugin.py`; `<Python> -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | current self-contained ZIP and wheel built; earlier artifacts retained | package paths/hashes below |
| `<Python> tools/test_built_packages.py` | wheel/core/adapter/bundled EN/AR help byte identity, isolated wheel install/import **PASS** | [packages.txt](evidence/PLAN-0015/r6/packages.txt) |
| QGIS vendor Python `tests/native_qgis/test_packaged_plugin.py` | relocated plugin, six algorithms, native synthetic NDVI readback **PASS** | [packaged_qgis.txt](evidence/PLAN-0015/r6/packaged_qgis.txt) |
| `node tools/test_documentation.mjs` | desktop 1400×1100 and mobile 390×844 **PASS**, 45 cards, language/search/filter/images/width | [browser.txt](evidence/PLAN-0015/r6/browser.txt) |

Actual Arabic native QGIS parameter panel rendered and inspected: [groups screenshot](evidence/PLAN-0015/r6/qgis_groups_ar.png). The screenshot shows joined Arabic, RTL, actual thematic groups and the manual section hidden before activation. This is not full user click-through acceptance in every host/tool/language.

## Science, licenses, attempts and limits

- RTE is checked with independent forward radiance then inverse retrieval, units and masks; classification checks exact boundaries, exclusions, saved effective settings and untouched continuous pixels. Generated interpretation survives the build. This does not establish field accuracy, a class standard or all mission support.
- Original papers/official technical documents are cited in source/reference registries and bilingual guides; code authored independently under MIT. No catalog, imagery or proprietary/GPL source copied into runtime. No IDB bulk redistribution.
- `git ls-remote` of Awesome Spectral Indices failed (getaddrinfo). No ASI SHA/version pinned/imported; independently reviewed formula definitions avoid pretending installation/import succeeded. Approved skills checkout remains available/verified, unchanged upstream.
- Native QGIS panel initially failed in the test interpreter because Processing plugins path was absent; adding the installed host plugin path to that test environment resolved it. Actual host Processing remains a host dependency, not bundled GPL source.
- Sandboxed separate Chrome could not expose its local test endpoint; the authorized separate-browser run passed. No user's browser or GIS windows were controlled.
- Pro still reports its missing GDAL CF-1 standard-name database. Tested GeoTIFF workflows pass; CF-1 lookups remain untested. No host environment package installation.
- **NOT RUN:** real downloaded L1/L2 acquisitions/field/local ecological calibration; clean-machine install; full interactive Pro dialog/RTL/map acceptance and all-six complete bilingual QGIS journeys; full CRS area/operation accuracy, large-scene/concurrency/crash recovery. AWEI/MTCI/IBI/MIRBI and a complete Sentinel-1 SAR tool remain future/unvalidated work. Temporal manual dual-mapping remains gated.

## Current artifacts and handoff

- QGIS: `QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev0.zip`, SHA-256 `4f4e40556f54c813c52d871722bb708da652a80b2df4d0b608fe65dc2612e4cb`.
- Core: `dist/atiaf-1.0.2.dev0-py3-none-any.whl`, SHA-256 `ecbff9c9d8e6ec12ad3185df2aa8ac00591e2f95aefad17658f04ae74e605b14`.
- Structured bounded observations: [observations.json](evidence/PLAN-0015/r6/observations.json). Fresh r6 DoneProof retains original and added acceptance; partial items are not archived as complete.
- Refresh/restart host applications and reopen dialogs after updating (old Python/plugin caches may hold earlier modules). Install current QGIS ZIP from its native plugin manager; keep repository core beside Pro toolboxes. No live host installation was silently changed.
- Next acceptance: real-product/local calibration and full actual dialog journeys, then remaining scientific variants/product readers with separate reviewed inputs/evidence. Keep PLAN-0015 Active; do not declare a stable release or mark previous gaps completed.

## ملخص عربي

نُفذت دفعة التعديلات: الإدخال اليدوي الأصلي دون JSON إلزامي، مجموعات المؤشرات دون بحث، اختيار LST واحد ووحدته ومسار NDVI المحلي المشروط بمدخلاته، تفسير النتائج باللغتين وتصنيف NDVI المحلي الاختياري، وحزمة توزيع QGIS واضحة. نجح 140 اختبارًا عامًا و11 اختبار QGIS أصليًا و8 اختبارات Pro، وفحص الحزم والموقع. هذه أدلة صناعية وليست تحققًا ميدانيًا أو تثبيتًا نظيفًا. المرشحات العلمية المتبقية وأداة Sentinel-1 الكاملة ليست دعمًا منفذًا؛ الخطة نشطة بقيودها، ولا يوجد نشر أو تعديل لمستودع المهارات الخارجي.
