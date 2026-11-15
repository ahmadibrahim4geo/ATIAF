# Dependency and licensing strategy
- **Core (future):** Python pure functions; NumPy/xarray as suited to raster arrays; GDAL/Rasterio compatible with host GIS environments, explicit version pins and packaging test. Do not mix binary GDAL/PROJ wheel/Conda builds blindly with ArcGIS Pro's Python or QGIS's Python.
- **ArcGIS Pro adapter:** host ArcPy; user's legally installed ArcGIS Pro, plus Spatial Analyst license only where actual tool operations require it. Do not bundle ArcGIS proprietary binaries or claim all functionality is available without the appropriate host license.
- **QGIS adapter:** PyQGIS and QGIS Processing, provided by independently installed QGIS. Prefer built-in raster stack and standalone pure-Python core where possible.
- **Scientific formula catalog:** Awesome Spectral Indices MIT source, pinned SHA/schema + upstream license notice; `spyndex` MIT optional if the host environment accepts it. The catalog v1 schema is experimental as of November 2026. Validate each accepted method.
- **Geospatial science:** GDAL/PROJ, EPSG/PROJ database native host APIs; source CRS selected with host and output projected metre based. Align grids and physical units before calculations.
- **Optional external atmospheric correction:** ESA Sen2Cor/SNAP only when user explicitly has and chooses those dependencies and appropriate L1 files. L2 not double-corrected. FLAASH is not bundled or mandatory.
- **EnMAP-Box:** GPL ecosystem; may use as an independently installed external tool/reference but do not copy GPL implementation into MIT code without a documented compatibility strategy.
- **Remote platforms:** IDB API not required at runtime; available for individual opt-in lookup only if credentials and current terms permit. No bundled API keys. Do not include complete IDB database.
- **Testing and docs:** pytest and built-in Python standard library for structural tests; report native GIS acceptance separately. CHM build on Windows optional; markdown/HTML remains portable fallback.
- **No lockfile yet:** runtime versions must be measured on the first development host. Agent should record exact versions and checksums in a newly versioned lock/compatibility file when actual environment is known; never claim a fabricated compatible matrix.

## PLAN-0015 observed environment correction

Measured versions and limits are in tested_environments.json. The standalone test constraints are developer-only, not instructions to mix binary stacks in Pro/QGIS. Native Pro 3.6 and QGIS 4.2.3 synthetic workflows were observed separately. QGIS Python is 3.12.15 on this session, correcting older report claims of 3.12.9. SciPy is absent in standalone Python; optional paths are not asserted as installed. No packages were installed into either GIS host. The helpers now diagnose without pip installation. Clean-machine installation and real products remain NOT RUN.
