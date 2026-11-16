# Decision Register — ATIAF (2026-11-13)
| ID | Decision | Status |
|---|---|---|
| D-001 | Project Arabic name «أطياف»; acronym **ATIAF**; official expansion **Advanced Thematic Imagery Analysis Framework** (Systematic would spell ASIAF). | Accepted name convention |
| D-002 | One native ArcGIS Pro toolbox containing multiple independent tools; QGIS adapter planned; common `atiaf_core`. | Accepted |
| D-003 | Every tool handles sensor input, processing, mosaic option, optional AOI, selected calculations, output and reporting end-to-end. | Accepted |
| D-004 | Single scene or multi-scene parent folder; preserve per-scene results, and quality-aware mosaic result when enabled. | Accepted |
| D-005 | All tools append to same `Work` / `Results` workspace; skip only verified reusable outputs. No silent delete/overwrite. | Accepted |
| D-006 | Last parameter is output directory; defaults to source folder; user can override; custom single/multiple destination organization as specification. | Accepted |
| D-007 | Native host projected CRS selector; no global EPSG/UTM default; projected metre-based output validation. | Accepted |
| D-008 | Optional expert band mapping; strict evidence for units/scale; missing critical metadata disables invalid calculations. | Accepted |
| D-009 | Add Results to Map optional; serial, host-safe loading, no excessive simultaneous additions. | Accepted |
| D-010 | Fully separate Arabic/English UI, docs, help, errors and reports; scientific acronyms stable. | Accepted |
| D-011 | Per-result reproducible report, formula, exact band files and metadata key/value provenance, log, QA and limitations. | Accepted |
| D-012 | MIT open source for original project; third-party copyright/licenses honored. | Accepted |
| D-013 | Local/free-first processing; image acquisition via linked external free portals, registered user accounts acceptable for download. | Accepted |
| D-014 | Index DataBase (IDB) is reference-only or optional authenticated lookup; no bulk redistribution under current API terms. | Accepted |
| D-015 | Scientific catalog local with MIT-compatible source(s) after pinned release/license audit; original scientific paper adjudicates names/formulas. | Accepted |
| D-016 | `AGENTS.md` and project-local plan/report/journal system mandatory; improve GIS-Development-Skills with reusable learnings, without automatically modifying external repo. | Accepted |
| D-017 | Primary development text/docs in English for efficiency, Arabic parallel documentation mandatory. | Accepted |
| D-018 | Geological/mineral and hyperspectral candidate capabilities included with capability gating; no misleading mineral confirmation. | Accepted |
| D-019 | Sensor and product support is global; native product structure discovery and product version/dates determine compatibility. | Accepted |
| D-020 | No mandatory third-party network access or external atmospheric inputs. Methods that physically require additional data stay gated. | Accepted |

## 2026-11-14 approved repair decisions

- D-021: Canonical implementation `atiaf_core` with I; remove duplicate facade/implementation. Host adapters stay separate and clearly named. Migrate Y imports.
- D-022: `documentation/` replaces docs; specifications/decisions/roadmaps live in `documentation/project/`. Root AGENTS/state remain recovery entry points; numbered history remains immutable.
- D-023: Supplied logo above supplied banner in both READMEs and HTML indexes; local assets; preserve originals.
- D-024: Explicit calculation choices, sensor-first/output-last, actionable science gates and honest evidence levels. Earlier stable claims are superseded.

محرك واحد بحرف I للواجهتين، والتوثيق الكامل في documentation، والحسابات ظاهرة باختيار صريح، وتفصل الأدلة الحقيقية عن الادعاءات السابقة.

## 2026-11-15 consolidated implementation decisions (user: execute)

- D-025: Input label is Input Data Folder / مجلد بيانات الإدخال. Keep scene/multiple-scene discovery. Manual mapping is a separate optional toggle with native local file controls and explicit calibration, not a fictional sensor. Saved JSON import/export is optional.
- D-026: Calculation controls are grouped by theme in both hosts and initially unselected. Remove analysis-dialog calculation search; documentation portal search is a separate feature.
- D-027: Surface Temperature has one explicit LST choice plus Celsius/Kelvin unit. Optional NDVI-assisted derivation uses verified local thermal/atmospheric inputs and documented emissivity assumptions; never add NDVI arbitrarily to temperature or correct official ST twice. Current user-parameterized mixture/RTE implementation has synthetic/native evidence, not field validation.
- D-028: Per-method EN/AR documentation/reports explain meaning, units, theoretical/typical ranges and caveats. Distinguish verified standards, research guidance and local classes. Optional NDVI local classification preserves continuous values and logs effective boundaries/source/basis. No universal weak/moderate/strong NDVI standard is claimed.
- D-029: Current QGIS installables belong under QGIS Tools/Distribution; source remains QGIS Tools/atiaf, core shared at root. Keep earlier archives and verify package/source/help identity. tools/ remains developer maintenance scripts.
- D-030: 1.0.2.dev0 remains a development build. First numerical additions EVI2 2.5/2.4 and unadjusted NIRv; other candidates require further scientific/product validation. Preliminary Sentinel-1 helpers are not a complete native radar tool. No publication or upstream skill changes authorized by this batch.

اعتمد المستخدم التنفيذ: اسم الإدخال موحّد، والتعيين اليدوي خيار مستقل، والحسابات في مجموعات دون بحث. الحرارة باختيار واحد ووحدة إخراج مع مسار NDVI المحلي عند اكتمال مدخلاته. تفسير النتائج والفئات موثق باللغتين مع ضبط محلي اختياري لا يغيّر القيم الأصلية أو يدعي معيارًا عالميًا. توزيع QGIS في مكان تابع له، والدعم الجديد يظل مقيدًا بمستوى أدلته الفعلية.

## 2026-11-15 Geological Color Composites execution

- D-031: User authorizes PLAN-0018 from the supplied Geological Color Composites plan. Add a seventh independent native tool in the existing toolbox/provider, sharing core logic, with initially unselected Direct RGB and Ratio RGB. Display/preview remain separate from continuous analytical values; no automatic classification or confirmed rock labels. Preserve all original acceptance and source text. Exact-band/calibration evidence, ASTER date gates, explicit TOA/experimental choices and separate EN/AR help remain mandatory. Real L1T numerical evidence is not field validation or blanket sensor support; local 1.0.3.dev1 is not publication or stable-release authorization.

اعتمد المستخدم تنفيذ التراكيب اللونية الجيولوجية على نمط الأدوات القائمة. يضاف مدخل مستقل للطريقتين بمحرك مشترك، دون تصنيف أو أسماء صخرية مؤكدة، مع فصل العرض والمعاينة عن القيم التحليلية. تبقى المعايرة والباندات والتواريخ والتوثيق والقبول الفعلي شروطًا مستقلة؛ الاختبار الحقيقي المتاح لا يعمم الدعم ولا يأذن بالنشر.

## 2026-11-16 Legacy imagery audit and supplied-plan relocation

- D-032: The explicit move instruction supersedes copy-and-leave-root. Relocate supplied plans into stable numbered lifecycle paths before implementation; retain source filename/path/title/SHA and optional pristine reference only in Source_Archive. No root/general duplicate unless expressly requested. Partials stay Active; verify integrity/status/index links at handoff. EN/AR requirements agree.
- D-033: PLAN-0019 independently audits legacy imagery/results. Retain CRC1 equation/order unless evidence proves a defect. Shared metadata/calibration/QA fixes and clearer outputs/display/interpretation are authorized; explicit TOA differs from SR. Fixture/native evidence cannot certify missing products or mineral classes. Local 1.0.4.dev0 is development only; no publication, forced download or upstream skill edit.

نقل الخطة يحفظ ملف عمل مرقم داخل مجلد الخطط، ولا يترك نسخة توهم بأنها لم تنفذ. لا يبرر التدقيق تبديل المعادلات دون دليل، ولا إغلاق الخطة قبل التحقق من جميع بنودها.
