# Official portals, scientific references and tools

## NV5 Geospatial / ENVI Spectral Reference — reviewed 2026-11-16

- [NV5 ENVI Spectral Indices Documentation](https://www.nv5geospatialsoftware.com/docs/SpectralIndices.html): Official reference for 120 standardized spectral indices across vegetation, geology, soil, water, fire, and snow.
- [NV5 Alphabetical List of Spectral Indices](https://www.nv5geospatialsoftware.com/docs/AlphabeticalListSpectralIndices.html): Full formula definitions and required wavelength ranges.
- [NV5 Mineral Indices Background](https://www.nv5geospatialsoftware.com/docs/BackgroundMineralIndices.html): Mathematical and geological basis for 31 mineral and rock alteration indices (Alunite ALUI, Calcite CALI, Carbonates CARI, Clay CLAI/CLAY, Dolomite DOLI, Ferric Iron Alteration FEAI, Ferrous Iron FEI, Ferrous Silicates FESI, Laterite LATI, Hydroxyl OHI, Muscovite MUSI, Phyllic PHAI, Propylitic PRAI, Silica SIDI).
- [NV5 Vegetation Indices Background](https://www.nv5geospatialsoftware.com/docs/BackgroundVegetationIndices.html): Formulations for greenness, canopy water, leaf pigments, and light use efficiency.
- [NV5 Burn Indices Background](https://www.nv5geospatialsoftware.com/docs/BackgroundBurnIndices.html): Formulations for burn area index and fire severity.
- [NV5 Spectral Libraries Guide](https://www.nv5geospatialsoftware.com/docs/SpectralLibraries.html): Documentation of public-domain laboratory spectral libraries embedded in ENVI.
- [USGS Spectral Library Version 7 Data](https://www.usgs.gov/data/usgs-spectral-library-version-7-data): Public-domain laboratory reflectance spectra for minerals, rocks, vegetation, and soils.
- [NASA JPL ECOSTRESS Spectral Library](https://speclib.jpl.nasa.gov/download): Relocated ASTER Spectral Library Version 2 with over 6,000 public domain spectral signatures.

*Licensing & clean-room note:* Formulas, physical constants, and wavelength ranges are published scientific facts implemented independently in clean MIT Python code; no proprietary binaries, IDL code, or copyrighted ENVI libraries are vendored into ATIAF.

## PLAN-0018 composite references — reviewed 2026-11-15

- [Duwi primary study](https://www.nature.com/articles/s41598-024-66199-3): exact Landsat 8/9 FCC 7-5-3 and RGB ratio channel order in Figures 3, 10 and 11 checked. Independent arithmetic implementation; no study figures copied and no local rock-class accuracy inferred.
- [USGS Level-1 calibration](https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product) and [QA Tools Guide v1.4](https://landsat.usgs.gov/sites/default/files/documents/landsat_QA_tools_userguide.pdf), section 2.1: metadata-scaled TOA reflectance, solar elevation and pre-Collection Landsat 8 BQA confidence layout. Not Collection 1/2 QA or atmospheric correction. PDF screenshot fetch failed; explicit textual bit descriptions were reviewed.
- [NASA/JPL ASTER SWIR advisory](https://asterweb.jpl.nasa.gov/swir-alert.asp) and [instrument characteristics](https://asterweb.jpl.nasa.gov/content/01_mission/03_instrument/01_Characteristics/default.htm): validity dates and nominal band identities. Real ASTER calibration/product evidence remains pending.
- [USGS Landsat 8 bands](https://www.usgs.gov/landsat-missions/landsat-8) and [Copernicus MSI band definitions](https://s2.pages.eopf.copernicus.eu/msi/s2msi/1.3.0/context.html): approximate reference wavelengths, explicitly distinguished from extracted product metadata and platform-specific response functions.
- [QGIS RGB API](https://api.qgis.org/api/classQgsMultiBandColorRenderer.html) and [Esri Pro 3.6 CIM RGB properties](https://pro.arcgis.com/en/pro-app/3.6/sdk/api-reference/topic4533.html): API reference only; independently authored thin adapters, no GPL or proprietary implementation copied. Installed native tests adjudicate version compatibility.
- [Proposed Fawakheir ASTER source](https://www.sciencedirect.com/science/article/pii/S1464343X09001071): retained from user plan; complete original formula text not independently verified, so preset remains experimental. Other exploratory presets are not promoted by citation proximity.

No reference is a runtime download/dependency. User-provided imagery and derived previews remain local; no new source/asset redistribution or publication is authorized.
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

## 2026-11-15 additional-index research (reference only)

See [English source review](../documentation/en/INDICES_AND_TEMPERATURE_REVIEW.md) and [المراجعة العربية](../documentation/ar/INDICES_AND_TEMPERATURE_REVIEW.md), PLAN-0015 r3. EVI2/NIRv/AWEI/MTCI/IBI/MIRBI are feasibility candidates, not new validated support. Source publishers, original DOIs, product versions and access limitations are listed there. Awesome Spectral Indices definition pages declare MIT; no release/commit was pinned and no code/catalog was imported. Exact version/license audit and original formula reconciliation remain prerequisites for a selective future import. Scientific-paper/data redistribution is not authorized by this review; no Index DataBase records or imagery were vendored. Local computation gained no network dependency.

Output interpretation/local-class guidance (PLAN-0015 r5): [EN reference/requirements note](../documentation/en/OUTPUT_INTERPRETATION_REQUIREMENTS.md), [AR](../documentation/ar/OUTPUT_INTERPRETATION_REQUIREMENTS.md). NASA/USGS guidance accessed 2026-11-15 is reference-only; no universally applicable NDVI classification standard was established. No data/code import, licensing change or new runtime dependency.

## r6 independently implemented methods (2026-11-15)

- EVI2: Jiang et al. 2008, DOI 10.1016/j.rse.2008.06.006; exact 2.5 gain / 2.4 red coefficient confirmed against [NOAA NDE Vegetation Products ATBD v4.0, 2018-06-01, Eq.3.6](https://www.ospo.noaa.gov/Products/documents/GVF_ATBD_V4.0.pdf) and [ESA SNAP 13 EVI2 specification](https://step.esa.int/main/wp-content/help/versions/13.0.0/snap-toolboxes/eu.esa.opt.opttbx.radiometric.indices.ui/evi2/Evi2AlgorithmSpecification.html). Other similarly named variants are not silently substituted.
- NIRv: unadjusted NIR × NDVI, [Badgley et al. 2017](https://doi.org/10.1126/sciadv.1602244). Not the background-offset NIRv variant or direct GPP.
- RTE/NDVI: [Sobrino et al. 2004, accessible author-hosted paper](https://www.uv.es/sobrino/sobrino_files/papers/Sobrino_LST-Landsat_RSE2004.pdf), Eq.1 and 8–9. Current user-parameterized linear mixture omits cavity term and masks negative NDVI; it is explicitly distinguished from the full published TM5 algorithm. Local band/atmosphere/calibration values remain user-sourced, not invented.
- Use: references only; independently authored MIT code, no scientific paper/catalog/source vendored. `git ls-remote` of Awesome Spectral Indices failed with getaddrinfo in this host; no ASI version pinned/imported, and no IDB redistribution. AWEI/MTCI/IBI/MIRBI remain research candidates. Numerical/native synthetic verification does not establish field accuracy or blanket sensor support.


## PLAN-0019 metadata/product audit references — 2026-11-16

Primary metadata/calibration references (documentation only, not runtime services or vendored code): [USGS old/new identifiers](https://www.usgs.gov/faqs/how-can-i-tell-difference-between-landsat-collections-data-and-landsat-data-i-have-downloaded), [L1 calibration](https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product), [C1/C2 SR scaling](https://www.usgs.gov/faqs/why-are-fill-values-and-scaling-factors-landsat-collection-2-level-2-products-different-those?items_per_page=6&page=1), [USGS QA guide v1.4](https://landsat.usgs.gov/sites/default/files/documents/landsat_QA_tools_userguide.pdf), [S2 processing baseline/offsets](https://sentiwiki.copernicus.eu/web/s2-processing), [USGS spectral library v7](https://pubs.usgs.gov/publication/ds1035). Supporting scientific comparison: [Minerals2022 doi10.3390/min12121577](https://www.mdpi.com/2075-163X/12/12/1577); source-checked Duwi recipes remain unchanged. Exact scope/failed fetches/uncertainty in Reports/PLAN-0019_Audit. No imagery, library spectra, proprietary/GPL source or study figures redistributed.
