# Surface temperature: official product or local NDVI-assisted derivation

Select **LST** and the output unit **Celsius** (default) or **Kelvin**. Nothing is calculated until LST is selected. These units represent the same quantity: 303.15 K = 30 °C. LST measures the surface, not 2 m air temperature. Legacy LST_CELSIUS/LST_KELVIN API IDs remain readable by older headless workflows but are no longer separate dialog choices.

Default path: extract a documented official L2 ST raster with its scale/offset and QA. It already incorporates an emissivity/atmospheric retrieval; never apply another emissivity correction to this product. Sentinel-1 and optical-only Sentinel-2 cannot provide thermal LST.

Enable **Derive LST using NDVI emissivity and local atmospheric inputs** only when all required local inputs are available:

- Calibrated at-sensor thermal radiance in W/m²/sr/µm, not DN, brightness temperature or official L2 ST.
- Compatible existing NDVI in physical units, or corresponding calibrated red/NIR bands. Document matching scene/date and processing provenance.
- Band-specific Planck K1 (same radiance units), K2 (Kelvin), atmospheric transmittance, upwelling and downwelling radiance. No assumed/default atmosphere or download.
- User-justified soil/full-vegetation NDVI thresholds and band soil/vegetation emissivities; record sources and assumptions. Spatially constant atmospheric terms assume scene-wide applicability and are not a substitute for an appropriate atmosphere.

The current explicit model is a local **linear soil/vegetation emissivity mixture with squared NDVI vegetation fraction**, no cavity term. Negative/out-of-range NDVI is masked, not guessed as water. It is not claimed to reproduce every branch/constant of Sobrino's published TM5 threshold algorithm. The user must justify band-specific coefficients and the flat-mixture approximation; real-product accuracy remains unvalidated.

```text
Pv = clamp((NDVI - NDVI_soil)/(NDVI_vegetation - NDVI_soil), 0, 1)^2
epsilon = epsilon_soil*(1-Pv) + epsilon_vegetation*Pv
Lsurface = (Lsensor - Lup - tau*(1-epsilon)*Ldown)/(tau*epsilon)
LST_K = K2 / ln(1 + K1/Lsurface)
LST_C = LST_K - 273.15
```

This path currently accepts a single Landsat scene. Existing ancillary rasters must match source CRS/grid/extent; align them explicitly first. The ordinary host CRS chooser can then project the output. Provide a valid source definition; no default EPSG. AOI/mosaic/output/map rules remain shared. Formula/inputs/assumptions are in each run's EN/AR reports. Numeric forward/inverse and synthetic raster checks are distinct from real-product/field validation. The old gated EMISSIVITY_NDVI-only choice is not shown as a standalone working LST method.

References: [Sobrino et al. (2004), RTE and NDVI emissivity approach, Eq.1 and 8–9](https://www.uv.es/sobrino/sobrino_files/papers/Sobrino_LST-Landsat_RSE2004.pdf), [USGS official ST inputs](https://www.usgs.gov/landsat-missions/landsat-collection-2-atmospheric-auxiliary-data). Literature is reference material, not copied runtime source.
