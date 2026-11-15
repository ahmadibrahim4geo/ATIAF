# ATIAF Development Roadmap — verified milestones
The user has approved the functional design; the roadmap's order is implementation guidance, not proof that any feature exists. Follow `AGENTS.md` for numbering/admission/archive of work plans and reports.

| Phase | Work | Observable acceptance/evidence |
|---|---|---|
| P0 — Governance & dependencies | Confirm license, repo structure, AGENTS + development journal, skill bootstrap, dependency/compatibility matrix, source and catalog legal review, CI skeleton | Source/JSON/links validation, pinned skills commit, unit tests and report 0001; no native GIS claims |
| P1 — Product recognition & metadata | Landsat L4-9 C2 L2, Sentinel-2 L2A, ASTER initial product profiles; scene directory/parent scan; sensor+band+QA manifest; manual mapping controls | Real unpacked samples, independently checked metadata, mismatches/partial paths, error and edge fixtures; T1–T3 |
| P2 — Core raster/CRS/output | Windowed processing, masks, scaling, native metre CRS adapters, AOI, shared Work/Results, cache hash, manifests, safe atomic writes, report renderer | Unit and raster readback, invalid CRS detection, clip geometries, multiple reruns safe, interrupted run recoverable |
| P3 — ArcGIS Pro independent tools | `.pyt` + native parameter validation/conditional sensor compatibility; first Spectral Indices tool, grouped selection within supported UI | Native ArcGIS Pro tool opens and executes real product, report/readback; T2/T3 verified |
| P4 — Temperature & geological | Surface Temperature from official ST, BT/LSE where valid, geological bands/methods and ASTER profiles, thermal/urban | Scientific reference tests and in-host outputs; ASTER date/band gate; no LST from S2 |
| P5 — Mosaic + temporal | Quality-aware per-scene mosaics, scene IDs, dates, AOI, change detection; support multiple scenes shared results | Overlap/QA provenance, single vs multiple, AOI/no AOI, source scenes retained |
| P6 — Expanded catalog + environment | Version-pinned MIT offline catalog, validated multi-sensor indices, drought and energy gated models, dozens of methods only once validated | Original research citation, independent numerical checks, actual sensor/level support tests; blocked formulas disabled |
| P7 — QGIS native adapter | Processing provider and bilingual help, native CRS UI, map queue, equivalent outputs | Real QGIS compatible version test, readback, identical formula fixture, installer test |
| P8 — High-accuracy advanced & modality | Hyperspectral sensors, SAR specialist, larger environmental products; optional more advanced UIs | Per product sensor+version+native host validation; never blanket claim support |
| P9 — Packaging + documentation | Install guides, website, help CHM optional, tutorials, English/Arabic screenshots and examples, GitHub community docs and releases | T4 clean system install, user-level workflow, links, help, outputs and license attribution verified |

## Cross-phase gates
1. One shared input and output API; no separate prerequisite preparation/mosaic tools.
2. All new indices have unique IDs, formulas, references, wavelength constraints and validated computed outputs; translated help and report sections.
3. No silent file replacement, missing data synthesis, unsupported band guessing, false screenshots/tests.
4. Reports and plans numbered and committed; `PROJECT_STATE.md` and the journal updated on each handoff.
5. Any source code import has documented immutable version, license and copyright notice; external proprietary GIS APIs do not become redistributed binaries.

### Phase 0 immediate plan template
Use `Development_Plans/TEMPLATES/PLAN_TEMPLATE.md` to instantiate `PLAN-0001_bootstrap.md` after the first agent inspection. If no native ArcGIS/QGIS host is available, do not claim a native acceptance test; record NOT RUN with details.
