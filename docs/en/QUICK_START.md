# ATIAF Quick Start — planned user experience
1. Download a suitable free scientific satellite product from an official portal (see `SENSORS_AND_DOWNLOADS.md`). A free portal login is acceptable; the tool itself must not require credentials.
2. Unpack the complete scene, keeping original band files, metadata, and QA layers. For multiple scenes, put them in distinct subfolders under one parent.
3. In ArcGIS Pro or QGIS, open the intended independent ATIAF tool. Select sensor/product (auto-detection should populate/verify it) and scene/parent folder.
4. Review preprocessing defaults and whether to enable **Mosaic**; enable it only for a compatible set of scenes you mean to analyze jointly. Optional AOI polygon clipping is independent.
5. Select one or more individual compatible indices/calc modes from thematic groups. Unsupported operations show disabled with a clear reason.
6. Select an output projected **metre-based** CRS through the host software CRS picker (prepopulated from source only if already valid); no fixed worldwide UTM default.
7. Last setting **Output Folder** defaults to input; choose another folder only if desired. Optionally enable **Add Results to Map**, with serial loading.
8. Execute. Find additions in `Work/` (cache) and `Results/` (tool-category output, reusable across ATIAF tools). Consult `Results/Reports/index.html` for result paths, formula, true band files/roles, actual metadata values, masks, QA and errors.

**This is the intended workflow, not a working UI in the initial documentation package.**
