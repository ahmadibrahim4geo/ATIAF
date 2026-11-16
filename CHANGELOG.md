# Change log

## 1.0.5.dev0 — 2026-11-17 Intelligent QA Mask Engine & Advanced ENVI Indices Integration

- Intelligent Quality Mask Engine: 4 granular operational modes (`Cloud_Only_Arid` default, `Full_Strict`, `Water_Protected`, `None`). Completely eliminates "missing cells / white holes" over desert mountains (23,676 rock pixels recovered) and deep river channels.
- Clamped optical negative reflectance to $\epsilon = 0.0001$ across indices, geology, environment, and composites engines to prevent NaN and division-by-zero artifacts.
- Advanced NV5 ENVI 6.3 & Geoscience Indices: 6 new indices fully integrated (`MTVI2`, `MCARI2`, `NDRE2`, `CIGREEN`, `CIREDEDGE`, `NDSI_SALINITY`) with dependency-free catalog definitions, compute functions, and bilingual interpretations.
- Usability Overhaul: Added optional Study Area Name across all 7 tools, producing clean short output filenames `[<StudyArea>_]<Method>_<YYYYMMDD>.tif` without UUID clutter.
- Simplified Surface Temperature: Defaulted RTE and Planck parameters with automatic computation and saving of intermediate NDVI to `Results/Vegetation/NDVI/`.
- Simplified Geological Presets (`7-5-3`, `7-6-2`, `CRC1`, `CRC2`) with dual Analytical (Float32) and Display (Byte RGB 2% stretch) GeoTIFFs.
- Multi-Generation Landsat Support: Hardened XML/TXT metadata parsing, preventing Level-1 provenance overwrite of Level-2 products, and enabled legacy thermal radiance derivation.
- Results Directory Tree Guide: Documented standard ASCII output folder hierarchy and file types for end users.
- Host UI parity across ArcGIS Pro and QGIS with `qa_mask_mode`, maintaining strict bilingual isolation (D-008).
- Verification: 192 automated unit tests passing (100%), verified with real dual-scene processing on modern Landsat 9 C2 L2 and legacy Landsat 8 L1T scenes with 0 NaN corruption. Delivery reports [0031](Reports/0031_comprehensive_usability_geological_and_envi_integration.md) and [0032](Reports/0032_advanced_envi_indices_and_qa_mask_engine.md).
- تحديث شامل لمحرك الجودة الذكي بأنماطه المتعددة وإلغاء الإنذارات الكاذبة للقضاء التام على الثقوب البيضاء في الجبال ومجرى النيل، وإضافة 6 مؤشرات جديدة من ENVI 6.3، وتبسيط حساب الحرارة بحساب NDVI تلقائياً، ودعم متعدد الأجيال للمرئيات القديمة والحديثة، وتوثيق شجرة النواتج باللغتين.

## 1.0.4.dev0 — 2026-11-16 legacy imagery/output audit (local development)

- Shared metadata-first Landsat pre-Collection/C1/C2 calibration/QA, explicit ESPA companion validation, TM/ETM+/MSS roles and corrected SLC-off dates. Diagnostic NDVI TOA is opt-in and separately named; SR/LST gates retained.
- Sentinel2 per-band L1C/L2A offsets, quantification and baseline checks replace a single assumed offset; missing modern calibration rejects processing.
- Independent read-only CRC1 audit verified arithmetic, masks and measured cyan display; formulas/order unchanged. Seven-tool/product/method inventory distinguishes eligibility from real validation.
- Composite runs separate Analytical/Display/Metadata/QA_Reports, readable satellite/recipe names, optional Work channels, full channel moments, NaN analytical NoData and linear/percentile/stddev display stretch. EN/AR preview explains source/limits.
- Supplied plans move into numbered plan folders; pristine references only in Source_Archive with identity/SHA, no root duplicate. PLAN-0019 stays Active for unavailable real/reference/clean-install checks. No publication.
- أُصلحت قراءة المنتجات القديمة ومعايرتها وأقنعتها، ووُثّق سبب اللون السماوي حسابيًا دون تغيير الوصفة. تنظيم المخرجات ونقل الخطط موثق باللغتين؛ النسخة محلية تجريبية.

## 1.0.3.dev1 — 2026-11-15 geological color composites (local development)

- Added a seventh independent native tool with Direct RGB and Ratio RGB, shared bounded arithmetic/multichannel core, source-checked Landsat presets and explicit experimental/custom choices.
- Separate reproducible display GeoTIFFs, sampled before/after preview, QGIS background preview dialog, Pro temporary HTML preview and preset export/import. Continuous Float32 values and original sources are preserved.
- Added exact multiband mapping/calibration, historical ASTER SWIR gates, pre-Collection Landsat 8 L1T TOA/legacy BQA handling, polygon clip and complete-triplet mosaic provenance. No classification, automatic atmospheric correction or field accuracy claim.
- EN/AR guide and native/package verification updated; per-criterion evidence and outstanding real Sentinel-2/ASTER/full Pro GUI/clean-install acceptance remain in PLAN-0018. No publication in this phase.
- أُضيفت أداة مستقلة للتراكيب اللونية الجيولوجية بطريقتي الدمج المباشر والنسب، مع معاينة وعرض منفصلين عن التحليل وحفظ التركيبات والمعايرة والمصادر باللغتين. النسخة محلية تجريبية وليست اعتمادًا جيولوجيًا حقليًا.

## Unreleased — 2026-11-15 agent instructions

- Plan intake now explicitly covers supplied files with any name and conversational development requests. Preserve or derive a descriptive title, copy supplied sources unchanged, and name working plans with a stable sequential ID plus subject.
- Reports require an independent sequential number plus descriptive name/heading and plan/revision link. Synchronized agent startup, indexes, skills registry and EN/AR specification addenda; no processing behavior changed.
- أصبحت تعليمات الوكيل تشمل الخطط بأي اسم وطلبات التطوير في المحادثة، مع اسم وصفي ورقم ثابت للخطة وحفظ الأصل، ورقم مستقل واسم وصفي لكل تقرير.

## 1.0.1.dev0 — 2026-11-14 recovery build

- One `atiaf_core` implementation, thin shared workflow adapters, explicit calculation choices and sensor-first/output-last order.
- Separate Pro language toolboxes and QGIS locale labels; expert JSON; actual saved CRS, AOI/mosaic routing and saturation QA.
- Unique result filenames preserve previous products. Unsupported science is gated with reasons.
- `documentation/` organization, supplied logo/banner, bilingual guides, offline portal and QGIS ZIP builder.
- Environment helpers now check only, never silently install binary wheels. Earlier stable claims superseded; see PROJECT_STATE.md and numbered reports.

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
  - Multi-sensor discovery engine (`atiaf_core/discovery/`): Landsat 1–9 Collection 2, Sentinel-2 L2A/L1C, and ASTER.
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
  - Tool 01: Spectral Indices engine (`atiaf_core/indices/`) supporting 14 core optical indices with capability gating.
- **Phase P4 (Surface Temperature & Geological Analysis):**
  - Tool 02: Surface Temperature engine (`atiaf_core/temperature/`) calculating LST in Kelvin and Celsius and Emissivity (LSE) via Sobrino et al. (2004) NDVI thresholds model.
  - Strict blocking of thermal calculations on sensors lacking thermal channels (Sentinel-2).
  - Tool 05: Geological Analysis engine (`atiaf_core/geology/`) with 8 diagnostic alteration ratios and ASTER post-April 2008 SWIR degradation cutoff.
- **Phase P5 (Multi-Scene Mosaic & Temporal Change Detection):**
  - Quality-aware multi-scene mosaic blending engine (`QualityMosaicEngine`) with union extent calculations, quality ranking, and `Source_Scene_ID.tif` provenance tracking.
  - Tool 06: Temporal Change Detection engine (`atiaf_core/temporal/`) calculating dNDVI, dNBR with official USGS FIREMON 7-class Burn Severity classification, relative change %, and standard deviation anomaly mapping.
- **Phase P6 (Expanded Catalog, Thermal Urban & Environmental Drought):**
  - Expanded optical index catalog to 22 validated indices (NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW).
  - Tool 03: Thermal Urban engine (`atiaf_core/urban/`) with Urban Thermal Field Variance Index (UTFVI; 6-class ecological comfort), thermal anomaly hotspots ($z \ge 2.0$), and SUHI.
  - Tool 04: Environmental Drought engine (`atiaf_core/environment/`) with Liang (2001) broadband shortwave surface albedo ($\alpha$) and Temperature Vegetation Dryness Index (TVDI).
- **Phase P7 (Native QGIS Processing Provider Adapter):**
  - Complete QGIS Processing Provider plugin package (`qgis/atyaf/`) with `metadata.txt`, `classFactory`, provider ID `atyaf`, and all 6 processing algorithms.
  - Tested natively inside QGIS 4.2.3 via `python-qgis.bat`.
- **Phase P8 (Advanced Modalities, SAR & Hyperspectral Gating):**
  - Advanced sensor modality architecture (`atiaf_core/modalities/`).
  - SAR engine (`SAREngine`) enforcing the non-negotiable rule: *"Never route SAR through optical equations"*, linear-to-dB conversion, cross-polarization ratio, dual-pol RVI, and pure-NumPy Lee speckle filter.
  - Hyperspectral engine (`HyperspectralEngine`) with Spectral Angle Mapper (SAM) in float64, continuum-removed diagnostic absorption feature depths (2205 nm, 2345 nm, 900 nm), and Level-2 surface reflectance cube gating.
  - Copernicus Sentinel-1 C-SAR parser (`Sentinel1Parser`) recognizing `.SAFE` GRD/SLC products.
  - Comprehensive bilingual documentation in `documentation/en/ADVANCED_MODALITIES.md` and `documentation/ar/ADVANCED_MODALITIES.md`.
- **Phase P9 (Packaging, Documentation Build & Release Readiness):**
  - PEP 517/518/621 `pyproject.toml` configuration enabling `pip install -e .`.
  - CLI diagnostic and verification utility (`atyaf-verify` / `tools/verify_installation.py`).
  - Responsive, modern bilingual offline documentation portal (`documentation/index.html`).
  - User documentation and walkthroughs in `README.md` and `README.ar.md`.
# 1.0.2.dev0 — consolidated UI and interpretation development

- Input Data Folder labels, optional manual native band-file fields, explicit calibration and source evidence in both hosts; JSON import optional.
- Thematic calculation groups and conditional controls; removed calculation search; one LST control with Celsius/Kelvin units and optional local NDVI/RTE derivation inputs.
- EVI2 (2.5/2.4 variant) and unadjusted NIRv numerical implementations, subject to separate real-product validation.
- Shared bilingual interpretation metadata, generated catalog/HTML and result reports; optional local NDVI classes preserve continuous data and record effective thresholds.
- QGIS installable ZIP defaults to QGIS Tools/Distribution; prior dist packages retained. Fresh validation status is recorded in the current numbered report; this is not a stable release.
# 1.0.2.dev1 — professional repository publication snapshot

- Refined matching English/Arabic README and generated Index: host installation cards, manual/thermal guide routes, accessible labels and explicit development/support scope; supplied logo then banner retained.
- Added citation/contribution/security guidance, portable Git attributes and a narrow publication file/credential-pattern audit. Local original asset duplicates, GIS metadata, scenes and build caches stay local.
- GitHub Actions uploads separate QGIS/core development artifacts after passing headless/package checks. No new scientific algorithm or stable/real-product validation claim in this presentation snapshot.
- Clean-checkout parser tests now generate isolated synthetic stubs; JSON validation excludes project-relative resource caches rather than matching parent folder names.
