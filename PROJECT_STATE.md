# ATIAF — Current implementation and evidence

**Latest delivery — report [0032](Reports/0032_advanced_envi_indices_and_qa_mask_engine.md), PLAN-0020 r1 completed.** All objectives of PLAN-0020 are implemented, verified, and empirically validated:
1. Intelligent Quality Mask Engine (`atiaf_core/raster/masks.py`): Multi-mode QA engine (`Cloud_Only_Arid`, `Full_Strict`, `Water_Protected`, `None`). Defaulted to `Cloud_Only_Arid` across ATIAF tools to eliminate false-positive cirrus, terrain shadow, and dilation masking over desert rocks and rivers.
2. Complete resolution of Missing Cells / White Holes: In real desert mountain crop (`LC09_L2SP_174043_...`), missing NoData pixels dropped from 23,705 (under strict mode) to only 29 (under Arid mode), recovering **23,676 real rock pixels (99.88% reduction in missing pixels)**.
3. Optical negative reflectance clamped to positive epsilon ($\epsilon = 0.0001$) across indices, geology, environment, and composites engines to prevent NaN and zero-division artifacts over dark water and shadows.
4. Advanced NV5 ENVI 6.3 & Geoscience Indices: 6 new indices fully integrated (`MTVI2`, `MCARI2`, `NDRE2`, `CIGREEN`, `CIREDEDGE`, `NDSI_SALINITY`) with dependency-free cataloging, compute registry, and bilingual interpretations.
5. Host UI parity in ArcGIS Pro (`ArcGIS Pro Tools/atiaf_arcgis.py`) and QGIS (`QGIS Tools/atiaf/algorithms/common.py`) with new `qa_mask_mode` parameter, adhering strictly to D-008 bilingual isolation.
6. Comprehensive Results Directory Tree Guide documented for end users.
7. Observed evidence: **192 unittests PASS (100%)**; full dual-scene real testing across 5 test suites on modern Landsat 9 C2 L2 and legacy Landsat 8 L1T scenes, producing verified GeoTIFF rasters in `Testing Results/PLAN-0020/` with summary manifest `plan0020_real_validation_summary.json`.

Snapshot: **2026-11-17**. Authorized root `D:/My Software/ATIAF`, branch `main`. Prior uncommitted work preserved.

## Current work — PLAN-0020 Completed; PLAN-0019 r2 Completed; PLAN-0018 / PLAN-0015 Active / partial

PLAN-0020 r1 intaken: Advanced ENVI & geoscience indices integration and intelligent QA mask engine. Diagnosed root cause of missing cells / white holes (CFMask Cirrus & Shadow false positives over desert mountains and river water). Plan covers granular QA mask modes (`Cloud_Only_Arid`, `Full_Strict`, `Water_Protected`, `None`), negative reflectance clamping, ENVI 6.3 indices integration in Tools 01/04/05, strict EN/AR separation, and dual-scene validation.

Local **1.0.4.dev0** implements shared legacy Landsat generation/identity/calibration/QA (including explicit matching ESPA), TM/ETM/MSS physical roles/SLC date, Sentinel2 per-band baseline offsets/quantification and diagnostic NDVI_TOA opt-in. Other SR/thermal/ancillary gates retained. T07 now has clear actual-satellite/recipe names, unique Analytical/Display/Metadata/QA_Reports, optional Work channels, NaN analytic NoData, full channel moments and separate display stretch modes/source explanations. No CRC1 formula/channel change.

The exact old CRC1 artifact was audited read-only:40,394,219 valid +20,221,952 NoData pixels/channel, zero mask mismatch/nonfinite, independent stable native arithmetic PASS. Bare-candidate median display14/207/231 explains cyan; no rock/mineral truth inferred. [Six audit deliverables](Reports/PLAN-0019_Audit/01_Sensor_Product_Compatibility_Matrix.md) include893 explicit product/method gate cells,100-pixel CSV and scientific/source/uncertainty distinction.

Observed final: **183 headless PASS; QGIS3 composites/11 regressions PASS; Pro2 composites/8 regressions PASS.** Both native languages exercised. Real RGB QGIS EN/Pro AR and NDVI QGIS AR/Pro EN independent readback PASS; full per-pixel analytic/display/NDVI values, masks and grids exactly agree. Final real QGIS metadata/stats reopened. Relocated QGIS ZIP NDVI/RGB, wheel/core/adapter/bilingual-help identity, isolated wheel import and offline desktop/mobile portal47cards PASS. Native evidence is offscreen/GP, not full installed interactive journeys or clean-machine install.

Current local packages: `QGIS Tools/Distribution/ATIAF-QGIS-1.0.4.dev0.zip`, `dist/atiaf-1.0.4.dev0-py3-none-any.whl`; hashes/evidence in0029. Earlier builds/imagery/results preserved, no runtime installs. Pro CF-1 database warning remains outside tested GeoTIFF scope. Scientific/source-checkout audit links are not additional bundled plugin assets.

Plan intake policy now **moves** supplied plans into numbered folders before implementation; optional original snapshots only in Source_Archive. PLAN-0019 source SHA verified; root intake absent; all14 requirements verbatim, progress checkmarks updated. [Bound DoneProof](Reports/evidence/PLAN-0019/doneproof_r1.json):10 verified within scope,4 partial; plan remains Active. PLAN-0018/0015 remain partial, PLAN-0016/0017 complete.

**Exact next work:** mapped rocky reference, same-acquisition C2/archived C1 and real other sensors when supplied, their actual QA/method/CRS/native journeys and clean install; automatic exact ASTER/Fawakheir/field/recovery acceptance remains unverified. No forced imagery download or invented scientific support. Read0029, plan and Journal handoff first.

نُقلت الخطة ورُقمت وحدّثت قواعد الوكيل، ونُفذ التدقيق والإصلاح والاختبار الممكن محليًا مع حفظ المصادر والنتائج. ثبت سبب السماوي حسابيًا دون تغيير الوصفة. الخطة نشطة لأن المرجع الصخري وبقية المرئيات والقبول الشامل غير متاحة أو غير مثبتة.

## Historical state snapshots

Snapshot: 2026-11-15. Authorized root: `D:/My Software/ATIAF`, branch `main`. Project published to https://github.com/ahmadibrahim4geo/ATIAF. Verified source commit `31794beb5c58b59b997d862d4689cb4001b56432`; headless/package CI and existing Pages deployment both succeeded. This state/report/journal archive follows in a records-only normal push; original Git history preserved.

## Earlier work snapshots

**PLAN-0018 r1 is IMPLEMENTED / PARTIAL — Geological Color Composites.** Local build **1.0.3.dev1** adds a seventh independent native tool with Direct RGB / Ratio RGB, exact-band mapping/calibration, reviewed/experimental/custom presets, separate display, native QGIS background before/after and Pro temporary HTML previews, preset save/import, polygon clip and coherent RGB mosaic provenance. See [delivery report 0027](Reports/0027_geological_color_composites_implementation_and_validation.md), [EN guide](documentation/en/GEOLOGICAL_COLOR_COMPOSITES.md), [AR guide](documentation/ar/GEOLOGICAL_COLOR_COMPOSITES.md), and [21-criterion partial DoneProof](Reports/evidence/PLAN-0018/doneproof_r1.json).

- Fresh: **162 headless PASS**, new QGIS **3** / Pro **2** native checks PASS; existing QGIS **11** regression checks PASS. Pro regression: seven passes in the eight-case suite; an outdated filename assertion was corrected and the single case rerun passed. Native scopes include controlled offscreen Qt preview/panels and saved RGB CIM, not full installed desktop journeys.
- User supplied `Testing Data/LC81760392014234LGN00`: actual pre-Collection Landsat8 L1T, calibrated as **TOA**, not surface reflectance. Correct legacy BQA; no atmospheric correction. QGIS English and actual Pro Arabic generated both methods. Independent sampled readback and complete raster comparison pass: **60,616,171 pixels per channel/method, bitwise equal, same CRS/grid/masks**. Pro helper receipt failed after GP output creation; separate readback/equivalence establishes products, not a successful helper exit. Preserve all failure logs.
- Local ZIP: `QGIS Tools/Distribution/ATIAF-QGIS-1.0.3.dev1.zip`; wheel: `dist/atiaf-1.0.3.dev1-py3-none-any.whl`. Source/help identity, isolated wheel and relocated native QGIS NDVI/RGB PASS. Offline desktop/mobile portal PASS with 47 cards. Original scene/source plan preserved; imagery/derivatives stay local and ignored. **No publication or stable release in this phase.** Prior package versions retained.
- Retain Active: complete automatic ASTER reader/calibration; real Sentinel-2/ASTER and mixed-resolution science; Fawakheir source review; field interpretation; full installed native UI/Pro journeys and clean-machine install; comprehensive CRS/concurrency/mid-write recovery acceptance. Exact next step: report 0027 handoff. PLAN-0015 stays partial; PLAN-0016/0017 remain complete. Pro CF-1 lookup warning persists outside tested GeoTIFF scope.

أضيفت أداة التراكيب بطريقتي RGB المباشر والنسب، مع عرض ومعاينة مستقلين عن الراستر التحليلي. اختُبرت مرئية Landsat 8 L1T المتاحة محليًا بانعكاس TOA، وتطابقت نتائج QGIS والنسخة العربية من Pro على كامل الراستر. الحزم محلية تجريبية؛ تبقى الخطة نشطة لاختبارات المستشعرات الأخرى والواجهة والتثبيت والتحقق الجيولوجي.

**PLAN-0017 r1: verified instruction/documentation change — descriptive plan/report naming.** Any supplied plan filename or conversational development request is covered; retain/derive the descriptive title, preserve supplied originals, and use `PLAN-<NNNN>_<descriptive_name>.md`. Reports require an independent number plus descriptive name/heading. Instructions, startup, indexes, registry and EN/AR addenda are synchronized; documentation/link and whitespace checks pass. See [0025](Reports/0025_agent_plan_report_naming.md). No processing change or geological implementation; supplied source unchanged. PLAN-0015 remains partial and PLAN-0016 complete. تم توحيد قواعد تسمية الخطط والتقارير وترقيم كل منهما بصورة مستقلة مع حفظ الأصل؛ لم يبدأ تنفيذ الخطة الجيولوجية.

**PLAN-0016 r1 is VERIFIED / COMPLETE: professional project presentation and GitHub publication.** Snapshot **1.0.2.dev1** is published with EN/AR README, offline/root Index, supplied logo/banner and community/citation files. Live page: https://ahmadibrahim4geo.github.io/ATIAF/ (HTTP 200). Hosted run 43733305094 succeeded: **141 tests**, documentation/links/JSON, QGIS/core builds, package identity and both downloadable artifacts. Pages run 43733304028 succeeded. Remote SHA/key files independently matched. See [0024](Reports/0024_verified_github_delivery.md) and publication receipt. PLAN-0016 archived after its delivery report; PLAN-0015 remains Active/partial.

**PLAN-0015 r6 is ACTIVE / PARTIAL: consolidated implementation delivered locally with bounded native/synthetic evidence.** Earlier stable-release/all-roadmap-complete claims in reports 0001–0014 remain superseded. Version **1.0.2.dev0 is a development build**, not a validated stable release. Original and added acceptance are retained; real acquisitions, clean installation and full interactive host acceptance remain unverified.

Previous numbered-report snapshot: [0027 composites implementation/validation](Reports/0027_geological_color_composites_implementation_and_validation.md). Inspection: [0026](Reports/0026_geological_color_composites_inspection.md). Naming rules: [0025](Reports/0025_agent_plan_report_naming.md). Publication delivery: [0024](Reports/0024_verified_github_delivery.md). Portability failures/fixes: [0023](Reports/0023_github_publication_and_clean_runner_portability.md). Preparation: [0022](Reports/0022_professional_presentation_and_publication_preparation.md). Consolidated implementation: [0021](Reports/0021_consolidated_tools_interpretation_and_native_evidence.md). Prior snapshots: [0020](Reports/0020_output_interpretation_and_local_classification_requirements.md), [0019](Reports/0019_ndvi_assisted_lst_and_sentinel1_clarification.md), [0018](Reports/0018_indices_research_and_temperature_requirements.md), [0017](Reports/0017_manual_input_and_qgis_distribution_requirements.md). r1 evidence: [0016](Reports/0016_usability_repair_and_verified_handoff.md); audit: [0015](Reports/0015_recovery_audit.md).

## Current r6 implementation and observed checks

- Input Data Folder / مجلد بيانات الإدخال. Separate manual toggle in both hosts with native file controls, known sensor, explicit platform/date/calibration/provenance, only available/required bands, optional saved JSON import and per-run mapping export. Current manual profiles Landsat C2 L2 and Sentinel-2 L2A. No mandatory header/JSON; missing calibration/QA is not guessed.
- Grouped initially unchecked calculations; calculation search removed. QGIS native panel has conditional manual/retrieval fields and RTL, Pro native categories/enabled parameters. Output remains last. Hidden QGIS INDICES retains compatible saved-model selection; old models/dialog caches require review/reopen.
- One LST choice and Celsius/Kelvin. Official ST default; optional single-scene local NDVI/RTE retrieval with compatible NDVI or red/NIR, calibrated thermal radiance, explicit band Planck/atmosphere/emissivity/threshold inputs and provenance. User-parameterized linear mixture omits cavity term and excludes negative NDVI; no full TM5/field-accuracy claim or extra correction of official ST.
- Per-method EN/AR interpretation metadata covers 45 catalog entries, including legacy/gated variants; generated Markdown/HTML, portal and reports show meaning/units/ranges/caveats. Optional local NDVI classes preserve continuous data, save separate class raster/legend/report and log original/effective boundaries/local basis. No international class standard claimed.
- EVI2 (gain 2.5/red 2.4) and unadjusted NIRv numerically implemented and checked on synthetic inputs in both native hosts. Other research candidates are not promoted to supported calculations.
- Fresh evidence: **140 headless tests PASS; 11 native QGIS tests PASS; 8 native Pro tests PASS**. Actual Arabic QGIS parameter panel rendered/inspected. Full six-tool Pro/QGIS execution remains synthetic. Byte identity of wheel/core/adapter/bundled help, isolated wheel and relocated QGIS execution PASS. Offline desktop/mobile portal checks PASS with 45 cards. Structure/link/JSON checks PASS. [Raw/structured evidence](Reports/evidence/PLAN-0015/r6/observations.json), [partial DoneProof with 21 retained criteria](Reports/evidence/PLAN-0015/r6/doneproof_r6.json).
- Pre-publication r6 QGIS ZIP snapshot: `QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev0.zip`; separate core wheel: `dist/atiaf-1.0.2.dev0-py3-none-any.whl`. Prior dist packages/intermediate r6 archives preserved. Builder/test/CI/docs use the QGIS-owned path. At r6 no live host installation, publication or host dependency install had occurred; current dev1 publication is recorded above.
- Original code MIT, approved skills checkout unchanged at 2a0a9a23618e40218484ec8ae5848a481df51f1a. New equations authored independently from recorded primary references. ASI Git query failed; no pinned ASI import or IDB redistribution claimed. Browser sandbox startup failure resolved with authorized separate-browser execution. Pro CF-1 database warning remains.
- Use [manual input](documentation/en/MANUAL_BANDS.md) / [العربية](documentation/ar/MANUAL_BANDS.md), [temperature](documentation/en/SURFACE_TEMPERATURE.md) / [العربية](documentation/ar/SURFACE_TEMPERATURE.md), and regenerated [catalog](documentation/ar/INDICATORS_CATALOG.md). Refresh/restart hosts after installing/reopening updated tools.

## Previous r2–r5 discussion state (historical)

The planning-only statements in this section record the earlier handoff and are superseded by current r6 behavior above. Original reports remain immutable.

r5 adds complete per-index EN/AR output interpretation and sourced classification applicability. Current catalogs contain formulas/roles/citations, not complete interpretation tables; the science-guide cross-reference overstates this coverage. Distinguish formal standards, research/educational guidance and local classes; do not invent universal NDVI thresholds. Optional local edits must retain accurate labels, continuous source values and logged original/effective class settings. See [EN](documentation/en/OUTPUT_INTERPRETATION_REQUIREMENTS.md) / [AR](documentation/ar/OUTPUT_INTERPRETATION_REQUIREMENTS.md). Full documentation/classification UI/generator/report integration remains NOT IMPLEMENTED; continue consolidated discussion from report 0020.

r4 clarification: optional NDVI-assisted **LST derivation** is a required path, not just a separate emissivity output. It is currently absent; no external NDVI parameter exists, and the visible emissivity choice is gated. Preserve scientific thermal/atmospheric inputs and do not correct official L2 ST twice. Sentinel-1 has preliminary parser/helpers only, not a dedicated validated radar tool. Its usefulness is documented; a full SAR phase is not automatically authorized by this question. Continue consolidated review using report 0019 before implementation.

- Input label: Input Data Folder / مجلد بيانات الإدخال.
- Optional native manual band-file selection in both hosts, separate from real sensor choice; only available/required bands, scientifically verified calibration; JSON optional import/export.
- QGIS-owned installable package directory linked to builder/tests/CI/EN-AR guides. Proposed path: QGIS Tools/Distribution/. Current ZIP remains in dist/ until implementation is authorized.
- General developer_tools rename is still a proposal. No runtime/folder change was performed during this discussion. Prior 124/8/6 checks and r1 DoneProof do not verify new r2 behavior.

## r3 research and calculation UX discussion

- Remove custom calculation search/filter from analysis dialogs; show thematic groups within both host tools. Portal documentation search is separate.
- Research candidates: EVI2, NIRv, AWEIsh/AWEInsh, sensor-specific MTCI adaptation, IBI and MIRBI. No formula imported or implemented; original-variant/sensor validation remains required. Most optical band requirements can be met by existing Landsat/Sentinel-2 families; this is feasibility, not support certification.
- Optional future thermal readers: MODIS MOD11A1/MYD11A1 and Sentinel-3 SLSTR SL_2_LST; not current validated workflows.
- Explained Celsius/Kelvin versus emissivity. Proposal for consolidated review: one LST calculation plus unit selector, with advanced emissivity outputs separately labeled; current NDVI emissivity gate remains. [EN research](documentation/en/INDICES_AND_TEMPERATURE_REVIEW.md), [AR research](documentation/ar/INDICES_AND_TEMPERATURE_REVIEW.md).
- Only planning/reference files changed for r3. No current tool behavior, package or sensor support changed; native runtime checks NOT RUN for this discussion.

## Implemented repair scope (r1 only)

- Sole implementation package: `atiaf_core` (I). The previous I facade/Y implementation split is removed. Old Y imports/CLI names require migration. ArcGIS and QGIS use thin native adapters and shared workflow preflight.
- ArcGIS Pro: `ArcGIS Pro Tools/ATIAF.pyt` in English; `ATIAF_AR.pyt` in Arabic. All six tools expose named initially unchecked calculations, sensor first, output folder last, search, optional QA/mosaic/AOI/CRS/map options and expert JSON mapping.
- QGIS: self-contained plugin ZIP; six Processing algorithms, locale-based labels and initially empty native multiple selection. Required science/input conditions are validated, not inferred from catalog presence.
- Actual CRS application, polygon clipping, sensor mismatch/empty-selection rejection, QA/saturation/NoData and raw DN validity masks, potential double-scaling guard, unique immutable raster filenames, explicit expert provenance, cancellation of windowed processing and separate EN/AR run reports.
- Spectral products use `Results/Spectral_Indices/<category>/<method>/`. Work/Results are reused; repeated runs currently recompute and preserve earlier outputs rather than claim unverified cache hits.
- `documentation/` replaces docs. Specifications, decisions and roadmaps are in `documentation/project/`; root AGENTS.md and this state remain recovery entry points. Numbered reports/plans/journal history preserved.
- Supplied original logo above supplied banner in both READMEs and HTML indexes; offline search/filter/language portal and generated EN/AR help. Original PNGs preserved; integrated hashes match.
- Environment helpers diagnose without automatic package installation. CI is configured for pinned headless checks, but remote CI has NOT RUN.

## Observed evidence (r1 code; not r2 acceptance)

- Standalone Python 3.14.7: **124 tests PASS** on current code.
- QGIS 4.2.3 / Python 3.12.15 / GDAL 3.13.3: **8 native tests PASS**, including all six tools on synthetic scenes, output CRS/readback, empty selection rejection and event-queued layer registration.
- ArcGIS Pro 3.6 build 59527: **6 native tests PASS on final code**, including all six tools, Arabic native parameter labels and the corrected Spectral_Indices output folder. Raw final output is in Reports/evidence/PLAN-0015/native_arcgis_final.txt.
- Wheel and relocated self-contained QGIS ZIP source identity/import/native synthetic NDVI smoke checks PASS on the refreshed build.
- Offline browser: desktop 1400 × 1100 and mobile 390 × 844 PASS for image loading/order, 42 catalog cards, search, filter, language directions and width; screenshot evidence in Reports/evidence/PLAN-0015.
- Package structure/JSON/link checks and dependency/import/syntax diagnostics PASS. These are not native/real-product science proof. Two immutable report-0009 links use explicitly recorded old-path migrations.
- Approved skills checkout verified at `2a0a9a23618e40218484ec8ae5848a481df51f1a`, MIT. Canonical journal and final handoff are maintained under .agent-development-log; verify its latest record count on recovery. No upstream skill source changes.

## Remaining acceptance / limitations

- Real downloaded L1/L2 product validation and a clean-machine installation: **NOT RUN**. Native tests use synthetic products, not real acquisitions.
- Full interactive GIS dialog, Arabic shaping/RTL, Pro map rendering and user click-through acceptance: incomplete. Physical Escape stopped Computer Use; no further live desktop automation was performed afterward.
- Thematic/conditional QGIS native UI is implemented and one Arabic panel rendered/inspected; all-six full bilingual user journeys remain unverified. Incompatible calculations are rejected with reasons; rows are not dynamically greyed from incomplete inputs. Pro full visual/RTL click-through is not observed.
- TVDI, SUHI, historical drought models, old emissivity-only branch, Tasseled Cap/Gao and ASTER TIR remain gated. The new explicit local NDVI/RTE path has numeric/native synthetic evidence only. SAR/hyperspectral code presence is not a validated native product workflow; AWEI/MTCI/IBI/MIRBI remain candidates requiring further review.
- Temporal comparison currently accepts one scene per epoch; same sensor/level and ordered dates. Mosaic requires matching sensor, level and acquisition day. Cross-sensor/date harmonization is not silently assumed.
- Full CRS area-of-use/suitability, datum-operation provenance/accuracy, all large-scene/resource limits, concurrent report-index updates and comprehensive crash/resume need further verification. Some derived analyses remain array-based with a size guard.
- Pro emitted a GDAL CF-1 standard-name database warning; tested GeoTIFF workflows passed, CF-1 lookup remains unverified. SciPy is absent from standalone Python; optional paths are not claimed installed.
- Old processing models using replaced parameter names need reconfiguration. Refresh/reopen old tool dialogs after updating.

## Exact next step

Resume from report 0021 and r6 DoneProof. Execute full actual six-tool English/Arabic dialog journeys and real L1/L2 product/independent field or local threshold calibration, followed by clean-machine acceptance. Use the current QGIS ZIP and matching Pro checkout; do not reuse old dist packages. Additional scientific variants/product readers/SAR require their own reviewed inputs and evidence. Keep PLAN-0015 Active until retained checks pass; never treat the new fixture counts as real-product or stable-release proof. See [the plan](Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md), [Arabic quick start](documentation/ar/QUICK_START.md), [English guide](documentation/en/QUICK_START.md), and [measured environments](development_resources/tested_environments.json).

## الحالة بالعربية

المحرك موحّد بحرف I، والأدوات الست لها حسابات صريحة وترتيب المعاملات المصحح. التوثيق والشعار والبانر منظّمة محليًا. الاختبارات الصناعية والأصلية المذكورة أعلاه نجحت، لكنها لا تثبت صلاحية كل منتج فضائي أو التثبيت في جهاز نظيف. فحص ArcGIS النهائي نجح وسُجل في التقرير 0016. الخطة ما زالت نشطة لفحوص الواجهة والمرئيات الحقيقية والتثبيت النظيف؛ لا يُعلن إصدار مستقر.

تحديث المناقشة: الخطة r2 تضم طلب مكان توزيع خاص بـQGIS مرتبط بالبناء والتوثيق، وواجهة تعيين الباندات يدويًا. لم تُنفذ هذه التغييرات بعد؛ النتائج السابقة تخص r1.

تحديث r3: سُجل طلب إزالة البحث من واجهات الحسابات وتصنيف المؤشرات داخل البرنامجين. حُفظ بحث ثنائي اللغة عن مرشحات إضافية وشرح الحرارة والانبعاثية ومقترح تبسيط الواجهة. لا توجد مؤشرات أو مستشعرات جديدة منفذة أو معتمدة بهذا البحث.

تحديث r4: استخدام NDVI ضمن اشتقاق حرارة السطح متطلب مؤكد، لكنه غير منفذ كمسار عامل؛ إخراج الانبعاثية وحده لا يحققه. Sentinel-1 مفيد وموجود له كود أولي، لكنه لا يملك أداة رادار مكتملة ومتحققًا منها داخل المشروع.

تحديث r5: سُجل تفسير مخرجات كل مؤشر ومداه ومعنى فئاته ومصدر التصنيف وحدود صلاحيته محليًا، مع ضبط الحدود اختياريًا وتوثيقها. التغطية الحالية ناقصة؛ لم تُنفذ الجداول الشاملة أو واجهات التصنيف بعد.

الحالة الحالية r6 تتجاوز ملاحظات التخطيط السابقة: نُفذ الإدخال اليدوي والمجموعات دون بحث وخيارات الحرارة ومسار NDVI المحلي المشروط، وتفسير النتائج والتصنيف المحلي الاختياري، وحزمة QGIS الخاصة به. نجح 140 اختبارًا عامًا و11 داخل QGIS و8 داخل Pro وفحص الحزم والتوثيق. هذه بيانات صناعية؛ المرئيات الحقيقية والتثبيت النظيف والقبول التفاعلي الكامل لم تُنفذ. الخطة نشطة جزئيًا ولا يُعلن إصدار مستقر أو دعم Sentinel-1 كامل.

تحديث النشر PLAN-0016: اكتمل تجهيز README باللغتين وIndex بالشعار ثم البانر ورفع المشروع إلى GitHub. نجح الفحص البعيد الكامل و141 اختبارًا وبناء حزم QGIS وPython، ونشر الصفحة تلقائيًا عبر إعداد Pages الموجود. تقرير التسليم 0024؛ خطة النشر مكتملة، وتبقى PLAN-0015 نشطة للتحقق العلمي والقبول الأصلي والتثبيت النظيف.
