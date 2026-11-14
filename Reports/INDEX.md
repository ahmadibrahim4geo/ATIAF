# Development Reports — chronological index
Every real work/verification/handoff batch gets a new monotonically numbered report: `0001_<slug>.md`, then `0002_...` and so on.

## Rules
- Every real work/verification/handoff batch gets new monotonically numbered report: `0001_<slug>.md`, then `0002_...` and so on.
- Reports are immutable evidence summaries; never silently overwrite. Corrections are new reports referencing the older number.
- The latest/highest number points to the current handoff, but compare it against `PROJECT_STATE.md`, the journal and actual Git tree.

| Report | Date | Plan | Status | Verified evidence | Next action |
|---|---|---|---|---|---|
| [0001_initial_bootstrap_and_environment.md](0001_initial_bootstrap_and_environment.md) | 2026-11-14 | PLAN-0001 | VERIFIED-COMPLETED | P0 bootstrap, skills commit 2a0a9a2, QGIS 4.2.3, ArcGIS Pro 3.6, 6 unittests OK | Begin Phase P1: Product recognition & metadata extraction |
| [0002_product_recognition.md](0002_product_recognition.md) | 2026-11-14 | PLAN-0002 | VERIFIED-COMPLETED | P1 discovery core: Landsat C2 L2, Sentinel-2 L2A/L1C, ASTER, SceneScanner, ManualBandMapper, 15 unittests OK | Begin Phase P2: Core raster arrays, CRS, QA masks & Work/Results manager |
| [0003_core_raster_crs_output.md](0003_core_raster_crs_output.md) | 2026-11-14 | PLAN-0003 | VERIFIED-COMPLETED | P2 raster core: windowed processing, QA masks, projected metre CRS validation, polygon AOI clipping, Work/Results manager, 29 unittests OK | Begin Phase P3: ArcGIS Pro independent tools (.pyt) & Spectral Indices |
| [0004_arcgis_pro_spectral_indices.md](0004_arcgis_pro_spectral_indices.md) | 2026-11-14 | PLAN-0004 | VERIFIED-COMPLETED | P3 ArcGIS Pro .pyt, Tool 01 Spectral Indices, capability gating, manifest generation, 40 unittests OK | Begin Phase P4: Surface Temperature & Geological Analysis |
| [0005_surface_temperature_geological.md](0005_surface_temperature_geological.md) | 2026-11-14 | PLAN-0005 | VERIFIED-COMPLETED | P4 Surface Temperature & Geological Analysis, LST, emissivity, ASTER SWIR cutoff, Tools 02 & 05 in .pyt, 53 unittests OK | Begin Phase P5: Multi-scene quality-aware mosaic & change detection |
| [0006_mosaic_temporal.md](0006_mosaic_temporal.md) | 2026-11-14 | PLAN-0006 | VERIFIED-COMPLETED | P5 Multi-Scene Quality-Aware Mosaic & Temporal Change Detection, union extent, Source_Scene_ID provenance, dNBR burn severity, Tool 06 in .pyt, 60 unittests OK | Begin Phase P6: Expanded index catalog & environmental models |
| [0007_expanded_catalog_environment.md](0007_expanded_catalog_environment.md) | 2026-11-14 | PLAN-0007 | VERIFIED-COMPLETED | P6 Expanded Offline Catalog, Thermal Urban & Environmental Drought, UTFVI, Hotspots, Liang Albedo, TVDI, Tools 03 & 04 in .pyt (all 6 tools complete), 71 unittests OK | Begin Phase P7: Native QGIS Processing provider adapter |
