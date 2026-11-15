# Report 0017 — Manual input and QGIS distribution requirements

- Date: 2026-11-15. Plan: [PLAN-0015 r2](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md).
- Status: **REQUIREMENTS RECORDED — implementation not started for r2**.
- Git: main; existing local edits preserved. No commit, move, runtime-code edit, build or publication in this discussion batch.

## User clarifications preserved

The user wants to discuss all modifications before implementation. The manual mode is an original requirement, not a future optional enhancement to a JSON-only UI: users with incomplete scene/header metadata choose their known sensor and only the local bands they possess or need. Native band-file fields appear when the optional mode is enabled in both ArcGIS Pro and QGIS. Scientific prerequisites still require real level/unit/calibration evidence. JSON may save/import the user-created mapping but must not be mandatory for normal manual selection.

Input label proposal: `Input Data Folder` / `مجلد بيانات الإدخال`, with single/multiple scene explanation in help.

The latest clarification requires QGIS packaging to be clearly QGIS-specific and linked to the plan/project. Proposed structure for consolidated review:

```text
QGIS Tools/
  atiaf/             # current source
  Distribution/      # proposed QGIS installable ZIP location
atiaf_core/          # shared implementation remains outside host-specific packaging source
```

The package builder, source-identity/relocated-native tests, CI, README and EN/AR installation paths must migrate together when implemented. Core wheel/browser/test outputs must not be confused with QGIS installables. Retain old builds. The suggested general tools-to-developer_tools rename remains a proposal, not an approved execution.

## Files updated

- Active plan: r2 revision history and requested behavior/acceptance added without deleting r1 requirements.
- New report 0017, both indexes, current state and linked canonical journal revision/handoff.
- Current adapter code, package builder and existing ZIP location remain unchanged.

## Inspection and evidence

- Read the manual-mapping requirements in both specification languages: English section 5 and Arabic section 5.
- Inspected `QGIS Tools/README.md`, `tools/README.md` and `tools/build_qgis_plugin.py`. Current builder defaults to `dist/ATIAF-QGIS-1.0.1.dev0.zip` and includes plugin source plus the shared core. That current behavior is not the proposed r2 layout.
- Verified canonical journal before this batch: 32 records valid.
- Structural/link validation and journal integrity are the applicable closure checks. Runtime tests are **NOT RUN for r2**, since runtime code and folders were not changed. Prior 124/8/6 test counts belong to r1 only.
- No scientific algorithm, external dependency, source download or license change. Original MIT policy and source/input protection remain.

## Next action

Continue the user's consolidated requirements discussion, then implement the agreed r2 scope in one coordinated batch. Do not mark the proposed folder layout or native manual file UI implemented based on this planning record. Keep PLAN-0015 Active.

## ملخص عربي

سُجل طلب تنظيم حزم QGIS في مكان تابع له بوضوح وربط مساره بالخطة والبناء والاختبارات والتوثيق، مع توضيح الفرق بين مصدر الإضافة وحزمة تثبيتها وبرامج صيانة المطور. سُجل كذلك التعيين اليدوي المباشر للباندات والاسم الموحد لمجلد الإدخال. المسار داخل QGIS Tools/Distribution مقترح للمناقشة، ولم يحدث نقل فعلي أو تعديل لواجهة الأدوات في هذه الدفعة.
