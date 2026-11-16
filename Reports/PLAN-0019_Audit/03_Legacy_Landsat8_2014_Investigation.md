# PLAN-0019 r1 — 03 Legacy Landsat8 investigation

Actual supplied folder: `Testing Data/LC81760392014234LGN00`. Exact source MTL and source/output hashes are recorded in [numerical audit](../evidence/PLAN-0019/exact_crc1_audit/numerical_audit.json); discovery before changes is in [baseline inventory](../evidence/PLAN-0019/baseline_inventory.json). Input dimensions 7711×7861, projected CRS EPSG:32636, 30 m source grid. No reprojection was needed for these checks; this is observed source CRS, not an imposed default.

| Evidence | Finding |
|---|---|
| Old Scene ID | LC8 + path176 + row039 + year2014 + day234 + stationLGN + archive version00 |
| Actual MTL | SPACECRAFT_ID LANDSAT_8, DATA_TYPE L1T, DATE_ACQUIRED 2014-08-22; no collection/product-ID field establishing C1/C2 |
| Identity meaning | LGN is a receiving/processing station code; final00 is archive version, not Collection2 or Level2 |
| Modern identity | Product ID has distinct acquisition and processing dates plus collection/tier fields; same acquisition can be reprocessed later |
| Radiometry | Optical reflectance coefficients and SUN_ELEVATION establish TOA, not SR |
| Calibration | `(DN*REFLECTANCE_MULT_BAND_n+REFLECTANCE_ADD_BAND_n)/sin(SUN_ELEVATION)`; each filename/coefficient/key retained in metadata |
| QA | Positive legacy identification selects pre-Collection BQA, never C1 BQA or C2 QA_PIXEL by filename alone |

Primary references: [USGS Scene ID vs Product ID](https://www.usgs.gov/faqs/how-can-i-tell-difference-between-landsat-collections-data-and-landsat-data-i-have-downloaded), [USGS L1 calibration](https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product), [QA tools guide v1.4](https://landsat.usgs.gov/sites/default/files/documents/landsat_QA_tools_userguide.pdf). Calibration uses scene-center sun angle; per-pixel sun-angle correction is not performed. Legacy BQA excludes fill/dropped frame/terrain and medium/high snow/cirrus/cloud confidence. Confidence00 is undetermined, retained with limitations; shadow/per-band saturation flags do not exist in this legacy schema. Raw0/65535 excluded.

Before: shared Landsat reader returned UNKNOWN/zero bands; only T07's separate legacy path worked. After: metadata-first reader is shared by discovery, diagnostic NDVI and RGB. NDVI requires explicit TOA opt-in and is named NDVI_TOA. SR-specific methods and official LST stay gated; raw B10 brightness temperature is not official ST. TOA ratios are dimensionless but retain atmospheric/calibration dependence. No C2 SR factor was applied to this L1T bundle; no FLAASH/DOS/atmospheric download was silently run.

C1 SR uses 0.0001/0/-9999 while C2 SR uses 0.0000275/-0.2/0 for scale/offset/fill; see [official scaling comparison](https://www.usgs.gov/faqs/why-are-fill-values-and-scaling-factors-landsat-collection-2-level-2-products-different-those?items_per_page=6&page=1). The new explicit ESPA and matching companion-MTL reader uses only the XML's SR assets, not companion L1 bands accidentally scaled as SR. Original inputs and previous results are unchanged; no same-acquisition C1/C2 counterpart is supplied, so cross-generation radiometric/geometry/calibration-notice differences remain NOT_TESTED. Calibration notices are context, not permission to invent updated coefficients for the old bundle.

بالعربية: تاريخ 2014 لا يمنع المعالجة ولا يثبت أنها Collection1/2. المرئية القديمة مثبتة ببياناتها الأصلية، وتستخدم معايرة TOA الموثقة؛ لا تُفرض إعادة تنزيل. المقارنة مع نسخة حديثة لنفس الالتقاط تحتاج ملفها الحقيقي ولم تُنفذ ببيانات صناعية بديلة.
