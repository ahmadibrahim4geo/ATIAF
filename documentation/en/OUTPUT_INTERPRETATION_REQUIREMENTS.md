# Output interpretation and classification — requirements note

**Historical r5 intake.** Current r6 implements shared per-method EN/AR interpretation and optional local NDVI classes; see the regenerated [catalog](INDICATORS_CATALOG.md) and [quick start](QUICK_START.md). Native/synthetic configuration tests do not constitute field calibration of class thresholds. Original requirements/audit below are preserved.

Date: 2026-11-15; PLAN-0015 r5. **Documentation/UI requirements, not implemented classification support.** [Arabic counterpart](../ar/OUTPUT_INTERPRETATION_REQUIREMENTS.md).

## Observed gap

The generated INDICATORS_CATALOG files provide formulas, band roles and citations. They do not provide complete per-method range interpretation/classification tables. SCIENTIFIC_METHODS currently refers to such detailed tables; that cross-reference overstates existing coverage and must be corrected during the documentation implementation. Source generator inspection found no complete interpretation/class-preset metadata pipeline. This is static inspection, not a native runtime test.

## Required explanation for every calculation

Provide meaning, formula/variant, input/sensor/level restrictions, units, theoretical and typical values, high/low/negative interpretation, NoData and quality behavior, limits and worked examples. Differentiate a scientific numeric product from display colors and an optional classified raster. Do not force all indices to [-1,1] or apply generic vegetation labels to nonvegetation outputs.

For class tables identify exact intervals/inclusivity, EN/AR names, source/version and applicability. Distinguish verified formal standards (issuer/version/scope), paper-specific classifications, educational guidance and locally calibrated/user-defined classes. Absence of an applicable verified standard must be explicit. Preserve scientific concepts when thresholds are adjusted; local classes cannot be represented as unchanged compliance with a standard. Greenness/density classes do not automatically measure plant health, biomass, yield or species.

## NDVI illustration — guidance, not an executable preset

NDVI = (NIR - Red)/(NIR + Red), dimensionless. Under valid nonnegative reflectance with a nonzero denominator its mathematical interval is [-1,1]. Real products can include negative reflectance, artifacts or invalid denominators; those need QA/explanation, not silent clipping into classes. Negative/near-zero values may occur for water, snow/cloud contamination, bare or other nonvegetated surfaces; NDVI alone does not uniquely identify them. Higher positive values generally imply greater green-vegetation signal, with canopy saturation and background effects limiting interpretation.

NASA's educational article gives examples of very low values around 0.1 or below, moderate shrub/grassland examples around 0.2–0.3, and dense-forest examples around 0.6–0.8. USGS describes approximately 0.2–0.5 for sparse vegetation or senescing crops. These are contextual illustrations, **not a universal international weak/medium/strong threshold standard**, nor a complete partition to install as a default preset. Differences reinforce the need to cite scope and validate local labels.

Numeric breaks can be locally calibrated using representative independent/field references; crop type, season, soil, moisture, atmospheric quality, sensor and resolution matter. A low NDVI is not sufficient to label a crop unhealthy. Histograms, quantiles and attractive colors alone do not validate ecological classes. Where a preset is implemented, retain the continuous raster and store optional class outputs separately. Log the original/effective intervals, names, source/version, user edits and validation basis; disclose classification changes when comparing dates.

## Delivery acceptance

Implement through canonical metadata and the documentation generator, then synchronize EN/AR Markdown/HTML, native help and result reports. Verify coverage by stable method ID/variant, exact boundaries, overlaps/gaps, NoData/QA and bilingual meaning. Verify optional local edits in both actual hosts and read back the recorded effective scheme. These controls/tests are **NOT RUN / not implemented** in this discussion. No field validation is claimed.

## Reference provenance

Accessed 2026-11-15, reference material only; no data/code imported or new runtime dependency:

- [NASA Earth Observatory, Measuring Vegetation (NDVI & EVI), published 2000-08-30](https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/): educational explanation/examples, not a class standard.
- [USGS, NDVI foundation for remote-sensing phenology](https://www.usgs.gov/special-topics/remote-sensing-phenology/science/ndvi-foundation-remote-sensing-phenology): official search-index text accessible; direct open was challenge-blocked. No standard is inferred from it.
- [NASA Disasters, NDVI interpretation caveats](https://science.data.nasa.gov/disasters/data-gallery/planet-ndvi): general caveats about season, vegetation, soil, atmosphere and moisture. The referenced commercial product is not a proposed free runtime source or added ATIAF sensor.

No verified internationally applicable NDVI class standard was established by this targeted review. A future claimed standard requires explicit issuer, edition and applicability evidence. Original project code remains MIT; web references retain their own rights.
