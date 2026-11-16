# PLAN-0019 r1 — 01 Sensor/product/method compatibility

2026-11-16. **Partial product validation**, not universal sensor certification. The inventory script observes seven native tool IDs and 47 catalog method entries (including compatibility aliases), not 47 independently validated algorithms. [893-cell CSV](../evidence/PLAN-0019/inventory/method_product_matrix.csv) and [JSON with actual catalog and scene metadata](../evidence/PLAN-0019/inventory/method_product_matrix.json) enumerate every tool × method × inspected profile. Reproduce with `python tools/inventory_product_eligibility.py Reports/evidence/PLAN-0019/inventory_new`.

`ELIGIBLE_BY_METHOD_GATE` means only the method's band/level gate accepted the inspected metadata with diagnostic TOA allowed. It does **not** mean QA, CRS, ancillary inputs, second temporal date, raster processing or scientific accuracy passed. `INELIGIBLE` includes the exact reason. Real missing acquisitions have `NOT_TESTED` and no synthetic substitution. Fixtures establish calibration/roles/rejection, not real historical sensor performance.

| Product/profile | Implemented reader/gate behavior | Evidence / real limitation |
|---|---|---|
| L8 pre-Collection L1T, 2014 | Old Scene ID, acquisition/date/path/row/station/version; MTL TOA coefficients; distinct BQA | Supplied real scene: both RGB methods in QGIS EN / Pro AR; diagnostic NDVI in QGIS AR / Pro EN, independent readback |
| Same acquisition C2 reprocessing | Modern Product ID supported; acquisition date is not processing date | Counterpart NOT SUPPLIED; no equivalence to reprocessed SR claimed |
| L8 C1 L1 | Metadata collection/level; per-band TOA calibration; C1 BQA decoder | Synthetic only; not pre-Collection BQA |
| L8 C1 SR | DN × 0.0001, offset 0, fill -9999; pixel_qa | Synthetic MTL and explicit ESPA, including matching companion MTL; real NOT_TESTED |
| L8 C2 L1 | MTL TOA, not C2 SR scaling | Synthetic only |
| L8/L9 C2 L2 | SR × 0.0000275 − 0.2; actual official ST_B10 separately × 0.00341802 + 149 K | C2 synthetic native regressions; real L9/C2 not supplied |
| L7 ETM+ before/after 2003-05-31 | Physical SWIR1 B5; SLC-off date comparison corrected, no gap filling | Synthetic pre/post and later January dates; real NOT_TESTED |
| L5 TM 1990s / L4 TM | Red B3, NIR B4, SWIR1 B5, SWIR2 B7; thermal B6 never reused as SWIR | Synthetic metadata/roles only; no automatic radiance→SR/ESUN reconstruction |
| MSS1–3 / MSS4–5 | Optical numbering B4–B7 / B1–B4 respectively; no SWIR/thermal | Synthetic mapping; no general MSS SR implementation or geology/TIR eligibility |
| S2 L1C PB03/PB04+ | Quantification and per-band RADIO_ADD_OFFSET; modern missing calibration rejected; explicit TOA option | Synthetic L1C namespace/offset tests; no real SAFE |
| S2 L2A PB03/PB04+ | BOA quantification and per-band BOA_ADD_OFFSET, processing baseline controls offsets | Synthetic only; no real SAFE or mixed-resolution field accuracy |
| ASTER before April 2008 | Existing exact-band manual calibrated stack/date gate; proposed presets experimental | Automatic exact SWIR reader incomplete; real NOT_TESTED |
| ASTER April 2008 onward | SWIR compositions rejected; no thermal inference from optical availability | Synthetic gate only; real NOT_TESTED |
| Agricultural/coastal mixed scene | Available 2014 scene has spectral proxy groups and spatial preview | Diagnostic proxies; no ground-truth land-cover labels |
| Independently mapped rocky reference | Required for interpretation validation | NOT SUPPLIED / NOT_TESTED |
| Mixed parent / missing band | Incompatible generations/dates cannot silently mosaic; missing required band rejects before writes | Fixture tests, no generalized multi-acquisition harmonization |

Actual tool paths: `atiaf_core/workflow.py` routes T01 indices, T02 temperature, T03 thermal/urban, T04 environmental/drought, T05 geological ratios, T06 temporal and T07 composites. Native adapters are `ArcGIS Pro Tools/atiaf_arcgis.py` / the two `.pyt` files and `QGIS Tools/atiaf/algorithms/`. Shared readers: `discovery/landsat_profiles.py`, `landsat.py`, `sentinel2.py`; gates: `workflow.unavailable_reason` and `composites.engine.validate_request`. Output cardinality/rejection and original preservation have fixture/native evidence; ancillary-dependent TVDI, VCI/TCI/VHI, SUHI, unreviewed emissivity and sensor-specific coefficients remain gated.

Observation classes: the screenshot suggests colors only; code establishes eligibility and routing; real rasters establish the bounded L8 results; primary product guides establish calibration semantics; all other real acquisitions remain uncertain. لا تعني أهلية الطريقة في الجدول نجاح تشغيلها أو تحققها الحقلي؛ العينات الصناعية والحقيقية مفصولتان صراحة.
