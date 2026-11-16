# 0028 — Legacy imagery and geological outputs inspection

- Date: 2026-11-15; PLAN-0019 r1; **INSPECTED / ACTIVE**. Baseline `main` at `1d15bad` with prior authorized uncommitted work preserved.
- Source moved from root `ATYAF_Legacy_Imagery_and_Geological_Outputs_Audit_Plan.md` to `Development_Plans/Active/PLAN-0019_Legacy_Imagery_and_Geological_Outputs_Audit.md`. Pristine reference-only snapshot in `Development_Plans/Source_Archive/SOURCE-0019_ATYAF_Legacy_Imagery_and_Geological_Outputs_Audit_Plan.md`. Both SHA256: `3A00DBDEECEF2412DD2789FF0132D9C567F5250E29942C17D9A9233BE17721F3` before intake notes.

## Findings before computational changes

Seven actual native tools/catalogs found, not an invented historical support list. `LandsatParser.parse()` returns UNKNOWN/zero bands for the supplied legacy L1T bundle; shared `discover()` fails. The separate composites legacy parser does identify/calibrate it, so that behavior is not yet shared with the other tools. Existing C2-oriented parser does not distinguish product generations robustly, has no MTL XML support and cannot establish archived C1 support. The Landsat7 SLC-off test compares year/month separately, which misses January–April in later years. Sentinel2 currently reads one BOA offset and assumes the default quantification scale; per-band/L1C/baseline metadata needs regression fixtures before correction.

The **exact** screenshot-referenced `...dad2439d6ee5_DISPLAY.tif` and its analytical TIFF/metadata/preview/overview were located under the previous standalone test results, not inferred from the screenshot. Read-only inspection confirms UInt8 RGB display and recorded CRC1 channels `B6/B7`, `B6/B2`, `(B4/B5)*(B6/B5)`. Numeric statistics/color attribution still require independent measurement; no recipe change is justified from appearance alone. The existing source is Duwi 2024; compare the 2022 paper without silently replacing attribution or channel order.

## Authorized work and outputs

1. Supersede copy-and-leave-root intake policy with relocation into numbered plan folders, source path/title/SHA preservation and optional reference-only source archive. No root duplicate remains. An earlier PLAN-0018 root original was already absent at session start; this agent did not remove it.
2. Audit the actual tools/product-generation/method paths and make minimal shared reader/calibration/QA fixes proven by independent fixtures; retain explicit scientific eligibility gates for unsupported methods. No forced downloads or automatic atmospheric correction.
3. Measure the actual CRC1 analytic/display layers, source/MTL, geography/NoData, full/sampled statistics and independently selected pixel arithmetic; explain cyan using measured channels/stretch and explicitly labeled diagnostic land-cover masks, without claiming mineral classes. Compare display stretch methods without modifying analytical values.
4. Make outputs/scene identity/recipe names/provenance understandable and maintain EN/AR help and real native parity. Deliver the six named audit documents under `Reports/PLAN-0019_Audit/`, evidence, a new sequential delivery report, indexes/state/Journal and all original acceptance.

Real data currently available: the 2014 pre-Collection Landsat8 bundle and its prior results. Same-acquisition C2, archived C1, real Landsat9/TM/ETM+/MSS/ASTER/Sentinel2 and independently mapped rocky reference scenes are **NOT SUPPLIED**. Build synthetic product-generation/band/QA regression fixtures and mark real matrix cells NOT_TESTED, not PASS. No clean installation or field accuracy inference.

## Observed commands and limits

`git status --short`, full root contract/current state/active indexes/latest report and supplied plan read; local skills and Journal verified (**51** records; skills SHA `2a0a9a23618e40218484ec8ae5848a481df51f1a`). `Copy-Item` created the internal pristine snapshot and checked-path `Move-Item` relocated only the supplied file. `Get-FileHash` confirmed equal hashes. `python -m unittest discover -s tests -v`: **162 baseline PASS**, [log](evidence/PLAN-0019/baseline_headless.txt). Read-only inspection saved [baseline inventory](evidence/PLAN-0019/baseline_inventory.json). No GIS execution or new raster result claimed at inspection stage. Native hosts remain independently installed Pro/QGIS; relevant fresh checks will follow fixes.

Primary sources reviewed: [USGS historical/product IDs](https://www.usgs.gov/faqs/how-can-i-tell-difference-between-landsat-collections-data-and-landsat-data-i-have-downloaded), [Duwi 2024](https://www.nature.com/articles/s41598-024-66199-3), [2022 candidate comparison](https://www.mdpi.com/2075-163X/12/12/1577). First scaling FAQ fetch failed; obtain official alternate/reference before applying C1 coefficients. Science/API sources are references, not runtime dependencies or permission to redistribute study images.

## بالعربية

نُقلت الخطة إلى مجلد الخطط برقم 0019 وحُفظ أصل مطابق داخل أرشيف المصادر فقط. الملف المرجعي نفسه موجود وفُحصت بياناته: صورة عرض RGB وليست وحدها المنتج التحليلي. ثبت أن قارئ المشهد القديم منفصل داخل أداة التراكيب ولا تعمل به بقية الأدوات المشتركة، وظهرت نقاط تستحق اختبارات في أجيال Landsat وإزاحات Sentinel-2. لن يتغير ترتيب CRC1 أو تفسير ألوانه قبل القياس ومراجعة المرجع، ولن تسجل العينات غير المتاحة بوصفها ناجحة.
