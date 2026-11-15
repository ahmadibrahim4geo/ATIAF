# PLAN-0005 — Surface Temperature & Geological / Mineral Analysis (Tools 02 & 05)
- **Status:** COMPLETED
- **Revision:** r1
- **Owner and date:** Implementation Agent, 2026-11-14
- **Original user request:** Execute Phase P4 of the ATIAF development roadmap: implement Tool 02 (Surface Temperature) and Tool 05 (Geological & Mineral Analysis) in `atyaf_core` and expose them as independent native tools within `arcgis_pro/ATIAF.pyt`.
- **Scope and exclusions:**
  - Scope:
    - Pure-Python thermal module `atyaf_core/temperature/` supporting official L2 ST products (Landsat C2 ST, ASTER AST_08), NDVI-threshold Land Surface Emissivity (LSE / $P_v$), Brightness Temperature (BT), and Kelvin/Celsius conversions.
    - Strict physical rule: Sentinel-2 lacks thermal bands and cannot compute LST.
    - Pure-Python geological module `atyaf_core/geology/` supporting Iron Oxides, Ferric/Ferrous Iron, Clay/Hydroxyl alteration, Gossan, and ASTER thermal indices (Quartz Index, Carbonate Index, Mafic Index).
    - Enforce ASTER post-April 2008 SWIR restriction disabling degraded clay/hydroxyl ratios.
    - Native ArcGIS Pro tools in `arcgis_pro/ATIAF.pyt`:
      - `SurfaceTemperatureTool` (02. Surface Temperature | درجة حرارة السطح)
      - `GeologicalAnalysisTool` (05. Geological & Mineral Analysis | التحليلات الجيولوجية والمعادن)
    - Comprehensive unit and integration tests in `tests/test_temperature_geology.py`.
  - Exclusions:
    - Multi-scene mosaic blending and change detection (Phase P5).
    - QGIS Processing provider (Phase P7).
- **Dependencies and scientific sources:**
  - `PROJECT_SPECIFICATION.md` & `PROJECT_SPECIFICATION_AR.md` (Sections 2, 3, 4, 7)
  - `DECISIONS.md` (D-002, D-003, D-007, D-011, D-018, D-020)
  - Sobrino et al. (2004), Land surface temperature retrieval from LANDSAT TM 5
  - Artis & Carnahan (1982), Survey of ground temperature via satellite
  - Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data
  - USGS Landsat Collection 2 Surface Temperature Product Guide
- **Skills and links selected:**
  - [`skills/remote-sensing-pipelines/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/remote-sensing-pipelines/SKILL.md)
  - [`skills/arcgis-toolbox-engineering/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/arcgis-toolbox-engineering/SKILL.md)
  - [`skills/geospatial-data-processing/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/geospatial-data-processing/SKILL.md)
  - [`skills/coordinate-reference-systems/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/coordinate-reference-systems/SKILL.md)
  - [`skills/completion-evidence/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/completion-evidence/SKILL.md)
  - [`skills/agent-development-journal/SKILL.md`](https://github.com/ahmadibrahim4geo/GIS-Development-Skills/blob/2a0a9a23618e40218484ec8ae5848a481df51f1a/skills/agent-development-journal/SKILL.md)
- **Affected paths:**
  - `atyaf_core/temperature/__init__.py`
  - `atyaf_core/temperature/emissivity.py`
  - `atyaf_core/temperature/engine.py`
  - `atyaf_core/geology/__init__.py`
  - `atyaf_core/geology/registry.py`
  - `atyaf_core/geology/engine.py`
  - `arcgis_pro/ATIAF.pyt`
  - `tests/test_temperature_geology.py`
  - `Development_Plans/Completed/PLAN-0005_surface_temperature_geological.md`
  - `Development_Plans/INDEX.md`
  - `Reports/0005_surface_temperature_geological.md`
  - `Reports/INDEX.md`
  - `PROJECT_STATE.md`
- **Execution steps:**
  1. Record request/plan in Agent Development Journal.
  2. Implement `atyaf_core/temperature/emissivity.py` for NDVI-based LSE estimation.
  3. Implement `atyaf_core/temperature/engine.py` for LST calculation, thermal gating, and Kelvin/Celsius conversion.
  4. Implement `atyaf_core/geology/registry.py` and `engine.py` with optical and thermal mineral indices and SWIR degradation checks.
  5. Update `arcgis_pro/ATIAF.pyt` to include Tool 02 and Tool 05 with canonical parameters and dynamic validation.
  6. Author and run unit tests in `tests/test_temperature_geology.py`.
  7. Author Report 0005, update indexes and `PROJECT_STATE.md`.
- **Acceptance criteria (testable):**
  - [x] Surface temperature calculation extracts accurate Kelvin and Celsius values from Landsat C2 L2 ST ($DN \times 0.00341802 + 149.0 - 273.15$).
  - [x] Sentinel-2 scenes are strictly blocked from LST with clear error notification (`NO_THERMAL`).
  - [x] NDVI-based emissivity calculation outputs valid emissivity values ($0.97 \le \varepsilon \le 0.99$).
  - [x] Geological indices (Iron Oxide, Ferrous, Clay, ASTER QI, CI, MI) compute accurately against test fixtures.
  - [x] ASTER post-April 2008 SWIR degradation cutoff disables clay/hydroxyl alteration indices with explicit warning.
  - [x] `arcgis_pro/ATIAF.pyt` exposes Tool 01, Tool 02, and Tool 05 with valid parameter configurations.
  - [x] All tests in `tests/test_temperature_geology.py` and prior test suites pass cleanly.
  - [x] Report 0005 written and recorded in development journal.
- **Risk/rollback approach:**
  - Standalone pure-Python core algorithms verified against synthetic fixtures. Git checkpoints provide clean rollback.
- **Reports:**
  - [`Reports/0005_surface_temperature_geological.md`](../../Reports/0005_surface_temperature_geological.md)
- **Revision log:**
  - r1 (2026-11-14): Initial plan creation and full verification for Phase P4 temperature and geology.
