# Output naming, per-result provenance and scientific reports
**Directory policy:** shared `Results/` across tools and runs; names as simple as possible, IDs unique. Original input files remain untouched. Scene ID and acquisition timestamp come from verified product metadata, not guessed from names. Output full and clip in same calculation folder.

| Path/example | Purpose |
|---|---|
| `Results/Spectral_Indices/Vegetation/NDVI/NDVI_<SCENEID>_FULL.tif` | Original extent calculation, compressed GeoTIFF |
| `Results/Spectral_Indices/Vegetation/NDVI/NDVI_<SCENEID>_<AOI>_CLIP.tif` | Polygon-clipped calculation |
| `Results/Surface_Temperature/LST/LST_<SCENEID>_Celsius.tif` | LST, temperature unit explicitly named |
| `Results/Geological_Analysis/Clay_OH/CLAY_<SCENEID>_FULL.tif` | Geological proxy, not mineral confirmation |
| `Results/Reports/Calculations/NDVI_<RUNID>.html` | Human-readable formula, source and result |
| `Results/Reports/Runs/<RUNID>/Processing_Manifest.json` | Machine-readable full provenance, outputs, QA |
| `Results/Reports/Runs/<RUNID>/Band_Mapping.csv` | Per-input file physical role + wavelength + units |
| `Results/Reports/Runs/<RUNID>/Quality_Assessment.csv` | Valid pixels, cloud/shadow/snow exclusions, NoData, coverage |
| `Results/Reports/Runs/<RUNID>/Processing_Log.txt` | Runtime actions/warnings/errors with severity |
| `Results/Reports/index.html` | Cumulative index, never clobber previous runs |

### Example method report (illustration, NOT measured scene values)
**Output:** NDVI for a Landsat 8 OLI Collection 2 Level 2 scene.  **Formula:** `(NIR-Red)/(NIR+Red)`.  **Mapped assets:** `SR_B5`=NIR, `SR_B4`=Red. **Scaling:** `DN*0.0000275 -0.2` for USGS C2 L2 SR, with zero Fill excluded. **Provenance:** `metadata_source=USGS C2 L2 product specification` unless the particular scene MTL key/value was actually parsed, in which case record exact MTL filename/key/value. **Quality:** apply `QA_PIXEL` and `QA_RADSAT` as appropriate, masking exclusions. **Result type:** Float32, unitless; always preserve source native grid and resampling provenance. **Scientific reference:** NDVI original source (verified DOI to be supplied by implementation research).

### Required per-output fields
- `run_id`, `method_id`, method version, formula, formula original research citation, formula substitutions, constants/scale/offset with explicit source type (`metadata`, `scientific_reference`, `user_parameter`).
- Exact scene IDs, instrument, scene time/time zone and product processing baseline, full names/relative paths of source band files, actual band roles and nominal center wavelength.
- QA product and mask bits (names or values), correction steps performed/skipped with reason, `NoData` policy and denominator/mathematical-domain mask.
- Input and output CRS identifiers and WKT, transformation, pixel size, snap/grid, align resampling, sensor native thermal resolution and reprojected cell size.
- Mosaic scene list, acquisition time, overlap strategy and source-per-pixel, optional AOI file/geometry identifier, quality metrics and uncertainty/limitations.
- Output paths, data types, units, min/max only from measured raster readback, successful/failed tasks, error and warning codes, engine versions, user-facing language.
- Private full filesystem paths only in local reports, never by default in public Git history.
