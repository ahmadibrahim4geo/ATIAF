# Geological Color Composites

This independent tool follows ATIAF's existing sensor-first, output-last workflow in ArcGIS Pro and QGIS. Select **Direct RGB**, **Ratio RGB**, or both; neither is selected initially. The results are continuous spectral images that retain terrain detail. They do not classify lithology or confirm mineral deposits.

## What the two methods do

| Method | Analytical channels | Display |
|---|---|---|
| Direct RGB | Three calibrated physical bands, ordered R;G;B | Continuous false color; SWIR/NIR colors are not true color |
| Ratio RGB | Three independently calculated expressions | Continuous spectral contrast, not classes |
| Enhancement | The same three analytical channels | Quiet, Balanced, Enhanced or Custom; never changes the Float32 analytical values |

Landsat 8/9 source-checked presets: **7;5;3**, **B6/B7; B6/B2; (B4/B5)*(B6/B5)**, and **B4/B6; B4/B2; B6/B7**. Their formulas/order were checked in Figures 3, 10 and 11 of the [Duwi study](https://www.nature.com/articles/s41598-024-66199-3). Source checking does not validate local rock names or reproduce that study's atmospheric correction. Landsat 7-6-2, Sentinel-2 12-11-4/12-11-2 and historical ASTER 4-6-8 remain explicitly experimental. The proposed Fawakheir ASTER ratio remains experimental pending independent full-text verification.

## First run

1. In Pro open ATIAF.pyt (English) or ATIAF_AR.pyt (Arabic), then **Geological Color Composites** under Geological Analysis. In QGIS open the ATIAF Processing provider's Geological Analysis group. Reopen/restart tools after installing an updated matching package.
2. Choose sensor/product and one unpacked scene folder or its immediate multi-scene parent. AUTO can positively identify the supported pre-Collection Landsat 8 L1T profile. Normal optical paths use the existing Landsat C2 L2 / Sentinel-2 metadata readers; verify their limits on your actual product.
3. Select method(s), then a matching preset or manual channels. Direct example: `B7;B5;B3`. Ratio example: `B6/B7;B6/B2;(B4/B5)*(B6/B5)`. Custom choices need a reference/local justification. Expressions allow only band IDs, numeric constants, parentheses and `+ - * /`; no executable code.
4. Keep QA on when the necessary per-pixel mask exists. Experimental presets need their explicit toggle. TOA products need the explicit TOA toggle; no atmospheric correction is silently performed. L2 is not scaled twice.
5. Choose display enhancement. Balanced is the default. Custom controls are percent clip per tail, gamma, saturation and optional fixed bounds `Rmin,Rmax,Gmin,Gmax,Bmin,Bmax`. Constant channels display at midpoint. Automatic limits use a deterministic sample up to 512×512, fixed to the output footprint rather than current map extent; they are not exact full-scene quantiles.
6. Optionally set independent polygon AOI, native projected metre CRS and Add Results to Map. Output folder is the last setting; blank uses the source folder. A different destination creates a scene-named child. Earlier results are preserved with unique filenames.

## Preview and saved presets

QGIS has a **Preview RGB before / after** button running bounded reads on a background task; a native dialog compares the same channels with quiet versus selected enhancement. The normal Processing Preview-only option and Pro's **Temporary before/after preview only** option create temporary HTML/PNG views without full-size analytical rasters or Work/Results. Open the local HTML path from processing messages in Pro. Preview-only is per scene; mosaic must be off. PNG previews are reduced, not georeferenced analysis products. Normal completed runs also save a before/after HTML preview and PNG.

Every run saves `Composite_Preset.json` alongside its manifest. Import it through the optional preset file control; custom source/expressions and stable channel order are retained. **Restore saved display bounds and settings** optionally applies exactly saved limits/gamma/saturation. Otherwise display is recalculated with current controls. An imported JSON status cannot promote a custom formula to source-verified. Calibration/multiband inputs remain explicit, separately entered source information.

## Multiband input and sensor limitations

Enable explicit multiband mode, choose the actual sensor, select its local raster, list scientific IDs in file-position order, acquisition date, scale(s), offset(s), physical level and calibration/sensor/product provenance. One scale/offset can apply to all channels, or one value per channel. For example a three-channel file can have positions **B7,B5,B3**, scale **1**, offset **0**, only when verified calibrated values justify that mapping. Physical band B7 is not necessarily file position 7. B8 and B8A remain distinct. No mandatory mapping JSON is required.

ASTER needs this explicit calibrated mapping because the automatic project reader does not yet establish every exact B4–B9 band/calibration. SWIR requires a known acquisition **before April 2008**. Earlier 2007–January 2008 saturation advisories are also warned. Read the [NASA/JPL advisory](https://asterweb.jpl.nasa.gov/swir-alert.asp). Band availability alone does not validate a real ASTER product.

The supplied `LC81760392014234LGN00` is pre-Collection Landsat 8 **L1T**. Its optical TOA reflectance uses `(DN × REFLECTANCE_MULT + REFLECTANCE_ADD) / sin(SUN_ELEVATION)` with exact MTL keys. This is not surface reflectance, and no dark subtraction/FLAASH is applied. See [USGS Level-1 calibration](https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product). Pre-Collection BQA uses fill/dropped-frame/terrain bits 0–2 and medium/high snow/cirrus/cloud confidence pairs 10–11/12–13/14–15; it has no cloud-shadow flag or per-band saturation flags. Raw optical 0/65535 are excluded. This decoder is not used for Collection 1/2 BQA. See [USGS QA guide, version 1.4, section 2.1](https://landsat.usgs.gov/sites/default/files/documents/landsat_QA_tools_userguide.pdf).

## Saved outputs and safety

Analytical Float32 three-channel GeoTIFFs live under `Results/Geological_Color_Composites/Direct_RGB/` or `Band_Ratio_RGB/`. Optional `_DISPLAY.tif` is a separate UInt8 RGB product, with zero reserved for NoData and valid display values 1–255. It is not original reflectance. Metadata preserves preset/source, exact input files and band positions, calibration provenance/units, equations, denominator tolerance, QA limitations, dates, grid, resampling, settings, fingerprint and engine version. Per-run bilingual reports remain under `Results/Reports`.

The coarsest selected source band determines the reference grid, using documented nearest resampling; upsampling never creates new spectral detail. All RGB channels share one validity mask. Zero/near-zero denominators and nonfinite values become NoData; valid negative/unbounded ratios are retained. AOI is true polygon clipping, with full products retained. Mosaic requires matching sensor/level/day and a common output CRS, merges complete valid RGB triplets by scene cloud-cover priority then stable ID, and writes a Source_Scene_ID raster/table. Scene cloud cover is only priority; per-pixel QA masks provide the actual exclusions. No cross-date harmonization or universal geological color key is claimed.

## Evidence scope

Tests cover independent arithmetic, exact-band mapping, masks, NoData, preservation, temporary previews, custom import/export, ASTER date gates, polygon clipping and complete-triplet mosaic. Native synthetic checks and real Landsat L1T evidence are recorded in the [development reports](../../Reports/INDEX.md). Real Sentinel-2/ASTER products, field lithological accuracy, full interactive Pro journeys and clean-machine installation require their own evidence. A built ZIP or source-checked formula does not satisfy those checks.


## Legacy product audit update — 2026-11-16

AUTO now shares metadata-first Landsat TXT/JSON/XML and explicit ESPA discovery across tools. Collection1/2 and pre-Collection calibrations/QA differ; see the [compatibility matrix](../../Reports/PLAN-0019_Audit/01_Sensor_Product_Compatibility_Matrix.md). T01 separately allows diagnostic NDVI_TOA; other SR-dependent methods remain gated. Sentinel2 processing baseline, quantification and physical-band offsets are read from metadata, not acquisition year. Missing modern offsets are rejected. Real products other than the supplied L8 remain unverified here.

New composite layout: `Results/Geological_Color_Composites/<method>/<recipe>/<run>/Analytical`, `Display`, `Metadata`, `QA_Reports`. Names show actual satellite and recipe, not a combined sensor family or formula slug. Full reports remain under Results/Reports and QA_Reports points to them. Optional individual analytical R/G/B rasters go to `Work/Geology_<recipe>/<run>/Intermediate_Rasters`. Metadata records actual satellite separately from compatibility family, scene/product/collection/processing date, calibration keys, equations, units, full per-channel moments and sampled display bounds. New analytical NoData is NaN, retaining valid negative values including -9999; older outputs are unchanged. Display remains UInt8 with zero NoData.

Display stretch can be percentile, linear min/max or mean ± chosen standard deviations; all bounds use the declared deterministic reduced sample unless fixed explicitly. Gamma/saturation are display only. A cyan pixel has stronger green/blue display channels relative to red after stretch; interpretation depends on recipe, calibration, scene and display, and never proves a mineral. The real CRC1 audit independently checked native-resolution pixels and full raster masks/statistics: [numerical evidence](../../Reports/PLAN-0019_Audit/04_RGB_CRC1_Numerical_QA.md). Previews show scientific source and the interpretation warning. No new atmospheric correction, classification, imagery download or universal rock legend.
