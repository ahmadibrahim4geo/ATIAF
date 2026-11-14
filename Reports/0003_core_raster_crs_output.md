# Development Report 0003 — Core Raster Array Processing, CRS, Masks & Workspace Manager
- **Date:** 2026-11-14
- **Plan ID:** PLAN-0003 (revision r1)
- **Status:** VERIFIED-COMPLETED
- **Phase:** P2 — Core Raster, CRS, Masks & Output Manager

## 1. Summary of Actions
1. **Coordinate Reference System Validation (`atyaf_core/raster/crs_utils.py`):**
   - Implemented `CRSManager` adhering strictly to Decision D-007.
   - Enforces that output coordinate systems must be **projected** and have **metre units** (e.g. UTM, national metric projections).
   - Automatically detects and rejects geographic degree coordinate systems (e.g. WGS84 EPSG:4326) with an informative error message explaining that satellite raster calculations require metric spatial units.
   - Does not impose fixed global EPSG or UTM zones, enabling seamless integration with native host CRS pickers.
2. **Quality Assessment Masking Engine (`atyaf_core/raster/masks.py`):**
   - Implemented `QualityMaskEngine` for bitmask decoding and categorical filtering:
     - Landsat Collection 2 `QA_PIXEL`: isolates fill, dilated cloud, cirrus, cloud, cloud shadow, snow, and water.
     - Sentinel-2 `SCL` (Scene Classification Layer): isolates vegetation, bare soil, and water from clouds (medium/high probability), cloud shadows, thin cirrus, and snow.
   - Built `apply_valid_range_and_nodata` to safely assign `np.nan` to invalid pixels.
3. **True Polygon AOI Clipping (`atyaf_core/raster/clip.py`):**
   - Implemented `PolygonClipEngine` using `Shapely` and `rasterio.mask`.
   - Performs true polygon geometry boundary cuts (not mere bounding-box envelopes).
   - Validates and fixes self-intersecting geometries via `make_valid`.
   - Automatically transforms vector AOI geometries to the raster's native CRS using `pyproj.Transformer`.
   - Crops spatial dimensions and updates affine geotransform without corrupting NoData.
4. **Windowed Raster Processing & Atomic Writes (`atyaf_core/raster/windowed.py`):**
   - Implemented `WindowedRasterEngine` for memory-bounded, block-by-block processing of massive satellite imagery (configurable block size e.g. 512x512).
   - Computes multi-band mathematical operations on NumPy blocks.
   - Performs atomic writes using `.tmp_<filename>` temporary files; target destination is only written on verified successful completion.
   - On exception or interruption, automatically deletes incomplete temporary files, protecting existing user data.
   - Computes real-time streaming statistics (min, max, mean, standard deviation, valid pixel count, nodata count) during the write pass.
5. **Non-Destructive Workspace & Manifest Manager (`atyaf_core/raster/workspace.py`):**
   - Enforces the hierarchical directory layout:
     - `<ROOT>/Work/Preprocessing_Cache/`
     - `<ROOT>/Results/<Category>/<Method>/<Product>_<SCENE_ID>_FULL.tif`
     - `<ROOT>/Results/<Category>/<Method>/<Product>_<SCENE_ID>_<AOI>_CLIP.tif`
     - `<ROOT>/Results/Reports/Runs/<RUN_ID>/`
   - **Guaranteed Workspace Integrity:** Never creates `Results_2` or deletes prior user files.
   - Generates SHA-256 cache fingerprints based on input files, parameters, and CRS to enable skipping redundant computations.
   - Emits standardized execution run records: `Processing_Manifest.json`, `Parameters.json`, `Quality_Assessment.csv`, and `Processing_Log.txt`.
6. **Automated Unit & Readback Tests (`tests/test_raster_core.py`):**
   - Authored 14 comprehensive test cases covering CRS validation, QA masks, windowed computation, atomic write failure recovery, polygon clipping, and workspace manifests.
   - Total test suite now stands at 29 unit tests, all passing.

## 2. Exact Commands and Observed Outputs
### A. Unit test execution
```text
PS D:\My Software\ATIAF> python -m unittest tests/test_raster_core.py
..............
----------------------------------------------------------------------
Ran 14 tests in 0.236s

OK
```

### B. Full project test suite execution
```text
PS D:\My Software\ATIAF> python -m unittest discover tests
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.572s

OK
```

### C. Package validation check
```text
PS D:\My Software\ATIAF> python tools/validate_package.py
Candidate indices: 26
Planned sensors: 19
Markdown files: 285 JSON: 98
STRUCTURAL VALIDATION PASS — documentation only. Native ArcGIS/QGIS tests NOT RUN.
```

## 3. Test Evidence Table (DoneProof)
| Criterion | Expected Result | Observed Evidence | Outcome |
|---|---|---|---|
| Projected Metre CRS | Accepts UTM 36N, Web Mercator; rejects EPSG:4326 | EPSG:32636 accepted; EPSG:4326 rejected with explicit message | VERIFIED |
| Landsat QA Mask | Filters cloud, shadow, snow, dilated cloud, fill | Clear pixel valid (True); cloud, shadow, snow, fill invalid (False) | VERIFIED |
| Sentinel-2 SCL Mask | Filters clouds, shadows, cirrus, snow | Vegetation/soil/water valid (True); clouds/shadows invalid (False) | VERIFIED |
| Windowed Processing | Block-by-block computation with streaming stats | 64x64 GeoTIFF NDVI computed; streaming mean matches expected 0.6667 | VERIFIED |
| Atomic Writes | Cleans up temporary files on exception | On simulated crash, .tmp file deleted; target file never created | VERIFIED |
| Polygon Clipping | Cuts raster along exact polygon boundary | 40x40 clipped GeoTIFF created with updated transform and bounds | VERIFIED |
| Workspace Manager | Creates Work/Results without Results_2 | Repeated calls reuse Results directory; cache fingerprint reproducible | VERIFIED |
| Run Manifests | Generates JSON, CSV, and log in Reports/Runs/ | Processing_Manifest.json, Parameters.json, Quality_Assessment.csv created | VERIFIED |
| Full Test Suite | All tests pass in tests/ | 29 unit tests passed (Ran 29 tests in 0.572s, OK) | VERIFIED |
| Native GIS tools | In-host execution | Deferred to Phase P3 (ArcGIS Pro) and P7 (QGIS) | NOT RUN / AS PLANNED |

## 4. Science QA and Workspace Rules
- **Metric Integrity (Decision D-007):** Rejection of geographic coordinates prevents severe calculation distortion (e.g. calculating area or thermal variability in square degrees).
- **Physical Bounds:** Valid ranges and NoData handling preserve scientific integrity; NaNs and infinities are converted to standard floating-point NoData (-9999.0).
- **Data Preservation (Decision D-005):** Zero deletion or overwriting of raw satellite scenes or prior tool results.
- **Traceability (Decision D-011):** Every calculation run generates an immutable manifest with timestamp, parameters, output products, and quality assessment metrics.

## 5. Files Changed or Created
- `atyaf_core/raster/__init__.py` (created)
- `atyaf_core/raster/crs_utils.py` (created)
- `atyaf_core/raster/masks.py` (created)
- `atyaf_core/raster/clip.py` (created)
- `atyaf_core/raster/windowed.py` (created)
- `atyaf_core/raster/workspace.py` (created)
- `tests/test_raster_core.py` (created)
- `Development_Plans/Active/PLAN-0003_core_raster_crs_output.md` (created)
- `Development_Plans/INDEX.md` (updated)
- `Reports/0003_core_raster_crs_output.md` (created)
- `Reports/INDEX.md` (updated)
- `PROJECT_STATE.md` (updated)

## 6. Next Steps & Handoff
- **Phase P2 is complete.**
- Next milestone: **Phase P3 (ArcGIS Pro Independent Tools & Spectral Indices)**:
  - Implement native ArcGIS Pro Python Toolbox (`arcgis_pro/ATIAF.pyt`).
  - Wire parameter ordering: Sensor -> Input Scene/Parent -> Preprocessing -> Mosaic -> Calculations -> AOI & Projected CRS -> Output Folder.
  - Implement Tool 01 (Spectral Indices) with vegetation, water, soil, urban, burn, and snow indices.
  - Connect ArcGIS Pro host validator with `atyaf_core`.
