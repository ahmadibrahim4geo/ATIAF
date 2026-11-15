# Expert band mapping

Use this optional legacy JSON schema only when sensor, date, bands, calibration and level can be verified. In current dialogs choose the actual sensor/product, enable manual mapping, and optionally import this file; direct [native band fields](MANUAL_BANDS.md) do not require JSON. Legacy programmatic sensor=EXPERT still accepts this schema. Paths in this legacy schema must stay within the input scene. Direct manual runs export a newer atiaf_manual_v1 mapping into their unique report directory. No downloads occur.

```json
{
  "scene_id": "MY_SCENE",
  "platform": "Landsat 8",
  "instrument": "OLI_TIRS",
  "sensor_family": "Landsat",
  "product_level": "L2_SR",
  "acquisition_date": "2023-05-20",
  "bands": {
    "red": {"file": "red.tif", "scale": 0.0000275, "offset": -0.2, "unit": "reflectance", "wavelength_nm": 655, "provenance": "USGS C2 L2 product guide; confirm this file is unscaled SR DN"},
    "nir": {"file": "nir.tif", "scale": 0.0000275, "offset": -0.2, "unit": "reflectance", "wavelength_nm": 865, "provenance": "USGS C2 L2 product guide; confirm this file is unscaled SR DN"}
  }
}
```

These numbers are an example for unscaled Landsat C2 L2 SR, never universal defaults. Already scaled reflectance requires scale 1 and offset 0, backed by provenance. Every band needs explicit finite scale, offset, wavelength and calibration provenance. Unknown CRS, missing bands and unsupported levels stop execution. The current expert schema has no QA input mapping: leave the default QA request on to block unsafe processing, or explicitly turn it off after assessing cloud/saturation limitations. Never describe such a run as QA validated. Official thermal surface Kelvin is accepted only when product and unit evidence are correct. This interface does not convert arbitrary thermal DN or brightness temperature to LST. Expert multi-epoch mapping is not supported yet.
