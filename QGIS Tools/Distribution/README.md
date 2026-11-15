# QGIS installables / حزم تثبيت QGIS

Run `python tools/build_qgis_plugin.py` from ATIAF ROOT. Current development output: `ATIAF-QGIS-1.0.2.dev1.zip`. Install with QGIS Plugins → Manage and Install Plugins → Install from ZIP, then enable ATIAF and reopen tool dialogs. The archive bundles plugin source, shared core and bilingual HTML help, but no imagery or GIS runtime. It refuses to overwrite an existing package; preserve previous builds or choose a new output filename.

المصدر في المجلد المجاور atiaf، بينما هذا المجلد لحزم التثبيت. شغّل أمر البناء من جذر ATIAF ثم ثبّت ZIP من مدير إضافات QGIS وفعّل الإضافة. الحزمة تتضمن المحرك المشترك والمساعدة العربية والإنجليزية، ولا تتضمن المرئيات أو برنامج QGIS. الحزم القديمة محفوظة؛ بناء حزمة لا يعني اعتمادها علميًا بمرئيات حقيقية.

Root `dist/` contains separate core wheels and historical builds/test artifacts. Developer scripts under `tools/` maintain/build/test the project; they are not user geoprocessing tools.
