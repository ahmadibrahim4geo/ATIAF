# Installation

Development build **1.0.2.dev1**. Use [project state](../../PROJECT_STATE.md) for measured versions and remaining checks. Import success is not release acceptance.

## ArcGIS Pro

Keep `ArcGIS Pro Tools/` beside `atiaf_core/`. Add a folder connection to the whole repository in Catalog; open `ATIAF.pyt` for English or `ATIAF_AR.pyt` for Arabic. Close the old tool dialog and Refresh/restart Pro after updates, since open dialogs can retain old parameters. Do not copy a `.pyt` alone away from `atiaf_arcgis.py` and the core.

Required scientific libraries: NumPy, Rasterio, Shapely and pyproj in the **active Pro Python environment**. Clone the managed environment before changing packages and use host-compatible GDAL/PROJ builds. ATIAF helpers are now read-only diagnostics, not automatic pip installers:

```text
"<ArcGIS Pro install>/bin/Python/scripts/propy.bat" tools/setup_arcgis_pro_env.py
```

A missing dependency must produce a clear error while calculation controls remain visible. Repair the compatible cloned environment using Pro's environment manager, then restart and recheck. ATIAF does not alter your base installation.

## QGIS

Run `python tools/build_qgis_plugin.py`. Install `QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev1.zip` from Plugins → Manage and Install Plugins → Install from ZIP. Enable ATIAF; its six algorithms appear in Processing Toolbox. The ZIP includes the MIT shared core and JSON definitions, not imagery or third-party source. Scientific libraries must be available in QGIS's own Python; never mix host environments.

Tool language follows QGIS locale. Select calculation checkboxes under thematic groups; the manual toggle reveals local band fields. Incompatible selections are rejected with reasons; calculation search is removed. The new parameter set requires updating saved models (the old INDICES enum remains hidden for compatible scripted selection). Restart/refresh the plugin and reopen old dialogs after updating.

## Maintenance

`tools/validate_package.py` checks files, JSON and links. `tools/verify_installation.py` checks imports/syntax, not native or real-product acceptance. `tools/bootstrap_skills.py` verifies development guidance, not a user runtime dependency. [Quick start](QUICK_START.md).
