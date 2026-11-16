# Calculation catalog

Local implementation definitions; conditional availability is not real-product validation. See current project state and workflow eligibility. No external catalog imported.


## spectral_indices — 01. Spectral Indices

[Usage](QUICK_START.md)


### NDVI — Normalized Difference Vegetation Index

`(NIR - Red) / (NIR + Red)`

Band roles: nir, red

Reference: Rouse et al. (1974), Monitoring vegetation systems in the Great Plains with ERTS

**Meaning:** Red/NIR contrast of green vegetation; higher positive values usually mean stronger greenness, with canopy saturation. A low value alone does not diagnose plant disease.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

NASA examples: <=0.1 often rock/sand/snow; 0.2–0.3 shrub/grassland; 0.6–0.8 dense forest. These are overlapping-context illustrations, not exhaustive executable bins or a health standard. Negative values are not uniquely water.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)

**Optional LOCAL illustrative classes, NOT an international standard. Negative/out-of-range/QA values are excluded; continuous NDVI is preserved.**

| Code | Interval | Meaning |

|---|---|---|

| 1 | [0, 0.2) | Low green-vegetation signal / mixed or bare surface |

| 2 | [0.2, 0.4) | Sparse green vegetation |

| 3 | [0.4, 0.6) | Moderate green vegetation |

| 4 | [0.6, 1] | Dense green vegetation |

Change the three internal boundaries only with a documented local basis. Classification is not plant-health diagnosis.


### GNDVI — Green Normalized Difference Vegetation Index

`(NIR - Green) / (NIR + Green)`

Band roles: nir, green

Reference: Gitelson et al. (1996), Remote sensing of chlorophyll concentration in higher plant leaves

**Meaning:** Green/NIR vegetation contrast with pigment sensitivity; higher values suggest a stronger green vegetation signal, not a calibrated chlorophyll concentration.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### SAVI — Soil-Adjusted Vegetation Index

`((NIR - Red) / (NIR + Red + L)) * (1 + L)`

Band roles: nir, red

Reference: Huete (1988), A soil-adjusted vegetation index (SAVI)

**Meaning:** Soil-adjusted red/NIR vegetation response; larger values suggest more greenness under the selected soil constant L.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### EVI — Enhanced Vegetation Index

`2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))`

Band roles: nir, red, blue

Reference: Huete et al. (2002), Overview of the radiometric and biophysical performance of the MODIS vegetation indices

**Meaning:** Enhanced canopy greenness using blue/red/NIR; high values suggest stronger canopy response; denominator and aerosol contamination can cause exceptional values.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NDRE1 — Normalized Difference Red Edge Index 1

`(NIR - RedEdge1) / (NIR + RedEdge1)`

Band roles: nir, red_edge_1

Reference: Gitelson & Merzlyak (1994), Quantitative estimation of chlorophyll-a using reflectance spectra

**Meaning:** NIR/red-edge vegetation contrast; useful for canopy pigment sensitivity only with appropriate red-edge wavelengths.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NDWI_MCFEETERS — Normalized Difference Water Index (McFeeters)

`(Green - NIR) / (Green + NIR)`

Band roles: green, nir

Reference: McFeeters (1996), The use of the Normalized Difference Water Index in the delineation of open water features

**Meaning:** Green/NIR open-water contrast; larger values can favor open water but shadows/built surfaces can confuse it.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NDWI_GAO — Normalized Difference Water/Moisture Index (Gao)

`(NIR - SWIR1) / (NIR + SWIR1)`

Band roles: nir, swir_1

Reference: Gao (1996), NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space

**Meaning:** Original Gao water-content index depends on wavelength choice; this catalog variant remains gated for wavelength review.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### MNDWI — Modified Normalized Difference Water Index (Xu)

`(Green - SWIR1) / (Green + SWIR1)`

Band roles: green, swir_1

Reference: Xu (2006), Modification of normalised difference water index (NDWI) to enhance open water features

**Meaning:** Green/SWIR open-water enhancement; positive response is evidence to investigate, not a universal water mask.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NDBI — Normalized Difference Built-Up Index

`(SWIR1 - NIR) / (SWIR1 + NIR)`

Band roles: swir_1, nir

Reference: Zha et al. (2003), Use of normalized difference built-up index in automatically mapping urban areas from TM imagery

**Meaning:** SWIR/NIR built-surface contrast; bare soil can respond similarly. High values are not confirmed buildings.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### UI — Urban Index

`(SWIR2 - NIR) / (SWIR2 + NIR)`

Band roles: swir_2, nir

Reference: Kawamura et al. (1996), Relation between social and environmental conditions in developing countries and urban heat islands

**Meaning:** SWIR2/NIR urban-surface contrast; distinguish dry bare land and mixed pixels using independent evidence.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NBR — Normalized Burn Ratio

`(NIR - SWIR2) / (NIR + SWIR2)`

Band roles: nir, swir_2

Reference: Key & Benson (2006), Landscape assessment: Ground measure of severity, the Composite Burn Index; and Remote sensing of severity, the Normalized Burn Ratio

**Meaning:** NIR/SWIR2 burn-sensitive contrast. A single low NBR does not establish burn severity; compare compatible pre/post observations.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NBR2 — Normalized Burn Ratio 2

`(SWIR1 - SWIR2) / (SWIR1 + SWIR2)`

Band roles: swir_1, swir_2

Reference: Garcia & Caselles (1991), Mapping burns and natural hazards with Landsat Thematic Mapper data

**Meaning:** SWIR1/SWIR2 contrast sensitive to burn-related moisture changes; a low/high value needs scene/date context.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NDSI — Normalized Difference Snow Index

`(Green - SWIR1) / (Green + SWIR1)`

Band roles: green, swir_1

Reference: Hall et al. (1995), Development of methods for mapping global snow cover using moderate resolution imaging spectroradiometer data

**Meaning:** Green/SWIR snow contrast; water/cloud/background can overlap. Apply appropriate quality and snow-context checks.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### BSI — Bare Soil Index

`((SWIR1 + Red) - (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))`

Band roles: swir_1, red, nir, blue

Reference: Diek et al. (2017), The normalized difference bare soil index: a new approach

**Meaning:** Bare-soil spectral contrast; positive response may favor exposed soil but varies with soil color, moisture and built surfaces.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### NDMI — Normalized Difference Moisture Index

`(NIR - SWIR1) / (NIR + SWIR1)`

Band roles: nir, swir_1

Reference: Gao, B. C. (1996), NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space

**Meaning:** NIR/SWIR vegetation-moisture proxy; larger values often suggest more canopy moisture, not measured soil moisture.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### MSAVI — Modified Soil-Adjusted Vegetation Index

`(2 * NIR + 1 - sqrt((2 * NIR + 1)^2 - 8 * (NIR - Red))) / 2`

Band roles: nir, red

Reference: Qi et al. (1994), A modified soil adjusted vegetation index

**Meaning:** Vegetation signal with adaptive soil adjustment; larger values generally indicate more greenness. Negative square-root arguments are invalid.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### OSAVI — Optimized Soil-Adjusted Vegetation Index

`(NIR - Red) / (NIR + Red + 0.16)`

Band roles: nir, red

Reference: Rondeaux et al. (1996), Optimization of spectral indices for vegetation monitoring

**Meaning:** Soil-adjusted vegetation ratio; interpretation depends on the implemented normalization variant and 0.16 constant. Do not transfer NDVI classes.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### VARI — Visible Atmospherically Resistant Index

`(Green - Red) / (Green + Red - Blue)`

Band roles: green, red, blue

Reference: Gitelson et al. (2002), Novel algorithms for remote estimation of vegetation fraction

**Meaning:** Visible-band greenness contrast; atmosphere-resistant does not mean atmosphere-free. Unstable denominators may yield large values.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### GLI — Green Leaf Index

`(2 * Green - Red - Blue) / (2 * Green + Red + Blue)`

Band roles: green, red, blue

Reference: Louhaichi et al. (2001), Spatially located platform and aerial photography for documentation of grazing impacts on wheat

**Meaning:** Visible green-leaf contrast relative to red/blue; stronger positive response suggests greener surfaces, not a species diagnosis.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### TCB — Tasseled Cap Brightness

`0.3029*Blue + 0.2786*Green + 0.4733*Red + 0.5599*NIR + 0.508*SWIR1 + 0.1872*SWIR2`

Band roles: blue, green, red, nir, swir_1, swir_2

Reference: Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance

**Meaning:** Sensor-specific brightness component; coefficients/product level remain gated. It has no universal physical class breaks.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### TCG — Tasseled Cap Greenness

`-0.2941*Blue - 0.243*Green - 0.5424*Red + 0.7276*NIR + 0.0713*SWIR1 - 0.1608*SWIR2`

Band roles: blue, green, red, nir, swir_1, swir_2

Reference: Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance

**Meaning:** Sensor-specific greenness component; not interchangeable with NDVI. Coefficients/product level remain gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### TCW — Tasseled Cap Wetness

`0.1511*Blue + 0.1973*Green + 0.3283*Red + 0.3407*NIR - 0.7117*SWIR1 - 0.4572*SWIR2`

Band roles: blue, green, red, nir, swir_1, swir_2

Reference: Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance

**Meaning:** Sensor-specific wetness component; not a direct moisture measurement. Coefficients/product level remain gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### EVI2 — Two-band Enhanced Vegetation Index (2.5/2.4 variant)

`2.5 * (NIR - Red) / (NIR + 2.4 * Red + 1)`

Band roles: nir, red

Reference: Jiang et al. (2008), doi:10.1016/j.rse.2008.06.006; NOAA NDE Vegetation Products ATBD v4.0 (2018), Eq.3.6

[Method source](https://www.ospo.noaa.gov/Products/documents/GVF_ATBD_V4.0.pdf)

**Meaning:** Two-band enhanced vegetation response without blue; quality and coefficient variant matter; no automatic NDVI class transfer.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NIRv — Near-infrared reflectance of vegetation (unadjusted NDVI product)

`NIR * (NIR - Red) / (NIR + Red)`

Band roles: nir, red

Reference: Badgley et al. (2017), Canopy near-infrared reflectance and terrestrial photosynthesis, doi:10.1126/sciadv.1602244

[Method source](https://doi.org/10.1126/sciadv.1602244)

**Meaning:** NIR reflectance attributed to vegetation using NDVI; related to vegetation/photosynthesis but not direct GPP, biomass or yield.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### MTVI2 — Modified Triangular Vegetation Index 2 (MTVI2)

`1.5 * (1.2*(NIR - Green) - 2.5*(Red - Green)) / sqrt((2*NIR + 1)^2 - (6*NIR - 5*sqrt(Red)) - 0.5)`

Band roles: nir, red, green

Reference: Haboudane et al. (2004), Hyperspectral vegetation indices for predicting green crop area index, doi:10.1016/j.rse.2003.12.013

[Method source](https://doi.org/10.1016/j.rse.2003.12.013)

**Meaning:** Modified triangular vegetation index 2; sensitive to green leaf area index and canopy cover, reducing soil background influence.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### MCARI2 — Modified Chlorophyll Absorption in Reflectance Index 2 (MCARI2)

`1.5 * (2.5*(NIR - Red) - 1.3*(NIR - Green)) / sqrt((2*NIR + 1)^2 - (6*NIR - 5*sqrt(Red)) - 0.5)`

Band roles: nir, red, green

Reference: Haboudane et al. (2004), Hyperspectral vegetation indices for predicting green crop area index, doi:10.1016/j.rse.2003.12.013

[Method source](https://doi.org/10.1016/j.rse.2003.12.013)

**Meaning:** Modified chlorophyll absorption in reflectance index 2; estimates green biomass and canopy chlorophyll while minimizing soil and non-photosynthetic effects.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NDRE2 — Normalized Difference Red Edge 2 (Sentinel-2)

`(NIR - RedEdge2) / (NIR + RedEdge2)`

Band roles: nir, red_edge_2

Reference: Barnes et al. (2000), Coincident detection of crop water stress, nitrogen status and canopy density

[Method source](https://doi.org/10.1016/j.rse.2008.06.006)

**Meaning:** Red edge index variant using NIR and red-edge 2 bands; sensitive to high-biomass chlorophyll changes where NDVI saturates.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### CIGREEN — Chlorophyll Index Green (CIgreen)

`(NIR / Green) - 1`

Band roles: nir, green

Reference: Gitelson et al. (2005), Remote estimation of chlorophyll content in higher plant leaves, doi:10.1016/j.jplph.2004.12.014

[Method source](https://doi.org/10.1016/j.jplph.2004.12.014)

**Meaning:** Chlorophyll index green; related to total chlorophyll content in leaves and canopies based on green and NIR reflectance.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### CIREDEDGE — Chlorophyll Index Red-Edge (CIrededge / Sentinel-2)

`(NIR / RedEdge1) - 1`

Band roles: nir, red_edge_1

Reference: Gitelson et al. (2005), Remote estimation of chlorophyll content in higher plant leaves, doi:10.1016/j.jplph.2004.12.014

[Method source](https://doi.org/10.1016/j.jplph.2004.12.014)

**Meaning:** Chlorophyll index red-edge; sensitive to chlorophyll concentration across moderate to high canopy densities.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NDSI_SALINITY — Normalized Difference Salinity Index (NDSI_Salinity)

`(SWIR1 - NIR) / (SWIR1 + NIR)`

Band roles: swir_1, nir

Reference: Major et al. (1990) / Tripathy et al. (2012), Remote sensing of soil salinity in agricultural lands

[Method source](https://doi.org/10.1016/j.rse.2012.03.018)

**Meaning:** Normalized difference salinity index from SWIR1 and NIR; highlights salt-affected bare soils and crusts.

**Units:** dimensionless

**Range:** [-1,1] for nonnegative calibrated operands and a nonzero denominator; QA may expose exceptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## geological_analysis — 05. Geological Analysis & Mineral Alteration

[Usage](QUICK_START.md)


### IRON_OXIDE — Iron Oxide Ratio (Hematite / Goethite / Limonite)

`Red / Blue`

Band roles: red, blue

Reference: Sabins (1999), Remote sensing for mineral exploration

**Meaning:** Red/blue iron-oxide spectral indication; higher ratios may highlight ferruginous surfaces, not mineral concentration or confirmed ore.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### FERRIC_IRON — Ferric Iron Ratio (Fe3+)

`Red / Green`

Band roles: red, green

Reference: Hunt (1977), Spectral signatures of particulate minerals

**Meaning:** Red/green ferric-related surface contrast; spectral proxy needing field/spectral confirmation.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### FERROUS_IRON — Ferrous Iron Ratio (Fe2+)

`SWIR1 / NIR`

Band roles: swir_1, nir

Reference: Rowan et al. (1977), Discrimination of hydrothermally altered and unaltered rocks in Nevada

**Meaning:** SWIR1/NIR ferrous-related surface contrast; mixed minerals/cover can alter the response.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### CLAY_ALTERATION — Clay / Hydroxyl / Al-OH Alteration Ratio

`SWIR1 / SWIR2`

Band roles: swir_1, swir_2

Reference: Drury (1993), Image Interpretation in Geology

**Meaning:** SWIR hydroxyl/clay alteration indication; cannot uniquely identify a clay mineral.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### GOSSAN — Gossan / Laterite Index

`SWIR1 / Red`

Band roles: swir_1, red

Reference: Sabins (1999), Remote sensing for mineral exploration

**Meaning:** Gossan-related band-ratio response; not confirmation of mineralization or economic value.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### ASTER_QUARTZ — ASTER Thermal Quartz Index (QI)

`(B11 * B11) / (B10 * B12)`

Band roles: thermal_1, thermal_2

Reference: Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data

**Meaning:** ASTER TIR quartz proxy; exact product/band emissivity semantics remain gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### ASTER_CARBONATE — ASTER Thermal Carbonate Index (CI)

`B13 / B14`

Band roles: thermal_1, thermal_2

Reference: Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data

**Meaning:** ASTER TIR carbonate proxy; exact product/band emissivity semantics remain gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### ASTER_MAFIC — ASTER Thermal Mafic / Silicate Index (MI)

`B12 / B13`

Band roles: thermal_1, thermal_2

Reference: Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data

**Meaning:** ASTER TIR mafic proxy; exact product/band emissivity semantics remain gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### FEAI — Ferric Iron Alteration Index (FEAI - ENVI)

`(SWIR2 / NIR) + (Green / Red)`

Band roles: swir_2, nir, green, red

Reference: NV5 ENVI Spectral Indices / Crowley et al. (1989)

**Meaning:** Ferric Iron Alteration Index (FEAI) from SWIR2/NIR and Green/Red; highlights ferric iron alteration zones.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### FEI — Ferrous Iron Index (FEI - ENVI)

`(SWIR2 + NIR) / (Green + Red)`

Band roles: swir_2, nir, green, red

Reference: NV5 ENVI Spectral Indices / Segal (1983)

**Meaning:** Ferrous Iron Index (FEI) from (SWIR2+NIR)/(Green+Red); highlights ferrous iron minerals.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### FESI — Ferrous Silicates Index (FESI - ENVI)

`SWIR2 / SWIR1`

Band roles: swir_2, swir_1

Reference: NV5 ENVI Spectral Indices / Rowan et al. (1986)

**Meaning:** Ferrous Silicates Index (FESI) from SWIR2/SWIR1; highlights ferrous silicate rock units.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### LATI — Laterite Index (LATI - ENVI)

`SWIR1 / Green`

Band roles: swir_1, green

Reference: NV5 ENVI Spectral Indices / Boettinger et al. (2008)

**Meaning:** Laterite Index (LATI) from SWIR1/Green; highlights laterite and ferric weathered soils.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## surface_temperature — 02. Surface Temperature

[Usage](QUICK_START.md)


### LST — Land surface temperature

`LST`

**Meaning:** Land surface temperature, not 2 m air temperature; official L2 extraction or explicitly selected local NDVI/RTE derivation are distinct methods.

**Units:** temperature unit selected

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### LST_CELSIUS — Official L2 surface temperature (Celsius)

`Kelvin - 273.15; Landsat C2 L2 Kelvin = DN * 0.00341802 + 149.0`

Reference: USGS Landsat Collection 2 Level-2 Science Products

**Meaning:** Official surface temperature in Celsius; Celsius = Kelvin - 273.15. Hot/cold classes depend on location, season and reference.

**Units:** temperature unit selected

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### LST_KELVIN — Official L2 surface temperature (Kelvin)

`Landsat C2 L2: DN * 0.00341802 + 149.0; other official products use their own verified profile`

Reference: USGS Landsat Collection 2 Level-2 Science Products

**Meaning:** Official surface temperature in Kelvin; same physical quantity as Celsius, with a different zero point.

**Units:** temperature unit selected

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### EMISSIVITY_NDVI — NDVI emissivity (gated: method review)

`EMISSIVITY_NDVI`

**Meaning:** Dimensionless thermal emission efficiency estimated with an NDVI model, not temperature or NDVI itself; legacy choice remains gated.

**Units:** dimensionless

**Range:** Physical fraction [0,1]; the model/product can be invalid or outside assumptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## thermal_urban — 03. Thermal & Urban Analysis

[Usage](QUICK_START.md)


### UTFVI — UTFVI and classification

`(LST_K - mean(LST_K)) / mean(LST_K); reference = valid scene pixels`

Reference: Existing UTFVI mean-normalized convention; classification requires independent real-product validation

**Meaning:** LST departure from the valid-scene mean normalized by mean Kelvin temperature; categories are convention/reference dependent, not air heat risk.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### HOTSPOTS — Thermal hotspots (z >= 2)

`(LST_K - mean(LST_K)) / std(LST_K) >= 2; reference = valid scene pixels`

Reference: Descriptive z-score threshold; not air temperature or urban/rural SUHI

**Meaning:** Binary pixels with scene-relative thermal z-score >= 2; descriptive high-temperature anomaly, not spatial significance or confirmed SUHI.

**Units:** binary flag

**Range:** 0=not flagged, 1=flagged; 255=NoData in the binary raster

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### SUHI — SUHI (gated: urban/rural references)

`SUHI`

**Meaning:** Urban-versus-rural surface temperature difference requires defined reference masks; currently gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## environmental_drought — 04. Environmental & Drought Analysis

[Usage](QUICK_START.md)


### ALBEDO — Broadband albedo (Landsat TM/ETM+ only)

`0.356*Blue + 0.130*Red + 0.373*NIR + 0.085*SWIR1 + 0.072*SWIR2 - 0.0018`

Reference: Liang (2001), Narrowband to broadband conversions of land surface albedo; TM/ETM+ profile only

**Meaning:** Broadband reflected/incident shortwave fraction using the restricted TM/ETM+ conversion; no universal land-cover classes.

**Units:** dimensionless

**Range:** Physical fraction [0,1]; the model/product can be invalid or outside assumptions

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### TVDI — TVDI (gated: validated dry/wet edges)

`TVDI`

**Meaning:** NDVI/temperature dry-wet edge position; genuine fitted edges are required and current calculation is gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### VCI_TCI_VHI — VCI / TCI / VHI (gated: historical baseline)

`VCI_TCI_VHI`

**Meaning:** Historical vegetation/temperature condition indices require compatible seasonal baselines; current calculation is gated.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## temporal_change — 06. Temporal Analysis & Change Detection

[Usage](QUICK_START.md)


### NDVI — NDVI difference (T2 - T1)

`NDVI(T2) - NDVI(T1)`

Reference: Arithmetic difference; identical sensor, level and compatible epochs required

**Meaning:** NDVI(T2) minus NDVI(T1); positive means increase, negative decrease. Direction alone does not establish a cause or burn severity.

**Units:** dimensionless difference

**Range:** [-2,2] only when both valid input indices are within [-1,1]

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.

[Source](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/)

[Source](https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices)


### NBR — NBR difference (T2 - T1)

`NBR(T2) - NBR(T1)`

Reference: Arithmetic difference; identical sensor, level and compatible epochs required

**Meaning:** NBR(T2) minus NBR(T1); positive means increase, negative decrease. Direction alone does not establish a cause or burn severity.

**Units:** dimensionless difference

**Range:** [-2,2] only when both valid input indices are within [-1,1]

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### LST — Surface temperature difference (T2 - T1)

`LST(T2) - LST(T1)`

Reference: Arithmetic difference; identical sensor, level and compatible epochs required

**Meaning:** LST(T2) minus LST(T1); positive means increase, negative decrease. Direction alone does not establish a cause or burn severity.

**Units:** °C difference

**Range:** No universal fixed interval

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


## geological_composites — 07. Geological Color Composites

[Usage](QUICK_START.md)


### L89_753 — Landsat 8/9: 7-5-3 Direct RGB (Lithology & Structure)

`R=B7(2.20µm), G=B5(0.86µm), B=B3(0.56µm)`

Reference: https://www.nature.com/articles/s41598-024-66199-3

**Meaning:** Landsat 8/9 7-5-3 Direct RGB: assigns SWIR2, NIR and Green bands to RGB; standard geological composite for rock and vegetation contrast.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### L89_762 — Landsat 8/9: 7-6-2 Direct RGB (Geological Boundaries)

`R=B7(2.20µm), G=B6(1.61µm), B=B2(0.48µm)`

Reference: Sabins (1999) / USGS Geological Composite standard

**Meaning:** Landsat 8/9 7-6-2 Direct RGB: assigns SWIR2, SWIR1 and Blue bands to RGB; highlights lithological boundaries and structural features.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### L89_CRC1 — Landsat 8/9: Sultan CRC1 Ratio RGB (Ophiolite & Carbonates)

`R=B6/B7, G=B6/B2, B=(B4/B5)*(B6/B5)`

Reference: Sultan et al. (1987) / Duwi Figure 10

**Meaning:** Landsat 8/9 Sultan CRC1 Ratio RGB: assigns B6/B7, B6/B2, and (B4/B5)*(B6/B5) to RGB; highlights ophiolitic and carbonate rocks.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### L89_CRC2 — Landsat 8/9: Sultan CRC2 Ratio RGB (Hydrothermal Alteration)

`R=B4/B6, G=B4/B2, B=B6/B7`

Reference: Sultan et al. (1987) / Duwi Figure 11

**Meaning:** Landsat 8/9 Sultan CRC2 Ratio RGB: assigns B4/B6, B4/B2, and B6/B7 to RGB; highlights hydrothermal alteration zones.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### S2_12112 — Sentinel-2: 12-11-2 Direct RGB (Geology & Structures)

`R=B12(2.19µm), G=B11(1.61µm), B=B2(0.49µm)`

Reference: Copernicus Sentinel-2 Geological standard

**Meaning:** Sentinel-2 12-11-2 Direct RGB: assigns B12, B11 and B2 to RGB; standard geological composite for lithology and structures.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### S2_12114 — Sentinel-2: 12-11-4 Direct RGB (Lithological Discrimination)

`R=B12(2.19µm), G=B11(1.61µm), B=B4(0.66µm)`

Reference: Copernicus Sentinel-2 Lithology standard

**Meaning:** Sentinel-2 12-11-4 Direct RGB: assigns B12, B11 and B4 to RGB; highlights rock units and soil discrimination.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### ASTER_468 — ASTER: 4-6-8 Direct RGB (SWIR Alteration Zones)

`R=B4(1.65µm), G=B6(2.21µm), B=B8(2.33µm)`

Reference: ASTER Science Project / Rowan et al.

**Meaning:** ASTER 4-6-8 Direct RGB: assigns SWIR bands B4, B6 and B8 to RGB; highlights mineral alteration zones.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### ASTER_FAWAKHEIR — ASTER: Fawakheir Ratio RGB (Hydrothermal Mineral Mapping)

`R=(B2+B4)/B3N, G=(B5+B7)/B6, B=(B7+B9)/B8`

Reference: Zoheir et al. / Fawakheir study

**Meaning:** ASTER Fawakheir Ratio RGB: assigns band ratios (B2+B4)/B3N, (B5+B7)/B6, (B7+B9)/B8 to RGB; highlights hydrothermal mineralization.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### DIRECT_RGB — Direct RGB (Sensor default or custom)

`RGB = three explicitly selected scientific bands`

Reference: https://www.nature.com/articles/s41598-024-66199-3

**Meaning:** Three calibrated scientific bands assigned to red, green and blue. Spectral colors retain continuous terrain detail; they do not identify rock classes.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.


### RATIO_RGB — Band Ratio RGB (Sensor default or custom)

`RGB = three independently evaluated spectral expressions`

Reference: https://www.nature.com/articles/s41598-024-66199-3

**Meaning:** Three independently calculated spectral expressions displayed as RGB; ratio contrast is not a confirmed rock/mineral classification.

**Units:** dimensionless

**Range:** No universal fixed interval; use method assumptions and QA

**Limitations:** Interpret with sensor, product level, season, land cover, soil, atmosphere, moisture and resolution. Indicative ranges are not a universal class standard. Local independent validation is required; NoData/QA are not a land-cover class.

**Classification:** No verified universal classification standard; optional local schemes must be justified and recorded.
