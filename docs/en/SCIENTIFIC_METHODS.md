# Scientific index, transformation and physical-model reference (EN)
**All listed capabilities are planned; only registered and independently validated methods may be enabled by the future UI.** Formula variant/source/physical units take precedence over display acronym. The original peer-reviewed description is the authority for scientific naming; catalogs support discovery.

## Formula families and explicit definitions
| Category | Formula or method | Band roles / conditions | Notes |
|---|---|---|---|
| Vegetation | **NDVI = (NIR − Red)/(NIR + Red)** | Surface reflectance Red+NIR | Mask invalid zeros/NoData, floating-point math; not a direct emissivity measurement |
| Vegetation | EVI = G*(NIR−Red)/(NIR+C1*Red−C2*Blue+L) | Reflectance plus method-specific G,C1,C2,L | Cite/validate accepted coefficients and physical input before use |
| Vegetation / soil | SAVI = (1+L)*(NIR−Red)/(NIR+Red+L) | Red+NIR; chosen soil adjustment L | Record value and reason/source |
| Water (McFeeters) | NDWI = (Green−NIR)/(Green+NIR) | Green+NIR | Different from Gao's vegetation water NDWI |
| Water (Xu) | MNDWI = (Green−SWIR1)/(Green+SWIR1) | Green+SWIR1 | Reproject/band alignment if necessary |
| Vegetation moisture (Gao) | NDWI = (NIR−SWIR1)/(NIR+SWIR1) | NIR+SWIR1 | Not the McFeeters formula; distinct stable ID |
| Urban | NDBI = (SWIR1−NIR)/(SWIR1+NIR) | SWIR1+NIR | Built-up response not a binary building classification |
| Burn | NBR = (NIR−SWIR2)/(NIR+SWIR2) | NIR+SWIR2 | delta-NBR requires reference acquisition |
| Snow | NDSI = (Green−SWIR1)/(Green+SWIR1) | Green+SWIR1 plus relevant masking | Similar algebra to MNDWI but different intended interpretation and QA context |
| Soil | BSI (one common variant) = ((SWIR1+Red)−(NIR+Blue))/((SWIR1+Red)+(NIR+Blue)) | Blue, Red, NIR, SWIR1 | Other "BSI" definitions exist; keep source-specific IDs |
| Geological iron | Red/Blue or Red/Green ratios | Sensor/scene-specific reflectance | Prospective ferric iron response only, requires contextual validation |
| Geological clay/OH | SWIR1/SWIR2 ratio | Landsat TM/OLI and suitable Sentinel-2 equivalents as researched | Not a universal mineral assay; reflectance and wavelength sensitivity vary |
| ASTER geology | Quartz Index (example) `TIR11*TIR11/(TIR10*TIR12)` | ASTER TIR; **verify emissivity vs radiance and preprocessing in source** | Do not use with Sentinel-2 band numbers |
| ASTER geology | Carbonate Index (example) `TIR13/TIR14` | ASTER TIR; method/product state must be verified | Candidate until exact original method checked |
| Thermal | Landsat C2 L2 ST: K = `DN*0.00341802 + 149.0`; °C = K−273.15 | Product containing valid ST_B10 (L8/9), QA and fill mask | Refer to USGS for exact sensor/product variants; not for generic DN |
| Thermal | Landsat C2 L2 SR = `DN*0.0000275 - 0.2` | L4–9 valid Level-2 reflectance bands, QA & fill | Verify per-product tags and file QA; do not scale twice |
| Thermal | BT: Planck inversion with official K1/K2 coefficients | Radiance+metadata constants | BT ≠ LST; instrument-specific calibrated source required |
| Urban | SUHI intensity = `mean(urban LST)−mean(reference rural LST)` (chosen definition) | LST, documented built-up & rural polygons, spatial/temporal comparability | Distinct from air UHI; reference choice controls conclusions |
| Environmental | Tasseled Cap Brightness/Greenness/Wetness | Multi-band weighted sums | Coefficient tables depend on sensor & surface/TOA level; no universal matrix |
| Environmental | Albedo | Wavelength-weighted broadband model | Requires sensor-specific equation and product level |
| Drought | TVDI | LST + NDVI, dry and wet regression envelopes | Adequate land-cover sample range; not direct soil moisture |
| Drought | TCI, VCI, VHI | Temporal reference years and statistical convention | Needs multi-date climatological or site baseline |
| Surface energy | `Rn = G + H + LE` | Local net radiation, heat fluxes and weather/ancillary inputs | ETa requires actual model inputs; no fictional standalone imagery-only output |
| Hyperspectral | SAM, MNF, continuum removal, spectral unmixing | Compatible spectral cube; spectral response and optional reference spectral library | Preserve wavelength/fwhm and quality/uncertainty profiles |
| SAR | Calibrated VV/VH or other polarizations | Radar-specific product/geometry/calibration | Do not apply multispectral reflectance ratios directly |

## Expanded catalog candidate families
- **Vegetation/chlorophyll:** NDVI variants, EVI/EVI2, SAVI/OSAVI/MSAVI, GCI, NDRE, MCARI/TCARI, VARI, GEMI, GNDVI, WDRVI, ARI/ARI2, SIPI, PSRI, CIred-edge, kNDVI, TSAVI/ATSAVI, red-edge chlorophyll, mangrove index.
- **Water, moisture and snow:** two scientifically distinct NDWI methods; MNDWI, AWEI, WRI, NDMI, moisture stress, NDSI snow variants, water turbidity/chlorophyll proxies where spectral response supports them.
- **Urban, bare soil, agriculture, burn:** NDBI, BSI variants, IBI, UI, NBR/NBR2, dNBR/RdNBR, NDTillI, STI, MBI, bare rock and clay indicators.
- **Geology/mineral:** iron oxides, ferric/ferrous iron, ferric hydroxides, clay/OH alteration, gossan, lithological ratios, ASTER TIR QI/CI/MI/SI, geological PCA/Crosta, Tasseled Cap, specialized composites; future hyperspectral mineral absorption methods.
- **Thermal and environmental:** LST/BT/LSE/TIR radiance/uncertainty, SUHI/UTFVI/hotspot, TVDI/TCI/VCI/VHI, Albedo, Rn/G/H/LE/ETa gated by required meteorology.

## Scientific evidence and provenance rules
1. Search original paper/DOI first; record exact definition, variant and units, not a guessed acronym.
2. The sensor registry maps physical roles/wavelengths to actual band assets; UI disables absent or scientifically incompatible combinations.
3. A local registry entry must have unique ID, source, formula, variables, normalized role, sensor constraints, test fixture and validation status before release.
4. QA mask, product scaling/offset, NoData and image date/CRS always precede arithmetic. Distinguish L1 TOA from L2 BOA and surface temperature from thermal brightness temperature.
5. Record scale values read from actual metadata `file:key`; official product constants are cited if not actually sourced from file; user override separately flagged.
6. Use named, peer-reviewed original references for geology/mineral classes and verify wavelength-response suitability, not universal claims about iron/ore detection.

### Reference sources
- [Awesome Spectral Indices](https://github.com/awesome-spectral-indices/awesome-spectral-indices) (MIT; experimental v1 changes); [Spyndex](https://github.com/awesome-spectral-indices/spyndex).
- [USGS C2 Level 2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products).
- [GRASS Tasseled Cap](https://grass.osgeo.org/grass-stable/manuals/i.tasscap.html).
- [ASTER products](https://asterweb.jpl.nasa.gov/data_products.asp).
- [Index DataBase](https://www.indexdatabase.de/db/i.php) (reference/terms-restricted API).
- [Original ASTER geological methods](https://doi.org/10.11440/rssj1981.22.50), subject to interpretation/product verification.
