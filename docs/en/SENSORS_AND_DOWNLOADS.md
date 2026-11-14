# Satellite/sensor guide and FREE download portals (English)
**Workflow:** open an official portal → optionally register a free account → search/select product (prefer analysis-ready level) → download → extract/unpack the **entire original product with metadata and QA** → select its folder in ATIAF. No login or download required inside ATIAF. Support status in sensor_registry.json is a development TARGET, not implemented.

## Sensor families and safe input levels
| Family / sensor | Spatial detail | Recommended files/products | Main uses and important restrictions | Official free portal; account |
|---|---|---|---|---|
| Landsat 1–3 MSS; 4–5 MSS | approx 60–80 m, product-dependent | Level-1 and metadata | Old vegetation/land change; **no SWIR or thermal**; no USGS C2 MSS Level-2 SR currently | [USGS EarthExplorer](https://earthexplorer.usgs.gov/); free account |
| Landsat 4–5 TM; Landsat 7 ETM+ | 30 m reflective; thermal native resolution differs | Collection 2 Level-2 SR and ST where available | NDVI/water/urban/thermal; Landsat 7 SLC-off gaps after 31 May 2003 | [USGS EarthExplorer](https://earthexplorer.usgs.gov/); free account |
| Landsat 8 OLI/TIRS; Landsat 9 OLI-2/TIRS-2 | 30 m reflectance; TIR native ~100 m, delivered on 30 m grid | Collection 2 Level-2 `SR_Bx`, `ST_B10`, `QA_PIXEL`, `QA_RADSAT`, `MTL.txt/MTL.xml` | Rich reflectance, LST with valid ST; ST may be absent if auxiliary data unavailable | [USGS EarthExplorer](https://earthexplorer.usgs.gov/); free account |
| Sentinel-2 MSI A/B/C | 10/20/60 m band dependent | `*.SAFE`, L2A preferred; JP2 bands, MTD files, SCL | Excellent red edge, water, urban, geology; **no thermal**, L1C is TOA | [Copernicus Browser](https://dataspace.copernicus.eu/browser/); free account |
| ASTER on Terra | VNIR 15 m, SWIR 30 m, TIR 90 m | AST_L1T, AST_07/07XT reflectance, AST_05 emissivity, AST_08 temperature, AST_09T radiance | Geology/thermal archive; SWIR invalid after Apr 2008; TIR acquisitions ended 16 Jan 2026 | [NASA Earthdata](https://search.earthdata.nasa.gov/); free login; some products ordered on demand |
| Sentinel-3 OLCI / SLSTR | OLCI 300 m; SLSTR band/product 500 m–1 km | Verified Copernicus L1/L2 product structures | Ocean colour, vegetation, LST/fire | [Copernicus Data Space](https://dataspace.copernicus.eu/); free registration for download |
| MODIS Aqua/Terra | band/product-dependent 250 m–1 km | MOD09/MYD09, MOD11/MYD11, MOD13/MYD13 as appropriate | Long time series and land temperature; HDF/QA complexity | [NASA Earthdata](https://search.earthdata.nasa.gov/); free login |
| VIIRS | varies; ~375 m to 750 m or gridded 1 km | VIIRS LST, fire and reflectance products by verified shortname | Time series, fire; product-specific QA | NASA Earthdata; free login |
| ECOSTRESS | approx 70 m, product-specific | Ecostress L2 LST/emissivity and ET/stress products | Thermal/water stress; ISS variable acquisition and Version 2 product preference | [NASA Earthdata](https://search.earthdata.nasa.gov/); free login |
| EnMAP | 30 m hyperspectral | L2A GeoTIFF plus metadata preferred | Geological absorption, vegetation, mineral candidates; user registration and license conditions | [EnMAP portal](https://www.enmap.org/data_access/); free-data policy/account requirements need current check |
| PRISMA | 30 m hyperspectral; 5 m pan | ASI PRISMA L2D or suitable level and metadata | Mineral hyperspectral; product license may restrict redistribution | [ASI PRISMA](https://www.asi.it/en/earth-science/prisma/); register/accept conditions |
| EMIT | ~60 m spectroscopy | `EMITL2ARFL` NetCDF4 or `EMITL2BMIN`; orthorectification care | Mineral spectral products; L2A is not supplied as a ready north-up GeoTIFF | [NASA Earthdata](https://search.earthdata.nasa.gov/); free login |
| Sentinel-1 SAR | ~5–40 m depending acquisition product | GRD/SLC SAFE and XML metadata | SAR backscatter/coherence; requires dedicated processing pipeline | [Copernicus](https://dataspace.copernicus.eu/) or [ASF Vertex](https://search.asf.alaska.edu/); free account |
| ALOS PALSAR / PALSAR-2 | varies by archive/product | mission/product-specific L-band products | Forest/geology SAR; check product-specific permission and availability | [ASF Vertex](https://search.asf.alaska.edu/); Earthdata account |
| NISAR | acquisition mode/product-dependent | NASA/ISRO SAR formats and metadata | Deformation, biomass, change; planned separate radar capability | [NASA Earthdata](https://search.earthdata.nasa.gov/); verify specific products |

**NASA ASTER access note:** While all data from LP DAAC are free, some higher-level ASTER scenes are generated **on demand** via Earthdata Search. ASTER TIR stopped **Jan 16, 2026**; VNIR continued separately. Landsat 8/9 TIR sensor native IFOV is coarser than 30 m delivered rasters; do not claim true native 30 m heat detail. Sensor detector must check date and product metadata, not infer by filename alone.

## Product unpack examples (not a claim of implementation)
- Landsat C2: one scene directory with `*_MTL.txt` / `*_MTL.xml`, `*_SR_B4.TIF`, `*_SR_B5.TIF`, optional `*_ST_B10.TIF`, `*_QA_PIXEL.TIF`, and all product files. Detect actual instruments/versions and QA.
- Sentinel-2: keep the entire `.SAFE/` directory including `MTD_MSIL2A.xml`, `GRANULE/.../IMG_DATA/R10m,R20m,R60m/*.jp2`, `QI_DATA`, SCL. No blind path assumptions across processing baselines.
- ASTER HDF: store original HDF with all metadata/subdatasets; user may have more than one granule or ordered product. Parse GDAL subdatasets safely; distinguish radiance, reflectance, emissivity, temperature and ASTER DEM.
- EnMAP: L2A reflectance (GeoTIFF+metadata) includes wavelength/fwhm attributes and quality. EMIT L2A NetCDF is typically raw in instrument geometry and may need orthorectification before spatial use.

## Method of choosing product
1. For spectral indices, prefer calibrated surface reflectance (Landsat C2 L2 SR, S2 L2A, suitable ASTER/EnMAP products).
2. For LST, prefer validated surface-temperature products (e.g., Landsat C2 L2 ST, ASTER AST_08) with corresponding QA and units; thermal brightness ≠ LST.
3. For geology, match wavelength and source level to method; ASTER pre-2008 SWIR archival for SWIR geology, TIR indices must use correct thermal product type.
4. For historical comparisons, retain acquisition time, geometry, resolution and masks; product descriptions and dates matter as much as the sensor name.

## Help requirements for EACH sensor page
Name, mission, status, modality, band number/role, approximate center wavelength and FWHM where appropriate, resolution, products/levels, required ancillary/QA, sample directory structure, valid temporal bands, downloadable free portals, registration and license caveats, validated compatible indices, known processing issues, exact source links and date checked. Arabic/English pages share stable sensor and product IDs.
