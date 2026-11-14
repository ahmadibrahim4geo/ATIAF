# Changelog — ATIAF | أطياف

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-11-14

### Added
- **Phase P0 (Governance & Bootstrap):**
  - Project governance following mandatory 10-step lifecycle and append-only agent development journal.
  - Integration with user-owned GIS Development Skills repository.
  - Structural package validation suite (`tools/validate_package.py`).
- **Phase P1 (Product Recognition & Metadata Core):**
  - Multi-sensor discovery engine (`atyaf_core/discovery/`): Landsat 1–9 Collection 2, Sentinel-2 L2A/L1C, and ASTER.
  - Recursive directory scanner (`SceneScanner`) ignoring private staging directories.
  - Manual band mapping expert fallback (`ManualBandMapper`).
  - Synthetic scene fixtures for reliable offline test suites.
- **Phase P2 (Core Raster, CRS, Masks & Workspace Manager):**
  - Memory-efficient block/windowed raster processing engine (`WindowedRasterEngine`).
  - Strict enforcement of Decision D-007: rejection of unprojected geographic degrees (EPSG:4326) and validation of metric projected CRS (`CRSManager`).
  - Quality mask engine (`QualityMaskEngine`) decoding Landsat QA_PIXEL bitmasks and Sentinel-2 Scene Classification Layer (SCL).
  - True polygon AOI vector clipping (`PolygonClipEngine`) using Shapely and rasterio mask.
  - Additive, non-destructive workspace manager (`WorkspaceManager`) maintaining `Work/` cache and `Results/` with run manifests (`Processing_Manifest.json`).
- **Phase P3 (ArcGIS Pro .pyt & Tool 01 Spectral Indices):**
  - Native ArcGIS Pro Python Toolbox (`arcgis_pro/ATIAF.pyt`) with dynamic validation and canonical parameter layout.
  - Tool 01: Spectral Indices engine (`atyaf_core/indices/`) supporting 14 core optical indices with capability gating.
- **Phase P4 (Surface Temperature & Geological Analysis):**
  - Tool 02: Surface Temperature engine (`atyaf_core/temperature/`) calculating LST in Kelvin and Celsius and Emissivity (LSE) via Sobrino et al. (2004) NDVI thresholds model.
  - Strict blocking of thermal calculations on sensors lacking thermal channels (Sentinel-2).
  - Tool 05: Geological Analysis engine (`atyaf_core/geology/`) with 8 diagnostic alteration ratios and ASTER post-April 2008 SWIR degradation cutoff.
- **Phase P5 (Multi-Scene Mosaic & Temporal Change Detection):**
  - Quality-aware multi-scene mosaic blending engine (`QualityMosaicEngine`) with union extent calculations, quality ranking, and `Source_Scene_ID.tif` provenance tracking.
  - Tool 06: Temporal Change Detection engine (`atyaf_core/temporal/`) calculating dNDVI, dNBR with official USGS FIREMON 7-class Burn Severity classification, relative change %, and standard deviation anomaly mapping.
- **Phase P6 (Expanded Catalog, Thermal Urban & Environmental Drought):**
  - Expanded optical index catalog to 22 validated indices (NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW).
  - Tool 03: Thermal Urban engine (`atyaf_core/urban/`) with Urban Thermal Field Variance Index (UTFVI; 6-class ecological comfort), thermal anomaly hotspots ($z \ge 2.0$), and SUHI.
  - Tool 04: Environmental Drought engine (`atyaf_core/environment/`) with Liang (2001) broadband shortwave surface albedo ($\alpha$) and Temperature Vegetation Dryness Index (TVDI).
- **Phase P7 (Native QGIS Processing Provider Adapter):**
  - Complete QGIS Processing Provider plugin package (`qgis/atyaf/`) with `metadata.txt`, `classFactory`, provider ID `atyaf`, and all 6 processing algorithms.
  - Tested natively inside QGIS 4.2.3 via `python-qgis.bat`.
- **Phase P8 (Advanced Modalities, SAR & Hyperspectral Gating):**
  - Advanced sensor modality architecture (`atyaf_core/modalities/`).
  - SAR engine (`SAREngine`) enforcing the non-negotiable rule: *"Never route SAR through optical equations"*, linear-to-dB conversion, cross-polarization ratio, dual-pol RVI, and pure-NumPy Lee speckle filter.
  - Hyperspectral engine (`HyperspectralEngine`) with Spectral Angle Mapper (SAM) in float64, continuum-removed diagnostic absorption feature depths (2205 nm, 2345 nm, 900 nm), and Level-2 surface reflectance cube gating.
  - Copernicus Sentinel-1 C-SAR parser (`Sentinel1Parser`) recognizing `.SAFE` GRD/SLC products.
  - Comprehensive bilingual documentation in `docs/en/ADVANCED_MODALITIES.md` and `docs/ar/ADVANCED_MODALITIES.md`.
- **Phase P9 (Packaging, Documentation Build & Release Readiness):**
  - PEP 517/518/621 `pyproject.toml` configuration enabling `pip install -e .`.
  - CLI diagnostic and verification utility (`atyaf-verify` / `tools/verify_installation.py`).
  - Responsive, modern bilingual offline documentation portal (`docs/index.html`).
  - User documentation and walkthroughs in `README.md` and `README.ar.md`.
