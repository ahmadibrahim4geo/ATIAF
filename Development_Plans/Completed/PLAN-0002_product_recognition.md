# PLAN-0002 — Product Recognition, Scene Discovery & Metadata Extraction Core
- **Status:** VERIFIED-COMPLETED
- **Revision:** r1
- **Owner and date:** Implementation Agent, 2026-11-14
- **Original user request:** Execute Phase P1 of the ATIAF development roadmap: implement product recognition and metadata extraction with pure-Python `atyaf_core/discovery/` supporting Landsat 4-9 C2 L2, Sentinel-2 L2A, and ASTER, directory/parent scanning, band role and QA manifests, and expert manual band mapping.
- **Scope and exclusions:**
  - Scope:
    - Pure-Python core module `atyaf_core/discovery/` for scene identification, metadata extraction, band mapping, and QA mask identification.
    - Full parser support for Landsat Collection 2 Level-2 (Landsat 4-5 TM, Landsat 7 ETM+, Landsat 8 OLI/TIRS, Landsat 9 OLI-2/TIRS-2), Landsat 1-5 MSS Level-1, Sentinel-2 MSI L2A (with L1C detection/warning), and ASTER (L1T, AST_07, AST_08).
    - Single scene folder vs parent folder scanner that skips `Work/`, `Results/`, reports, and non-scene directories.
    - Physical model and temporal constraints enforcement (e.g. ASTER SWIR post-April 2008 degradation, S2 lack of thermal bands).
    - Expert manual band mapping data model and validation.
    - Synthetic scene fixtures in `tests/fixtures/synthetic_scenes/` and comprehensive unit tests in `tests/test_product_recognition.py`.
  - Exclusions:
    - Raster pixel array processing and windowed calculation engines are in Phase P2.
    - ArcGIS Pro `.pyt` UI parameters and QGIS plugin GUI are in Phases P3 and P7.
- **Dependencies and scientific sources:**
  - `PROJECT_SPECIFICATION.md` & `PROJECT_SPECIFICATION_AR.md` (Section 3, 5)
  - `DECISIONS.md` (D-003, D-004, D-008, D-019)
  - `scientific_library/sensors/sensor_registry.json`
  - USGS Landsat Collection 2 Level-2 Data Format Control Book
  - ESA Sentinel-2 Products Specification Document
  - NASA ASTER Product User Handbook
- **Skills and links selected:**
  - [`skills/remote-sensing-pipelines/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/remote-sensing-pipelines/SKILL.md)
  - [`skills/gis-development/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/gis-development/SKILL.md)
  - [`skills/geospatial-data-processing/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/geospatial-data-processing/SKILL.md)
  - [`skills/gis-data-flow-diagnostics/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/gis-data-flow-diagnostics/SKILL.md)
  - [`skills/completion-evidence/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/completion-evidence/SKILL.md)
  - [`skills/agent-development-journal/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/agent-development-journal/SKILL.md)
- **Affected paths:**
  - `atyaf_core/__init__.py`
  - `atyaf_core/discovery/__init__.py`
  - `atyaf_core/discovery/models.py`
  - `atyaf_core/discovery/scanner.py`
  - `atyaf_core/discovery/landsat.py`
  - `atyaf_core/discovery/sentinel2.py`
  - `atyaf_core/discovery/aster.py`
  - `atyaf_core/discovery/manual_mapper.py`
  - `tests/fixtures/synthetic_scenes/`
  - `tests/test_product_recognition.py`
  - `Development_Plans/Completed/PLAN-0002_product_recognition.md`
  - `Development_Plans/INDEX.md`
  - `Reports/0002_product_recognition.md`
  - `Reports/INDEX.md`
  - `PROJECT_STATE.md`
- **Execution steps:**
  1. Record request/plan in Agent Development Journal.
  2. Implement data models in `atyaf_core/discovery/models.py` (`BandRole`, `ProductLevel`, `SensorMetadata`, `BandAsset`, `QualityAsset`, `SceneInfo`).
  3. Implement Landsat parser in `atyaf_core/discovery/landsat.py` supporting C2 L2 (SR/ST), scaling coefficients, and QA bands.
  4. Implement Sentinel-2 parser in `atyaf_core/discovery/sentinel2.py` supporting L2A SAFE/flat formats, multi-resolution band roles, SCL, and L1C warnings.
  5. Implement ASTER parser in `atyaf_core/discovery/aster.py` with temporal SWIR constraint enforcement (post-2008 degradation).
  6. Implement scene scanner in `atyaf_core/discovery/scanner.py` for single scene or parent folder with `Work`/`Results` avoidance.
  7. Implement manual expert band mapping in `atyaf_core/discovery/manual_mapper.py`.
  8. Build synthetic fixtures in `tests/fixtures/synthetic_scenes/` (Landsat 8 L2, Sentinel-2 L2A, Sentinel-2 L1C, ASTER L1T/AST_07).
  9. Author and execute unit test suite in `tests/test_product_recognition.py`.
  10. Document results in Report 0002, update indexes and `PROJECT_STATE.md`, commit to Git.
- **Acceptance criteria (testable):**
  - [x] Auto-detection of Landsat 8/9 C2 L2 extracts correct metadata (scene ID, date, sun elevation, SR bands B1-B7, ST band B10, QA_PIXEL, scale/offset).
  - [x] Auto-detection of Sentinel-2 L2A extracts correct bands (B02-B04, B08, B05-B07, B8A, B11, B12), SCL mask, and confirms no thermal band exists.
  - [x] Sentinel-2 L1C produces explicit warning/rejection of surface reflectance equivalence.
  - [x] ASTER post-April 2008 SWIR bands correctly flagged as invalid/degraded.
  - [x] Scene scanner correctly identifies multiple scenes in a parent folder while ignoring `Work/`, `Results/`, and non-satellite directories.
  - [x] Manual band mapping interface validates role assignment, wavelengths, and user-supplied scaling.
  - [x] All unit tests in `tests/test_product_recognition.py` pass cleanly.
  - [x] Report 0002 written with exact commands and evidence; journal updated.
- **Risk/rollback approach:**
  - Standalone pure-Python code without native GIS host dependencies; safe offline tests using synthetic fixtures. Git commit checkpoints for safe rollback.
- **Reports:**
  - [`Reports/0002_product_recognition.md`](../../Reports/0002_product_recognition.md)
- **Revision log:**
  - r1 (2026-11-14): Initial plan creation for Phase P1 product recognition. Completed with all 9 tests passing.
