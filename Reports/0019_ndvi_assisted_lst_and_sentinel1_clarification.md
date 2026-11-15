# Report 0019 — NDVI-assisted LST and Sentinel-1 clarification

- Date: 2026-11-15. Plan: [PLAN-0015 r4](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md), **Active / partial**.
- Status: discussion/source inspection and references only; no runtime implementation, new sensor support, build or native test.
- Git: main, baseline 08954fc1add9b4bdb0b2b5645cebde35cba21235; existing edits retained, no commit/push/publication.

## User clarification and findings

The user reaffirms optional NDVI participation in temperature derivation, and asks whether Sentinel-1 exists and is useful. Both specifications already distinguish NDVI-based emissivity and official ST, and reserve dedicated SAR workflows. A separate emissivity output does not satisfy the intended NDVI-assisted LST path.

- Current native contract has no external NDVI input. `workflow.py` gates EMISSIVITY_NDVI and invokes Official_L2_ST for temperature. The low-level `temperature/engine.py` emissivity branch returns emissivity only. No complete NDVI-assisted LST derivation is available.
- Future reviewed path: NDVI -> vegetation-cover/emissivity estimate -> appropriate thermal/atmospheric retrieval; not arbitrary addition of NDVI to temperature. Existing/computed local NDVI input choice is a UI proposal. Official L2 ST must not be corrected twice.
- `discovery/sentinel1.py`, scanner integration and SAR array helpers exist, but the explicit sensor choices/native tools do not expose a dedicated SAR workflow. No calibrated end-to-end/real-product/native Sentinel-1 workflow is demonstrated. Preliminary helper docstrings/tests are not proof of scientifically validated radar support.
- Official sources confirm free C-band SAR observations and flood/agriculture/deformation applications. Sentinel-1 cannot directly provide optical NDVI or thermal LST. Conventional InSAR requires phase-preserving compatible SLC inputs, not GRD alone. Quantitative moisture is model-dependent.

## Files and science/license evidence

Active plan r4 preserves r1–r3 and adds NDVI-assisted acceptance and honest SAR scope. Matching [EN](../documentation/en/INDICES_AND_TEMPERATURE_REVIEW.md)/[AR](../documentation/ar/INDICES_AND_TEMPERATURE_REVIEW.md) notes append the clarification and primary references. State/indexes updated; journal revision #0036 links #0034. No runtime file or changelog feature changed.

Read accessible author-hosted Sobrino et al. (2004), DOI 10.1016/j.rse.2004.02.003; official USGS ST-input documentation and Copernicus Sentinel-1 mission/data/application pages. Exact URLs and limitations are in the bilingual notes. A TM5 paper is not automatic validation of another sensor/current algorithm. No source/data vendoring or licensing change; MIT original code policy preserved.

## Commands / observed results

- `git status --short`: local modifications/untracked history remain; no reset or deletion.
- `rg -n -i 'NDVI|emissiv|انبعاث|Sentinel.?1|رادار' documentation/project/PROJECT_SPECIFICATION.md documentation/project/PROJECT_SPECIFICATION_AR.md documentation/project/DECISIONS.md`, plus direct reads of temperature engine, shared workflow/contract, Sentinel-1 parser and SAR router/helpers: confirmed limits above. Static source inspection only.
- Installed Python: `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe`.
- `<Python> .agent_resources/GIS-Development-Skills/scripts/development_journal.py verify --project .`: **35 records valid before this batch**; revision #0036 appended using reviewed helper.
- `<Python> tools/validate_package.py`: exit 0, **STRUCTURAL VALIDATION PASS**, 26 candidate / 19 planned sensor registry entries, 355 Markdown / 55 JSON at the pre-report closure check. Registry counts are not support validation. Final report/index link check follows and is recorded in the journal.
- Native ArcGIS/QGIS, scientific numeric retrieval, real Sentinel-1/thermal products and clean installation: **NOT RUN for r4**. No claim that this discussion implements either feature; previous r1 test results do not prove r4 behavior.

## Handoff / ملخص عربي

Continue consolidated requirements discussion, then implement the agreed optional NDVI-assisted LST path only with reviewed thermal/atmospheric requirements and fresh independent/native evidence. A possible GRD radar phase needs explicit scope before development; InSAR is separate. Keep PLAN-0015 Active.

تأكد أن استخدام NDVI داخل اشتقاق الحرارة متطلب مطلوب لكنه غير متاح كمسار عامل حاليًا؛ خريطة الانبعاثية وحدها لا تكفي. Sentinel-1 موجود ومفيد، والكود الأولي له داخل المشروع لا يعني وجود أداة رادار جاهزة. حُفظ التوضيح بالعربي والإنجليزي دون تغيير الأدوات أو ادعاء نجاح اختبارات جديدة.
