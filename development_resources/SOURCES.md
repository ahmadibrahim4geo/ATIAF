# Official portals, scientific references and tools
**Free-first reference map.** Data acquisition is user-directed OUTSIDE ATIAF; ATIAF processes local unpacked products. A free account at the vendor portal is acceptable. This does not imply every provider/product allows unrestricted redistribution.

## Download portals / official products
| Mission | Portal | Public access summary |
|---|---|---|
| Landsat (1–9) | https://earthexplorer.usgs.gov/ | USGS free data; account commonly needed to download |
| Landsat C2 product guide | https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products | USGS source of SR/ST scale and QA guide |
| Landsat quality | https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands | QA_PIXEL / saturation interpretation |
| Sentinel-2, Sentinel-1, Sentinel-3 | https://dataspace.copernicus.eu/ | Copernicus free open datasets; Browser download currently free login |
| Sentinel-2 product definitions | https://sentinels.copernicus.eu/sentinel-data-access/sentinel-products/sentinel-2-data-products | L1C/L2A source and product changes |
| NASA ASTER/MODIS/VIIRS/EMIT/ECOSTRESS | https://search.earthdata.nasa.gov/ | NASA free user account for downloads; ASTER higher-level some on demand |
| ASTER detailed product types | https://asterweb.jpl.nasa.gov/data_products.asp | AST_05 / AST_07 / AST_08 / AST_09T |
| ASTER TIR 2026 termination | https://science.nasa.gov/blogs/science-news/2026/02/12/terra-adjusts-instrument-operations-to-extend-mission-life/ | official mission date and VNIR continuation |
| EnMAP | https://www.enmap.org/data_access/ | DLR access/registration/license + archived L1B/L1C/L2A |
| PRISMA | https://www.asi.it/en/earth-science/prisma/ | ASI product access and use policy |
| SAR (Sentinel-1/ALOS) | https://search.asf.alaska.edu/ | ASF Vertex; free NASA Earthdata login |

## Index databases and methods
| Source | URL | Rules |
|---|---|---|
| Awesome Spectral Indices (MIT, v1 experimental) | https://github.com/awesome-spectral-indices/awesome-spectral-indices | candidate offline catalog after pin/validation/copyright attribution |
| Spyndex (MIT) | https://github.com/awesome-spectral-indices/spyndex | computation/validation candidate |
| Index DataBase | https://www.indexdatabase.de/db/i.php | reference and optional authenticated API; **no bulk API-data redistribution** under current restrictions |
| IDB API request terms | https://www.indexdatabase.de/info/apirequest.php | respect rate limit 1/s, 2000/day, >=24h cache and redistribution terms |
| NASA HLS | https://hls.gsfc.nasa.gov/algorithms/ | Landsat/Sentinel harmonization methodological reference |
| Tasseled Cap from GRASS | https://grass.osgeo.org/grass-stable/manuals/i.tasscap.html | sensor-specific coefficients and docs |
| ASTER geology publication | https://doi.org/10.11440/rssj1981.22.50 | geological ASTER formulas—verify product semantics |

## Software/platform API docs
- ArcGIS Pro Python Toolbox: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-quick-tour-of-python-toolboxes.htm
- ArcGIS Pro parameter CRS: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/defining-parameter-data-types-in-a-python-toolbox.htm
- QGIS processing manual: https://docs.qgis.org/latest/en/docs/user_manual/processing/scripts.html
- QGIS `QgsProcessingParameterCrs`: https://api.qgis.org/api/classQgsProcessingParameterCrs.html
- GDAL: https://gdal.org/ ; Rasterio: https://rasterio.readthedocs.io/ ; PROJ: https://proj.org/
- ESA Sen2Cor (optional L1C->L2A, not bundled): https://step.esa.int/main/snap-supported-plugins/sen2cor/
- EnMAP-Box methods/QGIS: https://enmap-box.readthedocs.io/ ; license review before copying code.

## Provenance policy
Every scientific method in ATIAF must cite original peer-reviewed research where accessible; this registry is a navigation list, not authoritative mathematical proof of formula variants. For external sources record `url`, `publisher`, `access_date`, `source_version_or_commit`, `license`, `data_redistribution_allowed`, and `role` (runtime dependency vs reference vs optional user portal). When website terms are ambiguous, do not download and redistribute a bulk dataset.
