# PLAN-0004 — ArcGIS Pro Independent Tools & Tool 01 (Spectral Indices)
- **Status:** VERIFIED-COMPLETED
- **Revision:** r1
- **Owner and date:** Implementation Agent, 2026-11-14
- **Original user request:** Execute Phase P3 of the ATIAF development roadmap: implement the native ArcGIS Pro Python Toolbox (`arcgis_pro/ATIAF.pyt`) with canonical parameter ordering, dynamic parameter validation, and Tool 01 (Spectral Indices) connected to the core engine.
- **Scope and exclusions:**
  - Scope:
    - Pure-Python spectral indices registry in `atyaf_core/indices/registry.py` covering validated optical indices (NDVI, GNDVI, NDWI, MNDWI, NDBI, NBR, NDSI, SAVI, EVI, BSI).
    - Calculation execution engine in `atyaf_core/indices/engine.py` coordinating scene parsing, band role matching, QA masking, windowed processing, AOI clipping, and manifest generation.
    - Native ArcGIS Pro Python Toolbox (`arcgis_pro/ATIAF.pyt`) implementing Tool 01 (Spectral Indices | المؤشرات الطيفية) with the standard 8-parameter layout.
    - Dynamic parameter validation in `updateParameters` and `updateMessages` (metric projected CRS validation, conditional band capability gating, output path defaults).
    - Sequential and safe `Add Results to Map` handling via `arcpy.mp` when available.
    - Comprehensive unit tests in `tests/test_spectral_indices.py` validating index algebra, gating logic, and toolbox interface structure.
  - Exclusions:
    - Surface Temperature and Thermal tools (Phase P4).
    - QGIS Processing adapter (Phase P7).
- **Dependencies and scientific sources:**
  - `PROJECT_SPECIFICATION.md` & `PROJECT_SPECIFICATION_AR.md` (Sections 2, 3, 4, 6)
  - `DECISIONS.md` (D-002, D-003, D-005, D-006, D-007, D-008, D-009, D-010, D-011)
  - `skills/arcgis-toolbox-engineering/SKILL.md`
  - `skills/coordinate-reference-systems/SKILL.md`
  - `skills/remote-sensing-pipelines/SKILL.md`
  - `scientific_library/indices/candidate_indices.json`
- **Skills and links selected:**
  - [`skills/arcgis-toolbox-engineering/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/arcgis-toolbox-engineering/SKILL.md)
  - [`skills/coordinate-reference-systems/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/coordinate-reference-systems/SKILL.md)
  - [`skills/remote-sensing-pipelines/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/remote-sensing-pipelines/SKILL.md)
  - [`skills/geospatial-data-processing/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/geospatial-data-processing/SKILL.md)
  - [`skills/completion-evidence/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/completion-evidence/SKILL.md)
  - [`skills/agent-development-journal/SKILL.md`](../../.agent_resources/GIS-Development-Skills/skills/agent-development-journal/SKILL.md)
- **Affected paths:**
  - `atyaf_core/indices/__init__.py`
  - `atyaf_core/indices/registry.py`
  - `atyaf_core/indices/engine.py`
  - `arcgis_pro/ATIAF.pyt`
  - `tests/test_spectral_indices.py`
  - `Development_Plans/Completed/PLAN-0004_arcgis_pro_spectral_indices.md`
  - `Development_Plans/INDEX.md`
  - `Reports/0004_arcgis_pro_spectral_indices.md`
  - `Reports/INDEX.md`
  - `PROJECT_STATE.md`
- **Execution steps:**
  1. Record request/plan in Agent Development Journal.
  2. Implement `atyaf_core/indices/registry.py` with validated spectral index formulas and required band roles.
  3. Implement `atyaf_core/indices/engine.py` bridging discovery, QA masks, windowed computation, and workspace manifests.
  4. Implement `arcgis_pro/ATIAF.pyt` with canonical parameter order, dynamic validation, and safe execution.
  5. Author unit and integration tests in `tests/test_spectral_indices.py`.
  6. Execute tests and record results with full command outputs.
  7. Author Report 0004, update indexes and `PROJECT_STATE.md`.
- **Acceptance criteria (testable):**
  - [x] Validated index formulas (NDVI, GNDVI, NDWI, MNDWI, NDBI, NBR, NDSI, SAVI, BSI) compute correctly against synthetic numeric fixtures.
  - [x] Gating logic disables indices when required physical bands are missing (e.g. SWIR indices on Landsat MSS).
  - [x] End-to-end spectral index calculation on synthetic Landsat 8 and Sentinel-2 scenes produces valid GeoTIFFs, manifests, and logs.
  - [x] ArcGIS Pro `.pyt` parses cleanly without syntax errors and defines the 8 canonical parameters in exact order.
  - [x] Parameter validator enforces projected metre CRS and rejects geographic degree systems (EPSG:4326).
  - [x] All tests in `tests/test_spectral_indices.py` and prior test suites pass cleanly.
  - [x] Report 0004 written and recorded in development journal.
- **Risk/rollback approach:**
  - Thin ArcPy adapter separating ArcGIS Pro parameter plumbing from pure-Python core logic. All unit tests run headlessly. Git checkpoints enable safe rollbacks.
- **Reports:**
  - [`Reports/0004_arcgis_pro_spectral_indices.md`](../../Reports/0004_arcgis_pro_spectral_indices.md)
- **Revision log:**
  - r1 (2026-11-14): Initial plan creation for Phase P3 ArcGIS Pro toolbox and spectral indices. Completed with all 11 tests passing.
