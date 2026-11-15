# ATIAF — Current implementation and evidence

Snapshot: 2026-11-15. Repository: `D:/My Software/ATIAF`, branch `main`, baseline commit `08954fc1add9b4bdb0b2b5645cebde35cba21235`. Approved implementation/presentation published to https://github.com/ahmadibrahim4geo/ATIAF; remote main verified at 14d4c95. Follow-up portability/report changes await normal push; final hosted acceptance pending.

## Current work

**PLAN-0016 r1 is Active: project published; final hosted checks pending.** Current presentation/package snapshot is **1.0.2.dev1**. Professional EN/AR README/Index, logo/banner and project/community/citation files are published. Existing Pages configuration automatically deployed https://ahmadibrahim4geo.github.io/ATIAF/ (HTTP 200). Fresh indexed source passed 141 tests, documentation/links/JSON and package identity. Hosted checks exposed historical local skill links, then Windows short/long TEMP path assertions; fixes documented in [0023](Reports/0023_github_publication_and_clean_runner_portability.md). Hosted rerun/artifact verification pending; PLAN-0015 remains Active/partial.

**PLAN-0015 r6 is ACTIVE / PARTIAL: consolidated implementation delivered locally with bounded native/synthetic evidence.** Earlier stable-release/all-roadmap-complete claims in reports 0001–0014 remain superseded. Version **1.0.2.dev0 is a development build**, not a validated stable release. Original and added acceptance are retained; real acquisitions, clean installation and full interactive host acceptance remain unverified.

Latest numbered report: [0023 publication/portability](Reports/0023_github_publication_and_clean_runner_portability.md). Preparation: [0022](Reports/0022_professional_presentation_and_publication_preparation.md). Consolidated implementation: [0021](Reports/0021_consolidated_tools_interpretation_and_native_evidence.md). Prior snapshots: [0020](Reports/0020_output_interpretation_and_local_classification_requirements.md), [0019](Reports/0019_ndvi_assisted_lst_and_sentinel1_clarification.md), [0018](Reports/0018_indices_research_and_temperature_requirements.md), [0017](Reports/0017_manual_input_and_qgis_distribution_requirements.md). r1 evidence: [0016](Reports/0016_usability_repair_and_verified_handoff.md); audit: [0015](Reports/0015_recovery_audit.md).

## Current r6 implementation and observed checks

- Input Data Folder / مجلد بيانات الإدخال. Separate manual toggle in both hosts with native file controls, known sensor, explicit platform/date/calibration/provenance, only available/required bands, optional saved JSON import and per-run mapping export. Current manual profiles Landsat C2 L2 and Sentinel-2 L2A. No mandatory header/JSON; missing calibration/QA is not guessed.
- Grouped initially unchecked calculations; calculation search removed. QGIS native panel has conditional manual/retrieval fields and RTL, Pro native categories/enabled parameters. Output remains last. Hidden QGIS INDICES retains compatible saved-model selection; old models/dialog caches require review/reopen.
- One LST choice and Celsius/Kelvin. Official ST default; optional single-scene local NDVI/RTE retrieval with compatible NDVI or red/NIR, calibrated thermal radiance, explicit band Planck/atmosphere/emissivity/threshold inputs and provenance. User-parameterized linear mixture omits cavity term and excludes negative NDVI; no full TM5/field-accuracy claim or extra correction of official ST.
- Per-method EN/AR interpretation metadata covers 45 catalog entries, including legacy/gated variants; generated Markdown/HTML, portal and reports show meaning/units/ranges/caveats. Optional local NDVI classes preserve continuous data, save separate class raster/legend/report and log original/effective boundaries/local basis. No international class standard claimed.
- EVI2 (gain 2.5/red 2.4) and unadjusted NIRv numerically implemented and checked on synthetic inputs in both native hosts. Other research candidates are not promoted to supported calculations.
- Fresh evidence: **140 headless tests PASS; 11 native QGIS tests PASS; 8 native Pro tests PASS**. Actual Arabic QGIS parameter panel rendered/inspected. Full six-tool Pro/QGIS execution remains synthetic. Byte identity of wheel/core/adapter/bundled help, isolated wheel and relocated QGIS execution PASS. Offline desktop/mobile portal checks PASS with 45 cards. Structure/link/JSON checks PASS. [Raw/structured evidence](Reports/evidence/PLAN-0015/r6/observations.json), [partial DoneProof with 21 retained criteria](Reports/evidence/PLAN-0015/r6/doneproof_r6.json).
- Current QGIS ZIP: `QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev0.zip`; separate core wheel: `dist/atiaf-1.0.2.dev0-py3-none-any.whl`. Prior dist packages/intermediate r6 archives preserved. Builder/test/CI/docs use the QGIS-owned path. No live host installation, commit/push/publication or host dependency install.
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
