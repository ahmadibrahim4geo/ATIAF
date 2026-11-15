# PLAN-0015 — Usability, canonical naming and evidence recovery

- Revision: r6; 2026-11-15. Status: Active; consolidated implementation authorized and in progress.
- Request: repair unusable tools and absent calculations, enforce sensor-first and output-last order, ATIAF with I, explain shared core versus host adapters, rename docs to documentation, organize project documents, use supplied logo then banner in README and HTML index, improve bilingual help and scientific library clarity, actually apply approved skills.
- Authorization: user's current repair request; local reversible changes. No upstream skills modification, upload, publishing or environment package installation.
- Baseline: main at 08954fc; two user PNGs and four ArcGIS-generated XML files untracked. Preserve these inputs.

## Acceptance criteria

1. One implementation package `atiaf_core`; any old spelling is an explicitly documented compatibility shim, with identical nested module/class identity. ArcGIS and QGIS remain thin separate adapters.
2. All six tool dialogs expose sensor, input, QA/preprocessing, optional mosaic, explicit tool calculations (initially unselected), AOI, native CRS, map option and output folder LAST. Invalid or unsupported choices give actionable reasons. Sensor choices must affect preflight.
3. Selected calculations, QA, AOI, CRS, destination and mosaic must reach actual processing, with output readback. Fail safely for missing science prerequisites. Expert mapping must be explicit and validated or visibly blocked, never silently ignored.
4. `documentation/` contains user help and project references; English/Arabic guides explain each tool, available/gated science, installation, folder roles and a concrete first run. Historical records preserved, moved paths discoverable.
5. Supplied logo appears before banner in both READMEs and HTML portal, local assets work offline and retain original proportions. Original input PNGs preserved.
6. Correct release/support claims and distinguish observed T0/T1, native host tests, real products and clean install. Fresh package/unit/native checks and report, indexes, state and canonical journal updated.

## Execution and verification

Inspect existing engines and native APIs; implement focused shared contract/orchestration and adapter repairs; test fixtures including sensor mismatch, empty selection, CRS change, AOI, rerun preservation and missing dependencies. Run full regression suite, structural/link checks, native QGIS tests when available, native ArcGIS checks when importable, and visual portal checks. Record exact failures. No new scientific formula/catalog import in this repair phase.

## Dependencies and initial findings

- Approved skills checkout verified at 2a0a9a23618e40218484ec8ae5848a481df51f1a; bootstrap succeeds using explicit installed Python. Journal verifies 28 records.
- Python command alias is inaccessible; standalone Python is available at the installed pythoncore-3.14-64 executable. Scientific libraries import.
- ArcPy import crashes with process code -1073741819 in current execution context; native Pro validation currently blocked, not passed.
- Existing report 0014 and state claim stable readiness without demonstrated real-product/clean-install evidence. Correct by new records, preserve previous reports.

## Outputs

Code and regression repairs; bilingual documentation and portal; source asset manifest; Reports/0015_*.md and evidence files; canonical journal records and handoff. Keep plan Active if any required native/user acceptance remains unverified.

## Progress and handoff — 2026-11-15

r1 requirements retained. Reports 0015 (audit) and 0016 (implementation/evidence) written. Final observed checks: 124 fixture/regression tests, 8 native QGIS tests, 6 native Pro tests, isolated package checks and offline desktop/mobile portal checks PASS. Initial native import blocker resolved using the activated authorized vendor runtime; CF-1 warning remains recorded. Keep Active: actual GUI/RTL click-through, real L1/L2 products, clean-machine installation and full concurrency/CRS suitability acceptance remain unverified. No upstream skill edit, commit/push or publication. The old Y package was removed, not retained as a second implementation.

## Revision history

- r1 (2026-11-14–15): implemented repair and bounded evidence in reports 0015–0016. Original six acceptance criteria above are retained.
- r2 (2026-11-15): user discussion clarified manual file selection and QGIS-owned packaging. Record the following requirements for consolidated review; do not implement folder moves or runtime UI changes during this discussion. Prior r1 evidence does not verify the new r2 behavior.
- r3 (2026-11-15): research additional useful indices on free sensors; remove calculation filtering/search from tool dialogs; group calculations by theme in both hosts; explain and propose clearer LST/unit/emissivity controls. Research and requirements recorded only; no new formula or runtime UI implementation.
- r4 (2026-11-15): user reaffirms NDVI as an optional input to LST derivation, not only an independent emissivity output; asks about Sentinel-1 availability/usefulness. Current limitations inspected and recorded; no new runtime behavior or validated radar tool.
- r5 (2026-11-15): user requests complete EN/AR interpretation of each index/output, range meaning, evidence for classification standards, limitations and locally adjustable thresholds with accurate labels and provenance. Current catalogs contain formulas/roles/citations, not the requested complete interpretation. Record requirements only.
- r6 (2026-11-15): user says execute. All r1–r5 acceptance retained. Implement native manual input/grouping, LST units/optional NDVI derivation, interpretation and local classification, and QGIS-owned packaging. First reviewed numerical additions: EVI2 2.5/2.4 and unadjusted NIRv; AWEI/MTCI/IBI/MIRBI remain candidates pending original variant/product review. No unsupported SAR tool claimed. Real-product/clean-machine gaps remain acceptance work.

## r6 concrete execution and evidence gates

- Shared dependency-light fields; native local file controls with independent manual toggle and actual sensor. Explicit scale/offset/platform/date/provenance; optional JSON import. No mandatory all-band input.
- Grouped calculation controls in both hosts, no calculation search; conditional QGIS native panel and Pro parameters. Output folder last.
- One LST control and Celsius/Kelvin units. NDVI-assisted RTE inversion needs calibrated at-sensor radiance, local band Planck constants, atmospheric transmittance/up/down radiance, user-supplied band emissivities/NDVI thresholds/provenance. Negative NDVI excluded. This explicit linear mixture is not a claim to reproduce the full TM5 model or real-product accuracy. No hidden atmospheric download or correction of official ST twice.
- Shared EN/AR interpretation metadata drives generated catalogs/HTML/portal/reports. Optional local NDVI classes record exact boundaries/source/local basis, separate raster/legend/report, and preserve continuous values.
- Build 1.0.2.dev0 ZIP under QGIS Tools/Distribution, preserve old archives and verify source identity/relocated native execution. General tools/ rename remains outside this batch.
- Verify regression/numeric fixtures, actual QGIS widgets and native execution, Pro parameter/execution checks, docs/link/build/package checks. Real acquisitions and clean-machine acceptance remain NOT RUN without suitable actual inputs/environment. Keep Active until all retained criteria verified.

## r2 requested changes — not implemented

### Input naming and manual band UI

- Use `Input Data Folder` / `مجلد بيانات الإدخال` consistently in all six tools in ArcGIS Pro and QGIS; explain single/multiple scenes in help instead of the parent-folder label.
- Keep the actual sensor/product selection separate from a clearly labeled optional `Manual Band Mapping` / `تعيين الباندات يدويًا` switch.
- Enabling the switch reveals native local band-file inputs in both hosts. Users may have incomplete scene/header metadata but know their sensor and available bands; they select only the available/needed files, not every sensor band.
- Explain expected physical role, sensor band number and wavelength. Required inputs follow selected calculations (e.g. NDVI needs red/NIR; EVI additionally blue); unavailable calculations identify missing prerequisites.
- Request essential level/unit/calibration provenance when missing; never infer unknown calibration or claim arbitrary DN/brightness temperature is calibrated reflectance/LST.
- JSON becomes optional import/export of a mapping created through the UI, not the required normal interface for manual mapping.

### QGIS-specific distribution ownership

- User requirement: the QGIS installable package must live in an explicitly QGIS-owned location, reflected in the plan, project navigation and build workflow; a generic root distribution folder must not obscure which program the ZIP belongs to.
- Proposed destination for consolidated review: `QGIS Tools/Distribution/ATIAF-QGIS-<version>.zip`. Existing source stays at `QGIS Tools/atiaf/`; `atiaf_core/` stays shared. This is a proposed path, not a completed move.
- Update the package builder default, relocated-plugin/source-identity tests, relevant CI commands, README, EN/AR installation guides and links together when implementation is authorized.
- Separate QGIS installables from core wheel and browser/test outputs. Preserve earlier archives/results and document migrations; do not delete historical builds.
- A source update must be followed by an explicitly built current ZIP in the QGIS-owned location. Test the package outside the checkout with the supported QGIS runtime and record source/package identity.
- Renaming general `tools/` to `developer_tools/` remains an assistant proposal for discussion, not a user-approved code/folder change.

### r2 acceptance to add to the implementation check

- R2-A1: equivalent input labels and optional manual-mode visibility in the six native tools of both hosts, verified in the actual dialogs.
- R2-A2: red/NIR-only manual fixture runs NDVI without unrelated bands; missing blue prevents EVI with an explanation; JSON is optional, and unknown calibration remains gated.
- R2-A3: a self-contained current QGIS ZIP is generated in the agreed QGIS-owned directory, and relocated native execution plus source identity pass.
- R2-A4: current documentation/CI/tests/build defaults use the agreed path; core/test artifacts are separately identified; history is retained. Previous r1 test counts are not r2 acceptance evidence.

## ملخص متطلبات المناقشة

الاسم المقترح موحّد: مجلد بيانات الإدخال. التعيين اليدوي خيار مستقل يظهر حقول اختيار الباندات عند تفعيله في البرنامجين، ويطلب المتاح واللازم فقط مع توثيق المعايرة. JSON وسيلة اختيارية لحفظ التعريف واستيراده. حزم QGIS يكون لها مكان تابع له بوضوح؛ المسار المقترح داخل QGIS Tools/Distribution، مع ربط البناء والاختبارات والتوثيق به وفصل حزمة المحرك ومخرجات التجارب. هذه متطلبات للمراجعة المجمعة؛ لم تُنفذ تغييرات الواجهة أو نقل المجلدات في هذه المراجعة.

## r3 research and requested calculation organization — not implemented

- Remove the calculation-search/filter control from analysis tool dialogs. It currently filters local Pro calculation controls; it does not search imagery, the web or new methods. QGIS currently has a native multiple-selection widget, not an equivalent custom search parameter. Do not add a custom search there. The separate documentation portal search is outside this removal request.
- Show selectable calculations under meaningful thematic headings in BOTH native hosts: Vegetation/Chlorophyll, Surface Water, Vegetation Moisture, Urban, Bare Soil, Burn, Snow, and separately labeled advanced Transformations where applicable. A single flat list or category-prefixed text alone is not the intended grouping. Preserve sensor-first, output-last, initially unchecked choices and reasons for missing prerequisites. Each of the six tools uses groups relevant to its own domain; do not merge all domains into one tool.
- Research candidates, not runnable support: EVI2, NIRv, AWEIsh/AWEInsh, a sensor-specific MTCI adaptation, IBI and MIRBI. Most have matching band roles on Landsat optical products and Sentinel-2; MTCI needs red-edge bands and a reviewed Sentinel-2 adaptation, not an assumed Landsat equivalent. Existing NDVI/NDMI/NBR/etc. are not new additions. See the linked bilingual research notes.
- Prioritize sensor/product/variant validation over index count. Check original equations/constants, calibrated reflectance, QA/NoData, band spectral response, resolution alignment, denominator behavior, citations and tests before adding a candidate. Pin an audited Awesome Spectral Indices source version/license before any selective import; no bulk Index DataBase redistribution.
- Additional thermal product readers (MODIS MOD11A1/MYD11A1 and Sentinel-3 SLSTR SL_2_LST) are optional future scope, not required for the first optical additions and not current supported workflows. Separate readers, QA, grids and native product evidence are required.
- Explain current Surface Temperature choices: Celsius and Kelvin represent the same physical temperature; NDVI-derived emissivity is an empirical dimensionless estimate and is currently gated. LST is surface, not near-surface air temperature. Do not reapply emissivity correction to an official L2 ST product.
- UI proposal for consolidated review, not yet a settled user choice: one explicit LST calculation with output unit Celsius/Kelvin (proposed Celsius default); optional advanced emissivity outputs in a separate group with a clear method/source/status. Do not silently replace the existing parameter IDs until migration is documented. Do not enable the gated NDVI emissivity model through a label change.

### r3 acceptance to add to implementation

- R3-A1: inspect all six actual dialogs in both hosts; no custom calculation search remains, thematic groups and selection behavior are usable in English/Arabic, and unrelated portal search remains separate.
- R3-A2: each accepted new index has reviewed original citations/variant, explicit sensor/level/band requirements, independent numeric fixtures and real-product/native readback evidence; others remain proposed or gated. No sensor is declared supported from band matching alone.
- R3-A3: agreed temperature UI explains units and emissivity; unit conversion is verified numerically (303.15 K = 30 °C), official L2 ST is not corrected twice, and Sentinel-2 optical-only input cannot masquerade as thermal LST. Native UI/readback checks must be fresh.
- R3-A4: EN/AR help, registry statuses, examples, packaging and reports match the agreed implemented scope. r1 test counts do not validate r2/r3 behavior.

Research: [English](../../documentation/en/INDICES_AND_TEMPERATURE_REVIEW.md), [العربية](../../documentation/ar/INDICES_AND_TEMPERATURE_REVIEW.md).

تحديث r3: أضيف طلب إزالة البحث من واجهات الحسابات وتجميع المؤشرات تحت عناوين موضوعية في البرنامجين، وبحث مرشحات جديدة وشرح وحدات الحرارة والانبعاثية. تبسيط واجهة الحرارة وإضافة المؤشرات والمستشعرات ما زال مقترحًا للمراجعة المجمعة؛ لم يحدث تنفيذ أو تحقق علمي جديد لهذه المرشحات.

## r4 clarification — NDVI-assisted LST and Sentinel-1

- Preserve the user's original optional NDVI-assisted LST requirement. A separate emissivity output alone does not satisfy it. A validated derivation would use NDVI to estimate vegetation cover/emissivity, together with real calibrated thermal observations and method-specific atmospheric inputs. Never add NDVI directly to temperature or apply an extra correction to official L2 ST.
- Proposed input UX for review: select NDVI-assisted derivation, then choose an existing local NDVI raster or calculation from corresponding red/NIR bands. Require source/date/grid/mask compatibility, documented emissivity assumptions and complete thermal/atmospheric provenance; report intermediates and distinguish the result from official L2 ST. No hidden downloads.
- Current implementation: no external NDVI parameter, no complete NDVI-assisted LST path; shared workflow invokes Official_L2_ST. The gated EMISSIVITY_NDVI choice and old low-level emissivity branch do not provide that functionality.
- Sentinel-1 is a free-data C-band SAR mission, useful for flood/water change, agriculture and surface-moisture studies, and (with separate SLC interferometry) deformation. It provides neither optical red/NIR NDVI nor direct thermal LST. Current parser/array helpers are preliminary; no dedicated validated native radar tool exists. Its investigation is recorded, not automatic authorization to implement an entire SAR phase.
- R4-A1 (not run): both host dialogs expose the agreed optional NDVI-assisted path, compatible existing/computed NDVI, actionable missing-input gates and fresh thermal output readback; producing emissivity alone is insufficient.
- R4-A2 (not run): original method/sensor-specific equations, calibrated thermal/atmospheric inputs, NDVI provenance and uncertainty validated on independent fixtures/real products; official L2 ST never corrected twice.
- R4-A3: documentation keeps Sentinel-1 parser/helpers distinct from native validated SAR workflows. If a future radar phase is selected, start with an explicit GRD/backscatter scope and separate SLC/InSAR scope, with calibration/noise/terrain/orbit/DEM dependencies declared and supplied locally when needed.

تأكيد r4: المطلوب خيار فعلي لاستخدام NDVI ضمن اشتقاق حرارة السطح، وليس مجرد إخراج خريطة انبعاثية. هذا المسار غير منفذ حاليًا. Sentinel-1 موجود ومفيد، لكن الكود الأولي داخل المشروع ليس أداة رادار جاهزة أو متحققًا منها.

## r5 output interpretation and classification documentation — not implemented

- Every implemented calculation needs matching English/Arabic help explaining scientific meaning, equation/variant, required sensor/product/bands, units, theoretical versus typical observed range, valid/NoData/QA behavior, what high/low/negative values imply and what cannot be inferred. Do not assume every index is bounded by [-1,1]. Explain exceptional values and input/mask/scaling checks rather than silently clipping them.
- For classification, distinguish (a) a verified named formal standard with issuer/version/scope, (b) an original-paper method and its study context, (c) authoritative educational guidance, and (d) user-defined/local calibration. Never label a frequently repeated table an international standard. If no verified applicable standard exists, say so.
- Provide sourced class/interpretation tables only where scientifically justified: exact boundaries and inclusivity, code, EN/AR label, interpretation, applicable sensor/season/land cover and limitations. General indicative examples must be visibly separated from executable class presets; do not force classes on every continuous output.
- NDVI example: generally [-1,1] under valid nonnegative reflectance and a nonzero denominator; negative/near-zero is not a universal water/soil classifier, and high greenness is not a standalone diagnosis of crop health. Local vegetation type, phenology, soil background, moisture, atmosphere and resolution affect values. Prefer defensible labels such as sparse/moderate/dense green vegetation or low/moderate/high greenness; do not equate low NDVI automatically with sick plants.
- Where a reviewed class preset is offered, the user can optionally adjust numeric breaks for the study area while retaining appropriate scientific class concepts/IDs. Clearly label customized classes as local/user-defined, not compliant with an unchanged standard. Arbitrary relabeling must not imply measured biomass, yield, species or health.
- Preserve continuous scientific raster values; optional classified rasters/styles are separate. Reports/legends must record the preset/source/version, original and effective breaks, labels, inclusivity, units, user modifications and local-validation basis. Across-date comparisons must identify changed classification schemes.
- Explain how to calibrate locally using representative reference samples/field or independent imagery, assess classification errors where appropriate, and state limitations if no local validation is available. A histogram or quantile split alone does not validate ecological class meaning.
- Implement through canonical interpretation/classification metadata and `tools/build_documentation.py` so rebuilt Markdown/HTML and packaged host help retain the same EN/AR explanations. Correct the current SCIENTIFIC_METHODS claim that complete interpretation tables already exist in INDICATORS_CATALOG; synchronize tool help, website, run reports and examples when implemented.

### r5 acceptance — fresh checks required

- R5-A1: all exposed calculation IDs/variants have complete matching EN/AR interpretation entries or explicit scientifically justified no-classification status; generator coverage checks detect missing entries and rebuilt docs retain them.
- R5-A2: references and standard-vs-guidance-vs-local status are verified; the NDVI example carries a visible local-applicability warning and no unsupported global class/health claim.
- R5-A3: tests verify exact class boundaries, no overlapping bins, gaps handled explicitly, NoData/masks/out-of-range handling, and identical meaning across both languages. Continuous source output remains unchanged. Where adjustable classes are implemented, actual native host checks verify optional controls and saved effective settings.
- R5-A4: generated docs/portal/help, raster legends and EN/AR reports agree with the effective class scheme; original/custom settings and provenance survive package/rebuild/readback. Real local validation remains NOT RUN until real evidence exists; do not confuse a configuration test with validated ecological thresholds.

Reference/requirements notes: [English](../../documentation/en/OUTPUT_INTERPRETATION_REQUIREMENTS.md), [العربية](../../documentation/ar/OUTPUT_INTERPRETATION_REQUIREMENTS.md).

ملخص r5: يُضاف شرح معنى ناتج كل مؤشر ومداه ووحداته ودلالة القيم ومحدودية تفسيرها، مع بيان هل التصنيف معيار موثق أم طريقة بحثية أم إرشاد أم تصنيف محلي. حدود الفئات المناسبة لمنطقة الدراسة قابلة للضبط عند توفير تصنيف اختياري، مع إبقاء المسميات العلمية دقيقة وتسجيل المصدر والقيم الأصلية والمعدلة في التقرير. قيم المؤشر الأصلية لا تتغير بسبب التصنيف. هذا المتطلب سُجل ولم تُنفذ تغطيته الشاملة أو واجهاته بعد.
