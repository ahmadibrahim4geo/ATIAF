# 0026 — Geological Color Composites inspection and integration

- Date: 2026-11-15. Plan: PLAN-0018 r1; **INSPECTED / ACTIVE, runtime not yet implemented**.
- Authorization: execute supplied source plan using the existing ATIAF tool pattern. Baseline `main` at `1d15bad`; earlier local instruction changes preserved.

## Findings before runtime edits

`atiaf_core/geology/engine.py` and registry compute individual ratios. `workflow.py` has common discovery, preflight, run context, workspace/manifests and adapters for six existing tools. Native `.pyt` subclasses and QGIS algorithms delegate to this shared workflow. `raster/windowed.py` currently writes a single channel, so RGB needs a focused multichannel writer. Existing ASTER discovery lacks exact SWIR B6–B9 assets and fully validated calibration; do not claim those from generic SWIR roles. No reviewed complete composites/preview/preset path found in these files.

## Integration and acceptance

Add `geological_composites` as a seventh independent native tool in the existing toolbox/provider, with Direct RGB and Ratio RGB as separate initially unchecked choices. Add shared exact-band registry, restricted arithmetic parser, windowed Float32 RGB writer, QA/NoData and reference-grid handling, separate reproducible display settings/exports, temporary before/after preview and JSON preset save/import. Reuse common sensor discovery, output-last fields, polygon AOI, projected metre CRS, preservation and reports. Exact band mapping/calibration is explicit for multiband/custom input and ASTER where automatic parsing is insufficient.

Files planned: `atiaf_core/composites/`, workflow/schema/catalog integration, Pro tool classes/adapter and QGIS algorithm/provider/panel, targeted tests/native checks, EN/AR help, packaging/help source identity and registries/support notes. No additional runtime dependency intended: NumPy, Rasterio/PROJ and existing host APIs; optional preview PNG can use the already present image writer. No code copied from GPL hosts or proprietary APIs. Original code remains MIT.

All original plan criteria retained. Testing will distinguish independent formula fixtures, synthetic scene/readback, real native host execution, GUI render/journeys and real-product/clean-install evidence. User explicitly reports no local real scenes. Scientific/field/real-product validation remains NOT RUN; no hidden imagery downloads. Full native journeys/clean install must not be inferred from headless success.

## Observed commands and research

Read `AGENTS.md`, current state/indexes/report 0025 and source plan; inspected the exact files named above with `Get-Content` / `rg`; checked `git status --short` (preserved previous edits). `python tools/bootstrap_skills.py --verify` verified MIT skills SHA `2a0a9a23618e40218484ec8ae5848a481df51f1a`; Journal verify passed 48 records before request #0049. Copied source with `Copy-Item` to the numbered Active working plan; original retained.

Reviewed primary [Duwi study](https://www.nature.com/articles/s41598-024-66199-3), [NASA/JPL ASTER advisory](https://asterweb.jpl.nasa.gov/swir-alert.asp), and [QGIS RGB renderer API](https://api.qgis.org/api/classQgsMultiBandColorRenderer.html). Verify exact formulas in the study before registry approval; NASA advisory supports blocking SWIR from April 2008 and noting earlier saturation periods. QGIS API retrieved is master, so installed runtime tests must adjudicate compatibility. First Esri renderer URL was unavailable; consult reachable versioned official documentation. References are scientific/API sources, not runtime downloads or redistributed images.

Tests at this stage: code inspection / skills and Journal integrity only. GIS host: none yet; numerical/native tests NOT RUN. Next: validate formula/renderer sources, implement smallest full vertical slice, run and preserve real command evidence, then report current support honestly. Keep PLAN-0018 Active.

## بالعربية

المطلوب أداة مستقلة داخل نمط أطياف الحالي بطريقتي RGB المباشر ونسب الباندات، دون تصنيف. الموجود نسب منفردة وبنية مشتركة يمكن إعادة استخدامها؛ الناقص تجميع القنوات والمعاينة وسجل التركيبات وتحسين العرض المستقل. يلزم تحقق صريح لباندات ASTER ومعايرتها. لا تتوافر مرئيات حقيقية وفق رد المستخدم، ولن تُعد الاختبارات الصناعية بديلًا عنها.
