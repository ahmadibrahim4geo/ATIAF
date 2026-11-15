# Report 0018 — Additional-index research and temperature UX requirements

- Date: 2026-11-15. Plan: [PLAN-0015 r3](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md).
- Status: **RESEARCH / REQUIREMENTS RECORDED; r2/r3 runtime implementation NOT STARTED**.
- Git: main, baseline 08954fc1add9b4bdb0b2b5645cebde35cba21235. Existing local changes preserved; no commit/push/publication or host environment installation.

## Request and observed source behavior

User requested useful additional indices for popular free sensors, assessment of other sensors, removal of calculation search if it only filters, thematic groups inside tools, and an explanation of Surface Temperature choices before consolidated implementation.

`ArcGIS Pro Tools/atiaf_arcgis.py` defines a `search` parameter and uses it to enable matching existing calculation controls. There is no network or algorithm discovery in this control. QGIS's shared adapter uses a native multiselect without the same custom search parameter. Removal request concerns analysis dialogs; documentation portal search is distinct.

Current shared Surface Temperature IDs are LST_CELSIUS, LST_KELVIN and EMISSIVITY_NDVI. `atiaf_core/workflow.py` gates the latter for method/threshold review. The first two are units of the same official L2 ST quantity. Scientific caveats and a proposed single calculation/unit selector are recorded without enabling the gated method or changing parameter IDs.

## Research result and limits

New runtime-catalog candidates: EVI2, NIRv, AWEIsh/AWEInsh, a sensor-specific MTCI adaptation, IBI and MIRBI. Most band roles are available on common Landsat/Sentinel-2 optical products; MTCI requires appropriate red-edge adaptation and cannot be assumed available on Landsat. This is feasibility analysis, not new implemented/validated support. Existing NDVI/NDMI/NBR/etc. are not counted as new.

Optional future thermal products: MODIS MOD11A1/MYD11A1 and Sentinel-3 SLSTR SL_2_LST at 1 km. New local readers/QA/scaling/geolocation and tests are required; none were implemented. Sentinel-2 optical-only imagery does not provide a thermal LST measurement.

Reviewed official USGS/NASA/Copernicus documentation, accessible original research abstracts/publisher records and Awesome Spectral Indices maintainers' own definitions/citations. Some original DOI opens and PMC access failed/challenged; this is explicitly documented. Full original coefficient/variant review is pending. An EVI2 catalog coefficient representation demonstrates why blind import is inappropriate. No formula was copied into runtime code, no source catalog/data was imported, no ASI release pinned. MIT declaration is not a completed version/license audit for a future import. Index DataBase bulk redistribution remains prohibited.

Full source links, access limitations and matching EN/AR explanations: [English review](../documentation/en/INDICES_AND_TEMPERATURE_REVIEW.md), [Arabic review](../documentation/ar/INDICES_AND_TEMPERATURE_REVIEW.md).

## Files and verification

- Added both research notes, retained r1/r2 plan requirements and appended r3 acceptance; updated source navigation, both indexes and PROJECT_STATE. Journal revision #0034 links #0033.
- Read-only checks: `git status --short`; `rg -n -C 3 'surface_temperature|LST_CELSIUS|LST_KELVIN|EMISSIVITY_NDVI' atiaf_core/tool_contract.py atiaf_core/workflow.py`; catalog ID inspection using installed Python. Current source confirms the stated control/gate behavior; no native dialog action was performed.
- `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe .agent_resources/GIS-Development-Skills/scripts/development_journal.py verify --project .`: **33 records valid before r3**. Append via reviewed helper: #0034 recorded.
- `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe tools/validate_package.py`: exit 0, **STRUCTURAL VALIDATION PASS**, 26 candidate registry records, 19 planned sensor records; 352 Markdown / 53 JSON at first post-research check. Counts describe registry contents, not validated science support. A final structural check follows addition of this report/index links.
- Scientific numeric tests, native ArcGIS/QGIS, real products, package rebuild and UI grouping/unit migration: **NOT RUN for r3**; no runtime changes. Earlier r1 124/8/6 results do not validate r2/r3 acceptance. Overall PLAN-0015 remains **PARTIAL / ACTIVE**.

## Handoff

Continue consolidated user discussion, then implement agreed r2/r3 UI/package scope. Confirm the proposed temperature control shape in that review, review original candidate variants and select the incremental science scope. Validate each accepted algorithm numerically and on real products/native hosts before claiming support. Keep old report/history/artifacts intact. No new changelog feature entry because no runtime behavior changed.

## ملخص عربي

حُفظ بحث عن مؤشرات إضافية مفيدة ومعظمها مرشح للعمل على Landsat وSentinel-2، مع فصل الإمكانية النظرية عن الدعم الفعلي. سُجل طلب إزالة بحث الحسابات وتصنيف المؤشرات داخل البرنامجين. شُرح أن المئوية والكلفن وحدتان لنفس حرارة السطح، وأن تقدير الانبعاثية من NDVI طريقة مختلفة وموقوفة للمراجعة حاليًا. تبسيط واجهة الحرارة مقترح للمناقشة. لم تتغير الأدوات أو الحزم ولم تُضف مؤشرات أو مستشعرات في هذه الدفعة؛ الخطة ما زالت نشطة.
