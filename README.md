<div align="center">

# ATIAF | أطياف
### **Advanced Thematic Imagery Analysis Framework**
*Enterprise-Grade, Deterministic, 100% Free & Offline Satellite Remote Sensing for ArcGIS Pro and QGIS*

[![Release: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](pyproject.toml)
[![ArcGIS Pro: 3.x](https://img.shields.io/badge/ArcGIS%20Pro-3.x%20Ready-brightgreen.svg)](arcgis_pro/)
[![QGIS: 3.x / 4.x](https://img.shields.io/badge/QGIS-3.x%20%2F%204.x%20Ready-forestgreen.svg)](qgis/atyaf/)
[![Tests: 99 passing](https://img.shields.io/badge/Tests-99%20passed-success.svg)](tests/)
[![Docs: GitHub Pages](https://img.shields.io/badge/Documentation-GitHub%20Pages-informational.svg)](https://ahmadibrahim4geo.github.io/ATIAF/)

[**Explore Interactive Portal**](https://ahmadibrahim4geo.github.io/ATIAF/) •
[**Master Indicators Catalog**](docs/en/INDICATORS_CATALOG.md) •
[**دليل المؤشرات بالعربية**](docs/ar/INDICATORS_CATALOG.md) •
[**Quick Start Guide**](docs/en/QUICK_START.md) •
[**Sensors & Download Guide**](docs/en/SENSORS_AND_DOWNLOADS.md)

</div>

---

## 🌟 Executive Overview

**ATIAF (أطياف)** is a pure-Python, free-first, offline-at-runtime remote sensing analysis framework engineered to eliminate complexity in satellite imagery processing. It provides seamless native geoprocessing tools inside **ArcGIS Pro** (via `arcgis_pro/ATIAF.pyt`) and **QGIS** (via `qgis/atyaf/` Processing Provider plugin), powered by an independent, high-performance computational core (`atyaf_core/`).

Users supply downloaded raw or analysis-ready satellite scenes; ATIAF automatically discovers mission metadata, validates physical calibrations, applies pixel-level quality masks (clouds, shadows, saturation), blends multi-scene mosaics, clips study area boundaries (AOI), computes physical models, and generates immutable, publication-ready bilingual HTML run reports.

```
                           ┌────────────────────────────────────────────────────────┐
                           │   Raw Satellite Scenes (Landsat, Sentinel, ASTER, SAR) │
                           └───────────────────────────┬────────────────────────────┘
                                                       │
                                            [SceneScanner Auto-Discovery]
                                                       │
                           ┌───────────────────────────▼────────────────────────────┐
                           │      atyaf_core Unified Computational Engine           │
                           │  - Projected Metric CRS Enforcement (Decision D-007)   │
                           │  - Quality Masking (Cloud, Shadow, Saturation)         │
                           │  - Windowed Block Processing & Multithreading          │
                           │  - Additive Non-Destructive Workspace (Work / Results) │
                           └───────┬───────────────────────┬────────────────┬───────┘
                                   │                       │                │
            ┌──────────────────────▼───────┐ ┌─────────────▼──────────────┐ │
            │ ArcGIS Pro Native (.pyt)     │ │ QGIS Native Processing     │ │
            │ 6 Canonical Tools            │ │ 6 Algorithms (atyaf:*)     │ │
            └──────────────────────────────┘ └────────────────────────────┘ │
                                                                            │
                                   ┌────────────────────────────────────────▼───────┐
                                   │  - Calibrated Analysis-Ready GeoTIFFs          │
                                   │  - Bilingual Interactive HTML Run Reports      │
                                   │  - Cumulative Reports Index (Reports/index.html│
                                   └────────────────────────────────────────────────┘
```

---

## 💎 Core Architecture & Scientific Principles

- **100% Free & Local-at-Runtime:** Operates entirely offline without API keys, cloud credits, third-party logins, or telemetry.
- **Dual Native GIS Integration:** Single computational codebase powering both ArcGIS Pro (native Python Toolbox) and QGIS (native Processing Provider) with complete parameter parity.
- **Autonomous Sensor Auto-Discovery:** Scans metadata files (`MTL.txt`, `MTD_MSIL2A.xml`, etc.) to automatically resolve sensor families, band paths, radiometric gains/biases, acquisition timestamps, and sun angles.
- **Strict Metric Projected CRS (Decision D-007):** Strictly rejects unprojected geographic degrees (`EPSG:4326`) with explicit guidance, ensuring all physical area and distance calculations occur in linear metres.
- **Additive & Non-Destructive Workspace:** Never deletes or overwrites raw imagery or prior analysis. Maintains an intelligent cache in `Work/` and categorized products in `Results/`.
- **Dynamic HTML Run Reports:** Every run produces a self-contained, responsive, styled bilingual `report.html` alongside machine-readable JSON/CSV manifests, while dynamically updating `Results/Reports/index.html`.
- **Physical Sensor Modality Gating:** Enforces rigorous scientific boundaries:
  - *No SAR Through Optical Math:* Radar backscatter is calibrated in decibels ($\text{dB}$) and volume ratios ($RVI$), never routed to optical equations.
  - *Thermal Presence Enforcement:* Blocks thermal tools on sensors lacking thermal infrared detectors (e.g. Sentinel-2).
  - *ASTER Hardware Safeguard:* Automatically blocks post-April 2008 ASTER SWIR ratios due to historical instrument cryocooler failure.

---

## 🛠️ The 6 Canonical Remote Sensing Tools

| Tool | Thematic Domain | Key Formulas & Scientific Methods | Supported Satellites |
|---|---|---|---|
| **01. Spectral Indices** | Vegetation, Water, Soil, Urban, Burn | **22 Optical Indices:** NDVI, GNDVI, SAVI, MSAVI, OSAVI, EVI, NDRE1, VARI, GLI, NDWI (McFeeters), MNDWI (Xu), NDMI (Gao), NDBI, UI, BSI, NBR, NBR2, NDSI, TCB, TCG, TCW | Landsat 1–9, Sentinel-2, ASTER |
| **02. Surface Temperature** | Thermal Radiance, LST, Emissivity | Land Surface Temperature (Kelvin / Celsius) & Emissivity (LSE) via **Sobrino et al. (2004)** NDVI fractional vegetation cover model | Landsat 4–9, ASTER TIR |
| **03. Urban Heat Islands** | Thermal Variability, Human Comfort | Urban Thermal Field Variance Index (**UTFVI**; 6-class ecological comfort: *Excellent* to *Worst*), Severe Thermal Hotspots ($z \ge 2.0\sigma$), SUHI | Landsat, ASTER TIR |
| **04. Environmental Drought** | Surface Energy Balance & Drought | **Liang (2001)** Broadband Shortwave Surface Albedo ($\alpha$) & Temperature Vegetation Dryness Index (**TVDI**) triangular feature space | Landsat, Sentinel-2 + LST |
| **05. Geological Analysis** | Mineral Alteration & Lithology | **8 Diagnostic Mineral Alteration Ratios:** Ferric Iron, Ferrous Iron, Iron Oxide, Clay/Hydroxyl (Al-OH), Gossan, ASTER Thermal Quartz (QI), Carbonate (CI), Mafic (MI) | ASTER (pre-2008 SWIR), Landsat 4–9 |
| **06. Temporal Change** | Multi-Temporal Change & Wildfire | Multi-temporal differences (dNDVI, dLST) and **dNBR** with official **USGS FIREMON 7-class Burn Severity** classification, relative % change | Landsat, Sentinel-2 |

> 📖 **Need detailed band numbers, formulas, and interpretation guides?**  
> Consult the [Master Scientific Indicators Catalog (English)](docs/en/INDICATORS_CATALOG.md) or [دليل المؤشرات العلمي (بالعربية)](docs/ar/INDICATORS_CATALOG.md).

---

## 🚀 Quick Start Guide

### 1. Environment Installation
Clone the repository and install dependencies in editable mode:
```bash
git clone https://github.com/ahmadibrahim4geo/ATIAF.git
cd ATIAF
pip install -e .
```

### 2. Run Automated Diagnostics
Verify all scientific dependencies, processing engines, and host adapters in one command:
```bash
python tools/verify_installation.py
```

### 3. Usage in ArcGIS Pro
1. Open ArcGIS Pro.
2. In the **Catalog** pane (`View -> Catalog Pane`), right-click **Toolboxes** &rarr; **Add Toolbox**.
3. Navigate to `arcgis_pro/ATIAF.pyt` and click **OK**.
4. Open any of the 6 tools, select your unpacked satellite scene folder, and click **Run**!

### 4. Usage in QGIS
1. Copy or symlink `qgis/atyaf` into your active QGIS profile plugins directory:
   - **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\atyaf`
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/atyaf`
2. In QGIS, navigate to **Plugins -> Manage and Install Plugins -> Installed**, and enable **ATIAF (أطياف)**.
3. Open the **Processing Toolbox** (`Ctrl+Alt+T`) to access all 6 algorithms under `ATIAF | أطياف`.

---

## 📊 Verification & DoneProof Evidence

ATIAF enforces uncompromising completion evidence standards. Every milestone is independently audited and backed by reproducible test runs:

| Test Suite | Scope & Target | Execution Command | Result |
|---|---|---|---|
| **Core Scientific Unit Tests** | Discovery, Raster, Indices, Thermal, Geology, Modalities, Workspace | `python -m unittest discover tests` | **99/99 passed (100%)** |
| **Native QGIS Integration Tests** | Real QgsApplication, Provider Registration, Algorithm Execution in QGIS 4.2.3 | `python-qgis.bat tests/native_qgis/test_qgis_provider.py` | **5/5 passed (100%)** |
| **Package Structural QA** | Markdown validation, JSON schemas, registry consistency | `python tools/validate_package.py` | **Passed (325 MD, 116 JSON)** |
| **Environment Verification** | 5-tier diagnostic checking dependencies, engines, .pyt, and QGIS plugin | `python tools/verify_installation.py` | **All 5 check tiers verified** |

---

## 📚 Documentation & Resources

- 🌐 **[Interactive GitHub Pages Documentation Portal](https://ahmadibrahim4geo.github.io/ATIAF/)** — Searchable web catalog with live filters and host walkthroughs.
- 📖 **[Master Scientific Indicators Catalog (EN)](docs/en/INDICATORS_CATALOG.md)** — Exhaustive scientific encyclopedia covering all 22 optical indices, thermal LST, urban heat, drought, and geological formulas.
- 📖 **[دليل المؤشرات والطرق العلمية الشامل (AR)](docs/ar/INDICATORS_CATALOG.md)** — الدليل العربي الشامل للمؤشرات والمستشعرات وتفسير النتائج.
- 🚀 **[Quick Start Guide](docs/en/QUICK_START.md)** · **[دليل البدء السريع](docs/ar/QUICK_START.md)**
- 🛰️ **[Satellite Sensors & Free Download Guide](docs/en/SENSORS_AND_DOWNLOADS.md)** · **[دليل بوابات التحميل المجانية](docs/ar/SENSORS_AND_DOWNLOADS.md)**
- 🔬 **[Scientific Methods Reference](docs/en/SCIENTIFIC_METHODS.md)** · **[الطرق والمعادلات العلمية](docs/ar/SCIENTIFIC_METHODS.md)**
- 📡 **[Advanced Modalities (SAR & Hyperspectral)](docs/en/ADVANCED_MODALITIES.md)** · **[الأنماط المتقدمة](docs/ar/ADVANCED_MODALITIES.md)**
- 📜 **[Full Engineering Specification](PROJECT_SPECIFICATION.md)** · **[المواصفات الهندسية](PROJECT_SPECIFICATION_AR.md)**
- 📋 **[Chronological Development Reports](Reports/INDEX.md)** — Detailed history of every implementation phase.

---

## 🤝 Contributing & Security

Contributions, feature requests, and scientific spectral index proposals are welcome. Please consult:
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Guidelines for code style, tests, and pull requests.
- [`SECURITY.md`](SECURITY.md) — Security policy and vulnerability disclosure protocol.
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) — Community standards.

---

## 📄 License & Attribution

This project is open-source software licensed under the **[MIT License](LICENSE)**.

```text
Copyright (c) 2026 Ahmed Ibrahim (ahmadibrahim4geo)
```
Developed with strict adherence to scientific reproducibility, open-source principles, and native GIS compatibility.
