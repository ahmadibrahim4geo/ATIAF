# Mandatory scientific and GIS acceptance matrix
| Area | Minimum evidence | Tests |
|---|---|---|
| Source discovery | T1 + T3 | Unpacked Landsat/Sentinel-2/ASTER fixture product, aliases, hidden Results excluded, missing MTL and wrong selected sensor |
| Band mapping | T1 + T3 | Exact asset paths, wavelengths/QA, L1-vs-L2 scale; expert overrides detected and reported, impossible cases disabled |
| Spectral math | T1 + T3 | Independent hand-computed array values, zero-denominator/negative reflectance, QA, Float32, NoData |
| LST | T1 + T3 | Valid Landsat C2 L2 ST conversion and mask; no Sentinel-2 thermal; native thermal resolution disclosed |
| Geological | T1 + T3 | Source DOI/formula product and valid date/band checks; ASTER SWIR 2008 and TIR 2026 restrictions |
| CRS | T2 + T3 | Host-native picker, no fixed default, metre checks, unknown source CRS recovery, AOI reproject and raster align |
| AOI/mosaic | T1 + T3 | true polygon not bbox; multi-date warnings, quality-overlap, per-scene archive, source-scene ID map |
| Shared results | T1 + T3 | 3 tools same scene; preserve earlier outputs and reports, duplicate run validated skip, param difference versioning, interruption/recovery |
| Add-to-map | T2 + T3 | unchecked leaves products on disk; checked adds sequentially without UI freeze; failed layer handled separately |
| I18N | T2 + T3 | Arabic RTL, English no Arabic labels, localized messages/help/reports; stable IDs/files |
| Provenance | T1 + T3 | Exact metadata path:key:value, formula variant, DOI, real used bands, masks/CRS, calculation QA, readable HTML/JSON |
| Security | T1 | corrupted archives, path traversal, hostile XML, no token leakage, writable bounds |
| Installation | T4 | fresh ArcGIS Pro host, fresh QGIS host, dependencies/skills/license docs and simple workflow |

T0 = docs/static; T1 = deterministic offline fixture; T2 = native host integration; T3 = real satellite product readback and independent output check; T4 = clean packaging/install/user workflow. Never conflate tiers. Each report records tests with run timestamp, command, exit code, host versions and measured result. If a host is absent, report BLOCKED or NOT RUN, not pass.
