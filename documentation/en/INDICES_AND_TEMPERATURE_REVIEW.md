# Additional indices and temperature controls — research review

**Historical planning note (r3–r4).** Current 1.0.2.dev0 behavior supersedes the implementation-status statements below: grouped native controls, manual input, EVI2/NIRv and optional local NDVI/RTE now have numerical/native synthetic evidence. Other sensor/index candidates and real-product accuracy remain unvalidated. Use [current quick start](QUICK_START.md), [temperature guide](SURFACE_TEMPERATURE.md) and PROJECT_STATE for current status; the original research discussion is retained below.

Date: 2026-11-15. PLAN-0015 r3. **Research/proposals only; no new runtime calculation, sensor reader or UI change.** [Arabic counterpart](../ar/INDICES_AND_TEMPERATURE_REVIEW.md).

## Useful candidates

These IDs are absent from the current runtime calculation catalog. Band availability establishes feasibility, not validated sensor support. Prefer calibrated surface reflectance and apply product-specific scales, offsets, quality masks and a justified common grid. Thresholds/classification accuracy must be evaluated locally.

| Theme | Candidate | Purpose and required band roles | Initial sensor feasibility / review limit |
|---|---|---|---|
| Vegetation | EVI2 | Two-band vegetation index; red + NIR; useful when blue is unavailable | Landsat optical / Sentinel-2. Select and verify original coefficient variant; do not copy catalog defaults blindly. |
| Vegetation | NIRv | Vegetation contribution to NIR reflectance; red + NIR | Landsat / Sentinel-2. It is a photosynthesis-related proxy, not a direct GPP estimate. |
| Surface water | AWEIsh / AWEInsh | Water enhancement with distinct shadow/no-shadow formulations; green, NIR, SWIR1/2, additionally blue for the shadow variant | Landsat / Sentinel-2. Original study used Landsat 5 TM; other sensors and thresholds require validation. |
| Chlorophyll | MTCI adaptation | Red-edge chlorophyll sensitivity; red + two appropriate red-edge bands | Sentinel-2 candidate only after spectral adaptation review. Original MTCI was designed for MERIS band settings, not Landsat. |
| Urban | IBI | Combines built-up, vegetation and water information; green, red, NIR, SWIR1 | Landsat / Sentinel-2 candidate. Verify component conventions/constant and denominator behavior; not building footprints. |
| Burn | MIRBI | Burn-related SWIR response; SWIR1 + SWIR2 | Landsat / Sentinel-2 candidate. Correct reflectance scaling matters because the equation contains an additive constant. |

NDVI, EVI, NDMI, NBR, NBR2, NDSI, BSI and others already appear in the runtime catalog; they must not be counted as new additions. Keep moisture apart from open-water extraction. Similar equations/aliases must not inflate the count of independent methods.

First priority proposed: EVI2, NIRv and AWEI variants, then sensor-specific chlorophyll, urban and burn additions. Existing Landsat/Sentinel-2 band coverage should suffice for that optical batch; this is an inference from requirements and official sensor band tables, not a test result.

## Optional additional thermal products

- MODIS Terra MOD11A1 / Aqua MYD11A1: daily LST/emissivity products at 1 km; useful for regional time series rather than fine urban detail.
- Sentinel-3 SLSTR SL_2_LST: LST product at 1 km; useful regional thermal coverage.

These need independent local readers, QA, scaling, grid/geolocation handling and validation. They are **proposed**, not validated ATIAF workflows. Free availability does not remove possible provider download registration; local computation must still require no login/key/download. Sentinel-2 MSI covers visible/NIR/SWIR, with no thermal channel; optical Sentinel-2 alone cannot supply measured thermal LST.

## Calculation search and grouping

Source inspection: the Pro `search` parameter only filters existing local calculation controls. It neither searches the internet nor discovers imagery or new equations. QGIS currently uses native multiple selection without this custom parameter. Record removal from analysis dialogs, not the separate documentation portal. Group actual selectable controls by Vegetation/Chlorophyll, Surface Water, Vegetation Moisture, Urban, Bare Soil, Burn, Snow and advanced Transformations, using only groups relevant to each tool. Missing bands must give reasons rather than imply runnable support.

## Surface Temperature explanation and UI proposal

- LST is the temperature of the land surface, not air temperature measured above it.
- `LST_CELSIUS` and `LST_KELVIN` are the same quantity in different units: Celsius = Kelvin − 273.15; 303.15 K = 30 °C. Current tool paths use official L2 surface-temperature provenance.
- Emissivity describes thermal emission relative to an ideal blackbody; it has no temperature unit. NDVI is a vegetation index. A method may estimate emissivity from NDVI plus empirical assumptions; NDVI itself is not emissivity.
- `EMISSIVITY_NDVI` currently returns a method-review gate, not an accepted emissivity output. Do not describe the existing low-level model docstring as independent validation. Negative NDVI alone is not a reliable universal water classifier.
- Official Landsat C2 L2 ST retrieval already incorporates emissivity and atmospheric information. Decode its scale/offset and mask quality; do not apply another emissivity correction to that ST raster.
- Proposed clearer controls: one selected LST calculation and a Celsius/Kelvin unit selector (Celsius default proposed), with optional advanced emissivity outputs separately explained. An official supplied emissivity layer and an NDVI-derived estimate would require distinct source/method labels. This UI proposal awaits consolidated review; no parameter migration was performed.

## Sources and access limits

Access date: 2026-11-15. Sources are reference material only, not runtime dependencies or redistributed datasets.

1. [Jiang et al. (2008), EVI2 — NASA MODIS publication record](https://modis.gsfc.nasa.gov/sci_team/pubs/abstract_new.php?id=01496), DOI 10.1016/j.rse.2008.06.006. Search-index abstract accessible; direct open returned HTTP 502. Full equation/variant review still required.
2. [Badgley et al. (2017), NIRv — original article](https://doi.org/10.1126/sciadv.1602244). Original publisher search result accessible; PMC direct open was challenge-blocked.
3. [Feyisa et al. (2014), AWEI — authors' university record and abstract](https://researchprofiles.ku.dk/da/publications/automated-water-extraction-index-a-new-technique-for-surface-wate/), DOI 10.1016/j.rse.2013.08.029.
4. [Dash & Curran (2004), MTCI — publisher article](https://www.tandfonline.com/doi/abs/10.1080/0143116042000274015); publisher abstract accessible in search. Original equation targets MERIS wavelengths.
5. [IBI definition and original research citation](https://awesome-spectral-indices.github.io/awesome-spectral-indices/indices/IBI), Xu (2008), DOI 10.1080/01431160802039957; [MIRBI definition and original research citation](https://awesome-spectral-indices.github.io/awesome-spectral-indices/indices/MIRBI), Trigg & Flasse (2001), DOI 10.1080/01431160110053185. Original DOI direct opens unavailable; full-paper review is pending. These are the catalog maintainers' own definition pages, not independent sensor validation.
6. [Copernicus Sentinel-2 product specification 15.1](https://sentinels.copernicus.eu/documents/d/sentinel/sentinel-2-products-specification-document-15_1): spectral coverage and band resolutions.
7. [USGS Landsat C2 Level-2 factsheet](https://pubs.usgs.gov/fs/2021/3055/fs20213055.pdf), [USGS scale-factor instructions](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products), [USGS ST auxiliary inputs](https://www.usgs.gov/landsat-missions/landsat-collection-2-atmospheric-auxiliary-data).
8. [NASA MOD11A1 product](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/MOD11A1/), [NASA MYD11A1 product record](https://data.nasa.gov/dataset/modis-aqua-land-surface-temperature-emissivity-daily-l3-global-1km-sin-grid-v061-14a0b), [Copernicus SLSTR Land Handbook](https://sentinels.copernicus.eu/documents/247904/4598082/Sentinel-3-SLSTR-Land-Handbook.pdf).

Awesome Spectral Indices definition pages declare MIT. No catalog/code was imported; no release/commit was pinned by this research. Before any future import, inspect and pin an exact version/license and reconcile each selected formula with original research. Scientific papers retain their own rights; bibliographic reference is not redistribution permission. No Index DataBase records or satellite imagery were downloaded/vendored.

## r4 clarification: optional NDVI-assisted LST and Sentinel-1

The user reaffirms optional NDVI use **within LST derivation**. This is not fulfilled by a separate emissivity raster. Current workflow offers official L2 ST only; EMISSIVITY_NDVI is gated, no external NDVI input exists, and the low-level emissivity branch produces emissivity rather than derived LST. Proposed future UI: optional NDVI-assisted derivation with either a compatible local NDVI or red/NIR computation, scientifically reviewed emissivity and real thermal/atmospheric inputs. A direct arbitrary NDVI/temperature weighting is not the proposed physical method. Official L2 ST must not be corrected again.

Primary research: [Sobrino, Jiménez-Muñoz & Paolini (2004), Landsat TM5 LST retrieval](https://www.uv.es/sobrino/sobrino_files/papers/Sobrino_LST-Landsat_RSE2004.pdf), DOI 10.1016/j.rse.2004.02.003, accessible author-hosted paper. It is not automatic validation of another sensor or of the current code. [USGS ST processing inputs](https://www.usgs.gov/landsat-missions/landsat-collection-2-atmospheric-auxiliary-data) document the official-product path.

Sentinel-1 uses C-band SAR and operates day/night through cloud. Its data are free; applications include flood mapping, agricultural/soil-surface studies and deformation. It does not measure optical red/NIR or thermal LST. Quantitative moisture retrieval requires additional modeling/validation, not a backscatter ratio labeled as moisture. Conventional InSAR needs compatible phase-preserving SLC acquisitions; GRD alone does not retain that phase.

Current ATIAF has a Sentinel-1 discovery parser and preliminary array SAR helpers/gates, but no dedicated native radar tool, complete calibrated product workflow or real-product/native evidence. These helpers must be scientifically audited before reuse; their presence/tests are not full SAR support. Potential future priority: explicit GRD backscatter/water-change workflow, with calibration/noise/terrain corrections and locally supplied orbit/elevation inputs where required. InSAR is separate scope. No SAR implementation is undertaken by this discussion.

Sources accessed 2026-11-15: [Copernicus mission](https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-1), [data availability](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html), [official applications and SLC/GRD requirements](https://sentiwiki.copernicus.eu/web/s1-applications). References only; no imagery or third-party code downloaded/vendored. Native/real-product validation of these proposed paths: NOT RUN.
