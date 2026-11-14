# Troubleshooting / diagnostics contract
| Problem | Expected tool behaviour | Recorded evidence |
|---|---|---|
| Missing MTL/metadata | Offer guarded Manual Band Mapping; disable calculations needing unknown scale/radiance | Missing file, missing key, user mapping, affected methods |
| Wrong sensor selected | Detect mismatch, prevent unsafe processing | Detected product ID, user requested type |
| L1 wrongly treated as L2 | Stop or run explicitly configured validated path; never silently assume surface reflectance | Level, conversion method and actual source |
| Missing SWIR/thermal | Show index as unavailable with reason | Expected role vs actual band inventory |
| Sentinel-2 scene requested for LST | Disable unless an independently supplied valid local thermal input supports method | Sensor and thermal-source check |
| Wrong units/projection | Ask native GIS CRS picker for suitable projected metre CRS; define unknown source explicitly | Input/output CRS WKT/EPSG and transformation |
| AOI no overlap | Explain zero valid pixels, write warning not corrupted tif | AOI geometry and intersection result |
| Mosaic date or sensor differences | Warn / enforce documented comparability; preserve source ID and acquisition dates | Provenance table, overlap policy |
| Existing output filename | Check manifest & raster readback: reuse only exact match, else immutable version | Fingerprints, run ID, prior file unchanged |
| Raster succeeded but map add failed | Save outputs; log separate map-add failure; continue if safe | Status of map queue and layer IDs |
| Out of memory / cancel | Use windowed processing, partial cleanup, resume safe products | Last completed block / checksums |
| Background tool UI limitations | Document host parameter limitations and use supported UI or optional add-in | Native test and decision record |

Logs show human-readable localized error plus detailed technical trace, without secrets or user-private paths in publicly committed reports.
