# ATIAF — FULL ENGINEERING & SCIENTIFIC PROJECT SPECIFICATION
Version: 0.1 planning baseline, 2026-11-13. **Status: APPROVED design requirements, NOT implemented features.** Corresponding Arabic: [PROJECT_SPECIFICATION_AR.md](PROJECT_SPECIFICATION_AR.md).

## 1. Mission, scope, priorities
ATIAF — **Advanced Thematic Imagery Analysis Framework** (Arabic brand: **أطياف**). An MIT-licensed geospatial toolkit for independent processing of locally downloaded/unpacked satellite products in **ArcGIS Pro**, with **QGIS** compatibility via a second adapter. User supplies images; the system identifies sensor, satellite, level, acquisition date, native bands and metadata, validates methodology, and runs the chosen calculation(s) transparently.

**Non-negotiables:** global sensor coverage targeted; free-first; no obligatory account/network while calculating; bilingual and native-tool help; scientifically proven formulas; preserve originals and all prior results; complete reproducibility. Third-party imagery acquisition portals may require free registration. Do not imply an algorithm can run solely from imagery when external meteorology/reference spectra/etc. is scientifically required.

## 2. Proposed independent tools (one toolbox containing multiple tools)
| Tool | Scope | Expected processing options | Native dependency notes |
|---|---|---|---|
| T01 Spectral Indices | Groups: vegetation/pigments, water/moisture, soil/agriculture, urban, burn, snow, drought and compatible indices | Select individual formulas; disable unsupported; multi-scene, mosaic, AOI | Sensor wavelength, reflectance level, constants, explicit formula variant |
| T02 Surface Temperature | LST, brightness temperature, surface emissivity, uncertainty, radiance where inputs allow | Official ST products preferred; independent NDVI emissivity / optional DEM methods, reported separately | Requires real thermal measurements/products; no Sentinel-2-only LST |
| T03 Thermal & Urban Analysis | SUHI, SUHII, UTFVI, hotspot, LST–NDVI, LST–NDBI, water temperature, temperature variability | Native LST product/locally supplied LST; urban/rural AOI references; mosaic and time windows | No equating surface heat with air temperature; reference conditions mandatory for SUHI |
| T04 Environmental & Drought | Albedo, TVDI, VCI, TCI, VHI, stress proxies; advanced surface-energy balance ETa only with necessary auxiliary inputs | Separate checkboxes; multi-date processing for historical reference windows | ETa/H/LE not from arbitrary one image; external climate input only local user-supplied if required |
| T05 Geological & Mineral Analysis | Iron oxides, ferric/ferrous iron, clay/OH alteration, lithological band ratios, ASTER QI/CI/MI, Tasseled Cap, PCA/Crosta, composites; planned hyperspectral SAM/MNF/unmixing | Sensor-appropriate formula choice and wavelength sensitivity; separate variant IDs | Mineral *indications*, not confirmed assays; historic ASTER SWIR restrictions; TIR emissivity vs radiance |
| T06 Temporal & Change Detection | Spectral and thermal differences, delta products, time comparisons, trend/statistics when time series exists | Time-scoped scene grouping, harmonization/season QA, match grids | Distinguish true change from sensor/date/QA artifacts |
| Future modality tool: Radar Analysis | Sentinel-1, ALOS PALSAR, NISAR modalities | Dedicated SAR calibration/coherence/backscatter workflow | Never route SAR through optical equations |
| Future modality tool: Hyperspectral Analysis | EnMAP, PRISMA, EMIT mineral/spectral library analysis | Compatible cubes, spectral response, reference spectra, orthorectification | Specific L2 product/format and QA requirements; not first release promise |

**Never require running a separate Preparation or Mosaic tool first.** Every T01–T06 tool includes common input/preprocessing/mosaic/CRS/AOI/output/report flow; standalone administrative utilities may be added only as optional conveniences. Native `.pyt` grouping may not support a rich checkbox table; use ArcGIS Pro-supported parameters/ValueTable or optional C# add-in after actual host feasibility tests. Preserve equivalent QGIS UI behavior.

## 3. Common native tool parameter order
1. **Sensor / Product** (auto-detect from metadata if valid; explicit satellite and instrument selector; mismatch warning and safe stop).
2. **Imagery Input**: unpacked *single scene folder* or *parent folder* containing scene folders; select input data files only in expert mode; skip existing `Work`, `Results`, reports and hidden staging during discovery.
3. **Preprocessing**: appropriate band reflectance/radiance scaling and offsets, QA masks (cloud, shadow, snow, saturation, invalid), surface reflectance vs TOA vs DN detection, optional atmospheric/terrain methods only when authorized assets exist; 10/20/60m or other native-resolution alignment, NoData and grid tests. L2 must not be corrected twice.
4. **Mosaic**: optional default OFF; user asserts scenes form a study region. Include scene dates, sensors, overlaps, quality ranking, temporal warnings, source scene provenance. Default to per-scene computations then scientifically valid mosaic of outputs; each calculation may specialize ordering. Entire union if AOI omitted; user polygon for clipping independent.
5. **Tool-specific calculations**: grouped thematic categories, individual checkboxes, search, optional group select, default unchecked. Scientific details in tooltip; incompatible disabled with cause (missing band, unsupported product, required LST/time series/meteorology etc.).
6. **AOI & Projection**: polygon layer path (feature class, shapefile, GeoPackage) optional, optional AOI name; TRUE polygon clipping, not envelope. Output *projected CRS with metre units* from host GIS native CRS chooser. Prefer source if projected/metre/appropriate; no fixed EPSG or zone. Unknown source CRS requires explicit source definition before reprojection. Verify geodetic transformation and vertical DEM datum/units if used.
7. **Output options (LAST parameter)**: output folder default equals input scene (single) or selected parent (multiple); user may change folder. Output full and/or clip where configured. `Add Results to Map` optional (default OFF unless explicitly changed later), queued one-by-one with host event loop/validation; no fixed blocking sleeps; save products regardless of map-add outcome.

## 4. Folder and output semantics
### Single scene — output folder unchanged (default)
```text
SCENE_DIR/
  <unmodified_original_assets>
  Work/Preprocessing_Cache/...      # private reusable derived cache
  Results/
    Spectral_Indices/Vegetation/NDVI/NDVI_SCENEID_FULL.tif
    Spectral_Indices/Vegetation/NDVI/NDVI_SCENEID_AOI-SLUG_CLIP.tif
    Surface_Temperature/LST/...
    Thermal_Analysis/...  Geological_Analysis/...  Environmental_Analysis/...
    Reports/index.html
    Reports/Calculations/...
    Reports/Runs/RUNID/Processing_Manifest.json, Parameters.json, Quality_Assessment.csv, Processing_Log.txt
```

If user chooses a DIFFERENT output root, create `<CUSTOM_DEST>/<SCENE_FOLDER_NAME>/Work` and `Results`, without copying raw scene assets. For multiple scenes without mosaic, default per-scene Work/Results; if custom destination, use `<CUSTOM_DEST>/<SCENE_NAME>/Work` and `Results` for each. For multi-scene mosaic, put combined `Results/Mosaic_<stable-scene-set-id>/...` at parent output root; preserve individual results. Never create `Results_2` when `Results` exists. Do not conflict with raw source paths. Collisions resolved with exact source IDs and immutable run/version IDs, never silent overwrite.

### Additive workspace integrity
- `Work` cache reused only if source fingerprint, inputs, CRS, masks, methods, engine versions and validity checks match; missing metadata means reprocess or mark uncertain.
- `Results` reused as container; a same-name product from changed settings must version by run/parameter hash while preserving old output.
- Atomic or transactional raster writes and concurrency locks; interrupted jobs resume verified outputs and isolate partial files. No deletion of existing user data.
- Full output and clipped output in same index directory with unambiguous names. Mosaic must retain `Source_Scene_ID.tif` where meaningful and a scene/date provenance table. No blind averaging of LST from incompatible dates or sensor harmonization assumptions.

## 5. Sensor discovery, levels, and expert mapping
- Recognize Landsat 1–3 MSS, Landsat 4–5 MSS/TM, Landsat 7 ETM+, Landsat 8 OLI/TIRS, Landsat 9 OLI-2/TIRS-2; Sentinel-2 MSI A/B/C; ASTER VNIR/SWIR/TIR; targeted later Sentinel-3, MODIS, VIIRS, ECOSTRESS, EnMAP, PRISMA, EMIT and SAR modalities.
- Sensor support is **(sensor, processing-level, acquisition-date, product-version, actual-band-assets)** specific, not broad sensor label alone.
- Landsat C2 L2 SR `reflectance = DN*0.0000275-0.2` for valid reflectance pixels; ST `K = DN*0.00341802+149.0`, Celsius `K-273.15`; values must be verified against product metadata/guide, QA and NoData, never scaled twice.
- Sentinel-2 L2A (BOA) is preferred for reflectance indices; L1C (TOA) must not be silently treated as L2A. Sentinel-2 MSI has **no thermal bands**; Sentinel-2 10/20/60m resolutions require harmonized grid.
- MSS has no SWIR/TIR, hence disable SWIR ratios and LST. Landsat 7 post-2003 SLC-off may have coverage gaps. ASTER SWIR acquisitions after April 2008 generally invalid; ASTER TIR acquisitions ended Jan 16, 2026, but earlier archive remains usable.
- Manual Band Mapping expert mode: confirm satellite/sensor/product level; list required physical roles with expected band number and approx center wavelength; user maps exact files. Validate CRS/extent/grid, band integrity and unit provenance, scaling/offset, radiance/reflectance/brightness temperature. Do not invent calibration coefficients. Record all user-specified mappings and disable unsafe results.

## 6. Spectral formula registry
The stable scientific index ID, NOT the acronym, uniquely identifies a method. A variant can use the same acronym but a distinct wavelength/formula. Store names ar/en; acronym; scientific title; category; formula; roles; wavelength ranges; sensor-level constraints; constants; known numeric stability; official reference DOI/URL; version/license; validation state. `candidate_indices.json` contains **proposals only**. The index catalog from Awesome Spectral Indices (MIT) may be pinned/imported after license/schema review; IDB may be referenced/queried under its current terms but **never fully redistributed**. Geological/mineral identification remains probabilistic/diagnostic unless confirmed by ground truth.

## 7. Physical model requirements
- LST ≠ brightness temperature ≠ 2 m air temperature. LSE may derive from official product or approved NDVI threshold method, scientifically documented; no mandatory DEM unless a specific terrain/elevation correction requires it. Preferred official L2 ST unless user selects validated derivation method.
- Heat islands require urban-vs-reference surface definitions; hotspot statistics require reference frame/threshold logged; UTFVI formula and normalization convention explicitly recorded.
- TCI/VCI/VHI need a justified historical baseline (not arbitrary single-image extrema), TVDI needs dry/wet edges and adequately sampled feature space; ETa/SEBAL/METRIC needs meteorological and other inputs. Disable rather than synthesize missing inputs.
- Cross-sensor temporal/harmonization and quality-aware mosaic are independent of visual color balancing. No cloud-shadow contamination or invalid NoData smoothing.

## 8. Reporting + localization + help
For EACH output keep: original scene ID and time, sensor/instrument/level, actual band file names, band roles/wavelengths, formulas, constants and whether from metadata file:key vs reference vs user input, scaling offsets, QA/masks, preprocess list (performed/skipped/reason), grid, CRS & transformation, resolution/thermal native resolution, AOI and mosaic policy, source-ID provenance, output units, validity/uncertainty, errors/warnings and citation. File names are short and unambiguous. User summary + technical HTML/JSON/CSV/MD log, bilingual. Reports index cumulatively updates across tools without erasing prior reports.

Help: offline-first Markdown source EN/AR; generated HTML site `docs/index.html`, optional Windows `.chm` compiled help, ArcGIS Pro native parameter/tool help and QGIS help. Help shows sensor guide and provider download links, complete index cards, processing caveats, glossary, tutorials/screenshots, troubleshooting. Do not claim CHM/site is built until generated and tested. Translation excludes scientific internal IDs and sensor/product abbreviations.

## 9. Rendering and performance
Processing should use windowed/block operations, NoData-safe masking, memory and disk preflight, multithreading when safe, task cancellation, time/space estimates based on checked scene sizes not invented runtime, safe cache and resume; only one-at-a-time map addition on host's UI/event loop. Report failures without invalidating already verified saved data.

## 10. Distribution and community
MIT source code; user must separately provide licensed ArcGIS Pro (not bundled), or use QGIS free edition when adapter is implemented. Explicit OS/Python/ArcGIS Pro/QGIS supported version matrix; versioned dependencies, release notes, tests, reproducible examples and archive releases. Never bundle proprietary imagery, restricted index data, paid icons, API secrets or third-party incompatible code. GitHub issues and PR templates mandatory.

## 11. Scientific validation and release gates
- Verify formula algebra with independent numeric fixtures and full citation.
- Validate physical units, actual product metadata scales, QA bits, sensor band mapping, resolution/CRS/NoData/optical vs thermal.
- Test single-scene, multi-scene per-scene, mosaic ON/OFF, AOI FULL/CLIP, custom output path, crash/restart, duplicated runs, source asset protection.
- Test ArcGIS Pro `.pyt` parameter updates, readback, layer-add, i18n; QGIS Processing plugin version compatibility and native CRS picker separately; large raster stress and cross-platform paths.
- Evidence scale: T0 docs/static, T1 offline fixtures, T2 native host tests, T3 real product and output readback, T4 clean-environment installed workflow. Declared support needs its appropriate tier; do not substitute mock for native proof.
- Update plan/report indexes and journal after every phase. See [`DEVELOPMENT_ROADMAP.md`](DEVELOPMENT_ROADMAP.md) and [`AGENTS.md`](AGENTS.md).
