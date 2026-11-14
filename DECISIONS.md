# Decision Register — ATIAF (2026-11-13)
| ID | Decision | Status |
|---|---|---|
| D-001 | Project Arabic name «أطياف»; acronym **ATIAF**; official expansion **Advanced Thematic Imagery Analysis Framework** (Systematic would spell ASIAF). | Accepted name convention |
| D-002 | One native ArcGIS Pro toolbox containing multiple independent tools; QGIS adapter planned; common `atyaf_core`. | Accepted |
| D-003 | Every tool handles sensor input, processing, mosaic option, optional AOI, selected calculations, output and reporting end-to-end. | Accepted |
| D-004 | Single scene or multi-scene parent folder; preserve per-scene results, and quality-aware mosaic result when enabled. | Accepted |
| D-005 | All tools append to same `Work` / `Results` workspace; skip only verified reusable outputs. No silent delete/overwrite. | Accepted |
| D-006 | Last parameter is output directory; defaults to source folder; user can override; custom single/multiple destination organization as specification. | Accepted |
| D-007 | Native host projected CRS selector; no global EPSG/UTM default; projected metre-based output validation. | Accepted |
| D-008 | Optional expert band mapping; strict evidence for units/scale; missing critical metadata disables invalid calculations. | Accepted |
| D-009 | Add Results to Map optional; serial, host-safe loading, no excessive simultaneous additions. | Accepted |
| D-010 | Fully separate Arabic/English UI, docs, help, errors and reports; scientific acronyms stable. | Accepted |
| D-011 | Per-result reproducible report, formula, exact band files and metadata key/value provenance, log, QA and limitations. | Accepted |
| D-012 | MIT open source for original project; third-party copyright/licenses honored. | Accepted |
| D-013 | Local/free-first processing; image acquisition via linked external free portals, registered user accounts acceptable for download. | Accepted |
| D-014 | Index DataBase (IDB) is reference-only or optional authenticated lookup; no bulk redistribution under current API terms. | Accepted |
| D-015 | Scientific catalog local with MIT-compatible source(s) after pinned release/license audit; original scientific paper adjudicates names/formulas. | Accepted |
| D-016 | `AGENTS.md` and project-local plan/report/journal system mandatory; improve GIS-Development-Skills with reusable learnings, without automatically modifying external repo. | Accepted |
| D-017 | Primary development text/docs in English for efficiency, Arabic parallel documentation mandatory. | Accepted |
| D-018 | Geological/mineral and hyperspectral candidate capabilities included with capability gating; no misleading mineral confirmation. | Accepted |
| D-019 | Sensor and product support is global; native product structure discovery and product version/dates determine compatibility. | Accepted |
| D-020 | No mandatory third-party network access or external atmospheric inputs. Methods that physically require additional data stay gated. | Accepted |
