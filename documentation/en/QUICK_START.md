# First workflow

Start with [installation](INSTALLATION.md). These steps explain usage, not validation of every satellite product.

1. **Sensor / Product:** choose AUTO or the actual mission/level. Metadata mismatch stops automatic discovery. With incomplete metadata choose the actual supported sensor and enable [manual band mapping](MANUAL_BANDS.md); JSON is optional.
2. **Input Data Folder:** one unpacked scene or a folder containing scenes. Keep original metadata, bands and QA together where available. Work/Results are excluded from discovery. Manual mode accepts selected local band files without a header.
3. **QA / preprocessing:** QA is ON by default. Scaling is applied once from the product profile; no automatic atmospheric correction. Missing QA blocks a QA-enabled run. Explicit opt-out lowers assurance.
4. **Mosaic:** OFF by default. ON combines compatible same-day per-scene products and retains their source provenance. Different sensors/dates need a validated harmonization method.
5. **Calculations:** check named boxes under thematic headings in both hosts. All defaults are empty; calculation search is removed. Gated selections explain missing prerequisites. The [catalog](INDICATORS_CATALOG.md) explains output meaning, units, ranges and limits. Optional local NDVI classes need a justification and preserve the original raster.
6. **AOI:** optional nonempty valid polygon with known CRS, independently of mosaic. An invalid AOI stops instead of silently processing full extent.
7. **Output CRS:** native host chooser. Blank reuses a known suitable projected metre source. Unknown/geographic/foot-based CRS needs correction or selection. No global EPSG default. Your selection changes the saved raster grid.
8. **Map loading:** optional and OFF by default. Saved products survive rendering errors. Native map queue/RTL visual acceptance is separately recorded.
9. **Output folder:** LAST setting. Blank or equal to input keeps each scene's Work/Results. A custom destination creates a scene-named subfolder. Reruns retain earlier files.

For a first NDVI run use red and NIR surface reflectance with QA. `(NIR-Red)/(NIR+Red)` gives 0.6667 for red 0.1 and NIR 0.5; DN must be calibrated first. Open the GeoTIFF, inspect CRS/NoData, then open `Results/Reports/index.html` and the run's manifest.

| Tool | First useful selection | Prerequisite |
|---|---|---|
| Spectral | NDVI | Red/NIR surface reflectance |
| Temperature | LST, then Celsius/Kelvin unit | Official ST or explicit [local NDVI/RTE inputs](SURFACE_TEMPERATURE.md) |
| Thermal & urban | UTFVI or HOTSPOTS | Official LST; SUHI is gated |
| Environment | ALBEDO | Current Landsat TM/ETM+ profile only; TVDI is gated |
| Geology | IRON_OXIDE | Correct calibrated red/blue; indication only |
| Temporal | NDVI, NBR or LST | Select second scene, matching sensor/level and later known date; T2 minus T1 |

[Formula cards](INDICATORS_CATALOG.md) · [Folders](TOOL_UI_AND_WORKSPACE.md) · [Troubleshooting](TROUBLESHOOTING.md).


Archived Landsat: AUTO reads actual generation/level metadata. Only explicitly enabled diagnostic NDVI_TOA and calibrated RGB can use TOA; SR-dependent methods remain gated. See [legacy product/output guide](GEOLOGICAL_COLOR_COMPOSITES.md) and [compatibility audit](../../Reports/PLAN-0019_Audit/01_Sensor_Product_Compatibility_Matrix.md).
