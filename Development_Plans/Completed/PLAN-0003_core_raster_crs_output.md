# PLAN-0003 — Core Raster Array Processing, CRS, Masks & Workspace Manager
- **Status:** VERIFIED-COMPLETED
- **Revision:** r1
- **Owner and date:** Implementation Agent, 2026-11-14
- **Original user request:** Execute Phase P2 of the ATIAF development roadmap: implement pure-Python raster engine `atyaf_core/raster/` supporting windowed block operations, QA pixel masking, native metre-based projected CRS validation and reprojection, true polygon AOI clipping, non-destructive `Work/` / `Results/` workspace manager with cache fingerprinting and atomic writes, and run manifests.
- **Scope and exclusions:**
  - Scope:
    - Windowed block-by-block raster reading, computing, and writing via Rasterio to support large satellite scenes with bounded memory.
    - Bitmask and categorical QA interpretation (`QA_PIXEL` for Landsat, `SCL` for Sentinel-2, ASTER QA) with NoData and valid range masking.
    - Coordinate reference system (CRS) validation enforcing metre-based projected coordinates, rejecting raw unprojected degrees (EPSG:4326), and handling reprojection without hardcoded EPSG defaults.
    - True polygon AOI clipping via Shapely and Rasterio with CRS alignment.
    - Additive, non-destructive `Work/` (preprocessing cache) and `Results/` (hierarchical output) manager with atomic writes, cache hashing, and run manifests.
    - Synthetic raster fixtures and comprehensive unit and readback tests in `tests/test_raster_core.py`.
  - Exclusions:
    - ArcGIS Pro `.pyt` GUI parameter wiring (Phase P3).
    - Specific spectral index algebraic formula catalog execution (Phase P3).
- **Dependencies and scientific sources:**
  - `PROJECT_SPECIFICATION.md` & `PROJECT_SPECIFICATION_AR.md` (Sections 3, 4, 7)
  - `DECISIONS.md` (D-004, D-005, D-006, D-007, D-011)
  - `skills/geospatial-data-processing/SKILL.md`
  - `skills/coordinate-reference-systems/SKILL.md`
  - `skills/remote-sensing-pipelines/SKILL.md`
  - `skills/gis-data-flow-diagnostics/SKILL.md`
  - `rasterio 1.5.2`, `numpy 2.5.3`, `shapely 2.1.2`, `pyproj 3.8.0`
- **Skills and links selected:**
  - [`skills/geospatial-data-processing/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/geospatial-data-processing/SKILL.md)
  - [`skills/coordinate-reference-systems/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/coordinate-reference-systems/SKILL.md)
  - [`skills/remote-sensing-pipelines/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/remote-sensing-pipelines/SKILL.md)
  - [`skills/gis-data-flow-diagnostics/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/gis-data-flow-diagnostics/SKILL.md)
  - [`skills/completion-evidence/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/completion-evidence/SKILL.md)
  - [`skills/agent-development-journal/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/agent-development-journal/SKILL.md)
- **Affected paths:**
  - `atyaf_core/raster/__init__.py`
  - `atyaf_core/raster/windowed.py`
  - `atyaf_core/raster/masks.py`
  - `atyaf_core/raster/crs_utils.py`
  - `atyaf_core/raster/clip.py`
  - `atyaf_core/raster/workspace.py`
  - `tests/test_raster_core.py`
  - `Development_Plans/Completed/PLAN-0003_core_raster_crs_output.md`
  - `Development_Plans/INDEX.md`
  - `Reports/0003_core_raster_crs_output.md`
  - `Reports/INDEX.md`
  - `PROJECT_STATE.md`
- **Execution steps:**
  1. Record request/plan in Agent Development Journal.
  2. Implement `atyaf_core/raster/crs_utils.py` for metre-unit projected CRS validation and reprojection.
  3. Implement `atyaf_core/raster/masks.py` for Landsat `QA_PIXEL` and Sentinel-2 `SCL` masking.
  4. Implement `atyaf_core/raster/clip.py` for true polygon clipping and extent cropping.
  5. Implement `atyaf_core/raster/windowed.py` for windowed block computation and atomic writing.
  6. Implement `atyaf_core/raster/workspace.py` for non-destructive `Work/` / `Results/` directory layout, hashing, and manifest generation.
  7. Author unit and readback tests in `tests/test_raster_core.py`.
  8. Run tests, verify evidence, author Report 0003, update indexes and `PROJECT_STATE.md`.
- **Acceptance criteria (testable):**
  - [x] Projected metre CRS validation accepts projected metre CRS (e.g. UTM) and rejects geographic degrees (EPSG:4326) with explicit error.
  - [x] QA mask evaluation correctly isolates clear pixels from cloud, shadow, and snow for both Landsat C2 and Sentinel-2 SCL.
  - [x] Polygon AOI clipping cuts raster along exact polygon boundary and updates affine transform without corrupting NoData.
  - [x] Windowed processing operates block-by-block and matches full-array calculations within numeric tolerance.
  - [x] Workspace manager never creates `Results_2`, generates predictable scene/run folders, writes manifests, and detects reusable cache via SHA-256 fingerprint.
  - [x] Atomic write mechanism prevents partial corrupted files on disk if writing is interrupted.
  - [x] All tests in `tests/test_raster_core.py` and prior tests pass cleanly.
  - [x] Report 0003 written and logged in the development journal.
- **Risk/rollback approach:**
  - Pure-Python implementation using verified local packages (`rasterio`, `pyproj`, `shapely`, `numpy`). Git commit checkpoints ensure safe rollbacks.
- **Reports:**
  - [`Reports/0003_core_raster_crs_output.md`](../../Reports/0003_core_raster_crs_output.md)
- **Revision log:**
  - r1 (2026-11-14): Initial plan creation for Phase P2 raster core. Completed with all 14 tests passing.
