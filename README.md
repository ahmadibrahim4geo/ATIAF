# ATIAF | أطياف
**Advanced Thematic Imagery Analysis Framework**

An open-source, **free-first**, **offline-at-runtime** satellite imagery analysis toolbox planned for **ArcGIS Pro**, with an independently maintained **QGIS** adapter. This repository currently contains the **implementation-ready requirements, scientific governance, project-management rules, source registry, starter schemas, and agent bootstrap tooling**, not a tested working GIS add-on.

> **Start here:** Read [`AGENTS.md`](AGENTS.md), [`PROJECT_STATE.md`](PROJECT_STATE.md), and [`PROJECT_SPECIFICATION.md`](PROJECT_SPECIFICATION.md) **before editing or executing plans**. The one-time copyable agent prompt is in `START_AGENT_PROMPT.txt`.

## Core principles
- **Independent tools:** each tool discovers imagery, validates metadata, preprocesses only when needed, optionally mosaics/clips, calculates, saves, and reports. No required separate preprocessing/mosaic run.
- **Shared execution engine:** a single `atyaf_core/` powers all tools, with ArcPy / PyQGIS adapters; do not duplicate core logic.
- **Shared additive workspace:** `Work/` and `Results/` are reused; never erase user products. Existing valid products are reused only after metadata/parameter integrity checks.
- **No mandatory download or account:** users download and unpack imagery themselves; ATIAF recognizes supported provider products. Optional external catalogs must never gate normal analysis.
- **Sensor-aware:** formula availability depends on real bands, wavelengths, level, dates, QA, ancillary data, and verified processing pathways.
- **Native CRS selector:** use host GIS coordinate-system picker; no hardcoded EPSG/UTM default; require an appropriate projected metre-based output CRS (or reuse valid input).
- **Bilingual:** Arabic and English UI/help/reports; language separation except stable scientific acronyms and file identifiers.
- **Scientifically reproducible:** per-output equation, band-role mapping, source paths, actual scale/offset, masks, method, grid, uncertainty, references, and logs.
- **MIT:** open to modification, issues and pull requests, subject to separate licenses of external datasets and dependencies.

## Read the project
- [Complete English specification](PROJECT_SPECIFICATION.md) · [المواصفات العربية](PROJECT_SPECIFICATION_AR.md)
- [Roadmap EN](DEVELOPMENT_ROADMAP.md) · [خطة التنفيذ AR](DEVELOPMENT_ROADMAP_AR.md)
- [Scientific methods EN](docs/en/SCIENTIFIC_METHODS.md) · [الطرق العلمية AR](docs/ar/SCIENTIFIC_METHODS.md)
- [Sensor download guide EN](docs/en/SENSORS_AND_DOWNLOADS.md) · [المستشعرات والتحميل AR](docs/ar/SENSORS_AND_DOWNLOADS.md)
- [Source index](development_resources/SOURCES.md) · [Repository registry](development_resources/REPOSITORIES.md) · [Skill registry](development_resources/SKILLS_REGISTRY.md)
- [Agent working rules](AGENTS.md) · [Development plan index](Development_Plans/INDEX.md) · [Report index](Reports/INDEX.md)

## Project status
**Specification / handoff package; no implemented and validated ArcGIS or QGIS algorithms included.** The upcoming developer must install approved skills, build, test on real products, update evidence, and only then mark features supported.

## Community
Issues, bugs, index proposals and pull requests are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`LICENSE`](LICENSE).

Project: https://github.com/ahmadibrahim4geo (repository destination/name to be created or confirmed by owner). 2026 — Ahmed Ibrahim.
