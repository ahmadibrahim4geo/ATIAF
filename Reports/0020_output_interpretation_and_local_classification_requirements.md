# Report 0020 — Output interpretation and local classification requirements

- Date: 2026-11-15. Plan: [PLAN-0015 r5](../Development_Plans/Active/PLAN-0015_usability_branding_and_recovery.md), Active / partial.
- Status: **documentation audit / requirements recorded; classification implementation NOT STARTED**.
- Git: main, baseline 08954fc1add9b4bdb0b2b5645cebde35cba21235. Existing local work retained; no commit/push/publication.

## Request and source findings

User requests per-index documentation of the output, range meaning and class interpretation, whether a classification has international recognition, limitations for their study area, and local threshold adjustment while preserving accurate scientific labels. This joins the consolidated tool-repair scope.

Read EN/AR INDICATORS_CATALOG and SCIENTIFIC_METHODS, relevant specification requirements, report 0019, and inspected `tools/build_documentation.py` / `atiaf_core/reporting.py`. Catalogs currently list formulas, band roles and citations but not complete interpretation/classification tables. SCIENTIFIC_METHODS claims detailed interpretation tables in the catalog; this overstatement is a recorded documentation defect, not proof that such tables exist. No complete interpretation/preset pipeline was established by static inspection.

## Research and r5 scope

Official NASA/USGS educational NDVI references provide contextual ranges, not evidence of a universally applicable weak/moderate/strong international standard. No such standard was established by this targeted review. Formal standards require an issuer/version/scope; paper-specific classes, educational examples and user-calibrated schemes must be labeled separately. Low greenness is not sufficient to diagnose plant disease; negative NDVI does not uniquely classify water. Different methods have different ranges/units.

The plan now requires complete EN/AR output interpretation, qualified sourced class tables, optional local adjustments with accurate labels, preserved continuous values, and reports/legends recording source/version/original/effective thresholds and validation basis. Exact boundary/mask tests, generator coverage and actual native controls/readback are acceptance items, not already passed. Canonical metadata/generator changes must prevent rebuilding docs from erasing these explanations.

Added matching [English requirements note](../documentation/en/OUTPUT_INTERPRETATION_REQUIREMENTS.md) and [Arabic requirements note](../documentation/ar/OUTPUT_INTERPRETATION_REQUIREMENTS.md), including NDVI examples, source URLs and access limits. These are requirements/reference notes, not complete implemented per-index documentation. Updated active plan r5, both indexes, PROJECT_STATE and journal revision #0038 (ref #0036).

## Verification / limitations

- `Get-Location`: authorized project root D:/My Software/ATIAF. `git status --short | Measure-Object`: existing local changes retained; no reset/move/deletion.
- `rg -n -i 'threshold|interpret|classification|range|NDVI|تصنيف|تفسير|حدود|كثيف|قوي'` on the EN/AR catalog/science/specification files and reporting module, plus direct source reads, established the documentation gap. Static audit only.
- `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe .agent_resources/GIS-Development-Skills/scripts/development_journal.py verify --project .`: **37 valid records before this batch**. Request revision #0038 recorded.
- `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe tools/validate_package.py`: **exit 0 / STRUCTURAL VALIDATION PASS** after r5 notes/plan edits. Final new report/index link check is recorded in the journal handoff.
- Runtime, scientific classification boundary tests, native ArcGIS/QGIS controls, real local calibration and generated all-index documentation: **NOT RUN / not implemented for r5**. Earlier r1 tests are not evidence for this new scope. No GIS host used in this batch.
- Scientific QA: checked NASA educational guidance and caveats; did not invent a global NDVI classification or an executable preset. USGS direct-open was challenge-blocked; official search-index text was available. No external code/data import, license change or new dependency; original MIT policy retained.

## Handoff / ملخص عربي

Keep PLAN-0015 Active. Include per-index interpretation and defensible locally adjustable classification in the consolidated implementation. Review sources per method, implement canonical metadata/generator/report integration and run fresh acceptance evidence. Do not claim the new notes provide complete indicator coverage or a validated universal/local classification.

الموجود حاليًا شرح للمعادلات والباندات والمراجع، لكنه لا يغطي تفسير وتصنيف النتائج بالشكل المطلوب. سُجل بند شامل للشرح العربي والإنجليزي، وبيان مصدر وحدود التصنيف وقابلية ملاءمته محليًا مع المسميات الدقيقة والتوثيق. لم تُنفذ واجهة التصنيف أو تغطية كل المؤشرات بعد.
