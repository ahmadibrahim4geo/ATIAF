# External repository registry — ATIAF
Source URLs are explicitly retained for future skill improvements. Listing does not grant license to vendor entire repos; check upstream license/commit and chosen components before any integration. Status: reference/target unless exact dependency is implemented and tested.

| Class | Repo | Purpose / use | Integration policy |
|---|---|---|---|
| Skills primary | https://github.com/ahmadibrahim4geo/GIS-Development-Skills | master GIS/ArcGIS/QGIS/remote sensing/agent journal | clone pinned snapshot to `.agent_resources`; source + SHA logged |
| Skills supplemental | https://github.com/VelimirMueller/ai-development-skills | general engineering skill framework | reference selectively, not full injection |
| Skills supplemental | https://github.com/obra/superpowers | planned implementation/testing patterns | inspect first, reference, not full injection |
| Skills geospatial | https://github.com/opengeos/geoai-skills | geospatial AI techniques | reference-only until assessed |
| Catalog primary | https://github.com/awesome-spectral-indices/awesome-spectral-indices | MIT scientific index catalog, DOI/definitions | import pinned validated entries/offline with license notice |
| Catalog computation | https://github.com/awesome-spectral-indices/spyndex | MIT compute/reference formulas | evaluate as optional computation/backend or verification fixture |
| Sensors | https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments | sensor wavelengths/instrument metadata | candidate cross-check; verify correctness/license |
| Raster | https://github.com/OSGeo/gdal | geospatial raster I/O, transform, warp, mosaics | system/library dependency with host binary compatibility check |
| Raster Python | https://github.com/rasterio/rasterio | Python block/windowed raster access | optional shared backend if compatible with host GDAL |
| Coordinates | https://github.com/pyproj4/pyproj | PROJ CRS/transform interfaces | validate host-compatible install, prevent incompatible PROJ binaries |
| GIS Desktop | https://github.com/qgis/QGIS | QGIS source/API reference | QGIS install separate; avoid unnecessary code copying |
| ESA processing | https://github.com/senbox-org/snap-engine | SNAP core reference | separate ESA SNAP optional; check availability/license |
| Hyperspectral examples | https://github.com/nasa/EMIT-Data-Resources | EMIT tutorials/NetCDF geometry | method reference; no need to bundle sample scenes |
| EnMAP | https://github.com/EnMAP-Box/enmap-box | QGIS hyperspectral methods/processing | GPL-related considerations; independent integration rather than copying source |
| Testing | https://github.com/pytest-dev/pytest | pure Python tests | project dev dependency only |
| Catalog parsing | https://github.com/awesome-spectral-indices/eemont | Earth Engine-oriented examples | no mandatory GEE/Google credentials; reference only |

Other official non-GitHub scientific/mission sources are in [`SOURCES.md`](SOURCES.md). Include any new source with URL, purpose, legal rights, date reviewed, verified original version and usage scope.
