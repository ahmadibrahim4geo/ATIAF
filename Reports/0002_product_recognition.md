# Development Report 0002 — Product Recognition, Scene Discovery & Metadata Extraction Core
- **Date:** 2026-11-14
- **Plan ID:** PLAN-0002 (revision r1)
- **Status:** VERIFIED-COMPLETED
- **Phase:** P1 — Product Recognition & Metadata Extraction

## 1. Summary of Actions
1. **Core Data Models (`atyaf_core/discovery/models.py`):**
   - Implemented standard enumerated roles `BandRole` covering Coastal Aerosol, Blue, Green, Red, RedEdge (1-3), NIR, Narrow NIR, SWIR (1-2), Thermal (1-2), QA Pixel, QA Radsat, and SCL.
   - Implemented `ProductLevel` covering L1_MSS, L1C_TOA, L2A_BOA, L2_SR, L2_ST, L1T, AST_07, AST_08.
   - Built dataclasses `BandAsset`, `QualityAsset`, `SceneMetadata`, and `SceneInfo` encapsulating file paths, resolutions, wavelengths, physical units, scaling factors, offsets, and quality flags.
2. **USGS Landsat Parser (`atyaf_core/discovery/landsat.py`):**
   - Implemented auto-detection and parsing for Landsat 8/9 OLI/TIRS, Landsat 7 ETM+, Landsat 4/5 TM (Collection 2 Level-2 SR/ST), and Landsat 1-5 MSS Level-1.
   - Extracted acquisition timestamps, sun elevation, azimuth, and cloud cover from MTL metadata (`*_MTL.txt` and `*_MTL.json`).
   - Hardcoded verified USGS C2 calibration coefficients: Surface Reflectance scale `0.0000275`, offset `-0.20`; Surface Temperature scale `0.00341802`, offset `149.0` (Kelvin).
   - Enforced physical warnings: Landsat MSS lacks SWIR and Thermal bands; Landsat 7 acquired after May 2003 has SLC-off scan-line gap warnings.
3. **Copernicus Sentinel-2 Parser (`atyaf_core/discovery/sentinel2.py`):**
   - Implemented parsing for `.SAFE` hierarchical directory structures as well as flat unpacked folders.
   - Extracted XML metadata from `MTD_MSIL2A.xml` and `MTD_MSIL1C.xml` (platform S2A/S2B/S2C, sensing time, solar angles, cloud cover).
   - Multi-resolution band identification (10m, 20m, 60m) prioritizing optimal analysis resolutions.
   - Mapped categorical Scene Classification Layer (`SCL`) with class definitions.
   - **Strict Scientific Rule Enforced:** Sentinel-2 MSI contains NO thermal band; LST calculations are strictly flagged as unsupported (`NO_THERMAL`).
   - Level-1C (TOA) products emit a clear warning that they are top-of-atmosphere and not surface reflectance.
4. **NASA ASTER Parser (`atyaf_core/discovery/aster.py`):**
   - Implemented parsing for ASTER L1T, AST_07 (Surface Reflectance), and AST_08 (Kinetic Temperature).
   - **Strict Physical Rule Enforced:** ASTER SWIR subsystem degradation cutoff (April 2008). Scenes acquired after April 2008 automatically disable SWIR bands (B4-B9) for mineral/alteration ratios and emit `ASTER_SWIR_INVALID_POST_2008`.
   - Recorded TIR mission operational cessation notice (January 16, 2026).
5. **Scene & Directory Scanner (`atyaf_core/discovery/scanner.py`):**
   - Supports both single-scene folder input and multi-scene parent directories.
   - Automatically and strictly ignores `Work/`, `Results/`, `Reports/`, and hidden directories during scanning.
6. **Expert Manual Band Mapper (`atyaf_core/discovery/manual_mapper.py`):**
   - Allows advanced users to manually assign physical roles, custom scaling factors, offsets, and wavelengths to arbitrary raster files.
7. **Synthetic Fixtures & Automated Tests (`tests/test_product_recognition.py`):**
   - Built offline synthetic scene fixtures for Landsat 8, Landsat 7, Sentinel-2 L2A, Sentinel-2 L1C, ASTER pre-2008, ASTER post-2008, and multi-scene parent directory.
   - Created 9 comprehensive test cases in `tests/test_product_recognition.py`; 15 total unit tests across the test suite passing.

## 2. Exact Commands and Observed Outputs
### A. Generation of synthetic test fixtures
```text
PS D:\My Software\ATIAF> python tests/fixtures/create_synthetic_fixtures.py
Synthetic fixtures created successfully.
```

### B. Unit tests execution
```text
PS D:\My Software\ATIAF> python -m unittest tests/test_product_recognition.py
.........
----------------------------------------------------------------------
Ran 9 tests in 0.011s

OK
```

### C. Full test suite execution
```text
PS D:\My Software\ATIAF> python -m unittest discover tests
...............
----------------------------------------------------------------------
Ran 15 tests in 0.589s

OK
```

### D. Package validation check
```text
PS D:\My Software\ATIAF> python tools/validate_package.py
Candidate indices: 26
Planned sensors: 19
Markdown files: 281 JSON: 96
STRUCTURAL VALIDATION PASS — documentation only. Native ArcGIS/QGIS tests NOT RUN.
```

## 3. Test Evidence Table (DoneProof)
| Criterion | Expected Result | Observed Evidence | Outcome |
|---|---|---|---|
| Landsat 8 C2 L2 | Auto-detects OLI_TIRS, extracts SR/ST bands and scales | All bands found; SR scale=0.0000275, ST scale=0.00341802; thermal=True | VERIFIED |
| Landsat 7 SLC-off | Detects ETM post-May 2003 and issues warning | Warning present: "Landsat 7 acquired after May 2003 has SLC-off scan-line gaps" | VERIFIED |
| Sentinel-2 L2A | Detects MSI BOA, 10m/20m bands, SCL mask, NO thermal | Bands B02-B12 discovered; has_thermal()=False; warning "NO thermal bands" | VERIFIED |
| Sentinel-2 L1C | Identifies TOA and warns against treating as L2A | Level L1C_TOA detected; restriction "TOA_ONLY_WARNING" recorded | VERIFIED |
| ASTER Pre-2008 | Full VNIR and SWIR bands available | 2005-05-20 scene has valid SWIR_1 and SWIR_2 bands | VERIFIED |
| ASTER Post-2008 | SWIR bands disabled due to cooler failure | 2012-05-20 scene has SWIR disabled; restriction "ASTER_SWIR_INVALID_POST_2008" | VERIFIED |
| Scene Scanner | Scans parent folder while ignoring Work/Results | Discovered exactly 2 scenes; Work, Results, Reports ignored | VERIFIED |
| Manual Band Mapper | Creates validated custom SceneInfo | Expert mapped scene created with user scale 0.0001, expert_mapped=True | VERIFIED |
| Automated tests | All tests pass in `tests/test_product_recognition.py` | 9 tests passed (Ran 9 tests in 0.011s, OK) | VERIFIED |
| Native GIS tools | In-host execution | Deferred to Phase P3 (ArcGIS Pro) and P7 (QGIS) | NOT RUN / AS PLANNED |

## 4. Science QA and Physics Constraints
- **Landsat Collection 2:** Reflectance `SR = DN * 0.0000275 - 0.2`; Surface Temperature `ST = DN * 0.00341802 + 149.0` (Kelvin). Values checked against USGS Data Format Control Book.
- **Sentinel-2 L2A:** Scaling `0.0001` applied; strictly no thermal capabilities; SCL pixel classification preserved.
- **ASTER SWIR Rule:** Enforced historical degradation date (April 2008) preventing erroneous geological mineral mapping on broken detectors.
- **Cleanliness:** No network calls, no cloud credentials required during local file parsing; zero destruction of source files.

## 5. Files Changed or Created
- `atyaf_core/__init__.py` (created)
- `atyaf_core/discovery/__init__.py` (created)
- `atyaf_core/discovery/models.py` (created)
- `atyaf_core/discovery/landsat.py` (created)
- `atyaf_core/discovery/sentinel2.py` (created)
- `atyaf_core/discovery/aster.py` (created)
- `atyaf_core/discovery/scanner.py` (created)
- `atyaf_core/discovery/manual_mapper.py` (created)
- `tests/fixtures/create_synthetic_fixtures.py` (created)
- `tests/fixtures/synthetic_scenes/` (fixtures generated)
- `tests/test_product_recognition.py` (created)
- `Development_Plans/Active/PLAN-0002_product_recognition.md` (created)
- `Development_Plans/INDEX.md` (updated)
- `Reports/0002_product_recognition.md` (created)
- `Reports/INDEX.md` (updated)
- `PROJECT_STATE.md` (updated)

## 6. Next Steps & Handoff
- **Phase P1 is complete.**
- Next milestone: **Phase P2 (Core Raster, CRS, Masks & Output Manager)**:
  - Implement `atyaf_core/raster/` for windowed raster processing using rasterio / numpy.
  - Implement QA pixel masking (cloud, shadow, dilated cloud, cirrus, snow, water).
  - Implement native projected-metre CRS validation and reprojection.
  - Implement AOI polygon clipping.
  - Implement the non-destructive append-only `Work/` (preprocessing cache) and `Results/` (hierarchical output) manager with run manifests.
