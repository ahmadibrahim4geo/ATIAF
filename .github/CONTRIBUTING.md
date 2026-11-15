# Contributing to ATIAF

Start with the [project state](../PROJECT_STATE.md), [English specification](../documentation/project/PROJECT_SPECIFICATION.md), [Arabic specification](../documentation/project/PROJECT_SPECIFICATION_AR.md) and [agent contract](../AGENTS.md). Work incrementally; preserve numbered plans/reports and prior outputs.

1. Explain the concrete user problem and expected behavior in an issue or pull request. Keep proposed, implemented and validated support distinct.
2. Keep scientific calculations in atiaf_core and host-specific code in the thin Pro/QGIS adapters. Avoid mandatory online services and any change to original imagery.
3. Cite original research; verify formula variant, wavelengths, units, scaling, QA/NoData, product constraints and third-party licensing before integration. Never bulk-redistribute Index DataBase records.
4. Update English and Arabic help, interpretation, examples and provenance together. Do not call a locally chosen class scheme an international standard.
5. Run `python tools/build_documentation.py`, `python tools/validate_package.py` and `python -m unittest discover tests` in a compatible developer environment. Native host checks are separate and must identify actual host/version/fixture scope. Do not install packages blindly into vendor GIS environments.
6. Include observed validation and remaining NOT RUN checks in your PR. Do not commit scenes, Work/Results, keys, private paths/data or build caches. Original project contributions must be MIT-compatible.

## المساهمة بالعربية

ابدأ بحالة المشروع والمواصفات باللغتين وعقد التطوير. اربط كل تعديل بمشكلة واضحة، وافصل المحرك عن واجهات البرامج. وثّق المرجع العلمي والمعايرة والجودة وحدود التفسير، وحدّث المساعدة العربية والإنجليزية معًا. سجّل الاختبارات الفعلية وما لم يُنفذ، ولا ترفع المرئيات أو نتائج المستخدم أو المفاتيح أو الكاش. دعم مقترح لا يعني تنفيذًا أو تحققًا علميًا.
