# Developer utilities / برامج صيانة المشروع

These scripts maintain/build/test ATIAF. They are not satellite analysis tools and are not prerequisite preparation steps for users. هذه برامج تجهيز وصيانة وليست أدوات التحليل التي يفتحها المستخدم داخل GIS.

- `validate_package.py`: files, JSON, Markdown/HTML links and immutable historical path migrations.
- `verify_installation.py`: dependency/import/syntax diagnostics; no native success claim.
- `setup_arcgis_pro_env.py`: read-only dependency check in the active Pro environment, no installation.
- `build_documentation.py`: offline HTML portal and EN/AR help generation.
- `build_qgis_plugin.py`: self-contained plugin ZIP, no imagery or external source.
- `bootstrap_skills.py`: approved development guidance checkout SHA verification; no remote scripts executed.
- `sync_index_catalog.py`: optional developer catalog intake; requires pinned commit/license/science review before enabling entries. No catalog downloaded in this repair.

[Installation](../documentation/en/INSTALLATION.md) · [التثبيت](../documentation/ar/INSTALLATION.md).
