# ATIAF | أطياف
**Advanced Thematic Imagery Analysis Framework (v1.0.0)**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](pyproject.toml)
[![ArcGIS Pro: 3.x](https://img.shields.io/badge/ArcGIS%20Pro-3.x%20Ready-brightgreen.svg)](arcgis_pro/)
[![QGIS: 3.x / 4.x](https://img.shields.io/badge/QGIS-3.x%20%2F%204.x%20Ready-forestgreen.svg)](qgis/atyaf/)
[![Tests: 93 passing](https://img.shields.io/badge/Tests-93%20passed-success.svg)](tests/)

An open-source, **free-first**, **offline-at-runtime** satellite imagery analysis framework providing native geoprocessing tools in **ArcGIS Pro** (via `arcgis_pro/ATIAF.pyt`) and **QGIS** (via `qgis/atyaf/` Processing Provider plugin), backed by a shared pure-Python computational core (`atyaf_core/`).

---

## Key Principles & Architecture

- **Independent Standalone Tools:** Every tool autonomously performs sensor auto-discovery, calibration validation, optional quality masking, multi-scene mosaic blending, true polygon AOI clipping, and report generation. No mandatory preparatory tools required.
- **Shared Computational Core (`atyaf_core/`):** A single pure-Python engine powers both the ArcGIS Pro Python Toolbox and the QGIS Processing Provider without duplicated math.
- **Strict Metric Projected CRS (Decision D-007):** Rejects unprojected geographic degrees (EPSG:4326). All physical calculations enforce projected linear units in metres.
- **Additive & Non-Destructive Workspace:** Never deletes or overwrites user imagery or previous results. Maintains `Work/` for reusable caching and `Results/` with run manifests and quality assessment logs.
- **Free-First & 100% Offline Computation:** Operates locally on unpacked satellite scenes (Landsat, Sentinel-2, ASTER, Sentinel-1) without requiring cloud credentials, API tokens, or internet connectivity during processing.
- **Sensor Modality Boundaries:** Strictly enforces physics boundaries—**"Never route SAR through optical equations"**; blocks thermal tools on thermal-free sensors (Sentinel-2); enforces Level-2 surface reflectance cubes for hyperspectral mineral unmixing.
- **Bilingual Interface & Documentation:** Fully synchronized English and Arabic user interfaces, parameters, help strings, and technical reports.

---

## The 6 Canonical Tools

| Tool | Thematic Domain | Primary Methods & Formulas | Supported Missions |
|---|---|---|---|
| **01. Spectral Indices** | Vegetation, Water, Soil, Burn, Moisture | 22 validated optical indices: NDVI, NDWI, MNDWI, NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW, NDBI, NBR, SAVI, EVI, BSI | Landsat 1–9, Sentinel-2, ASTER |
| **02. Surface Temperature** | Thermal Radiance, LST, Emissivity | Land Surface Temperature (Kelvin / Celsius) & Emissivity (LSE) via Sobrino et al. (2004) NDVI thresholds model | Landsat 4–9, ASTER TIR |
| **03. Thermal & Urban Analysis** | Urban Heat Islands, Thermal Variability | Urban Thermal Field Variance Index (UTFVI; 6-class comfort), Thermal Anomaly Hotspots ($z \ge 2.0$), SUHI | Landsat, ASTER |
| **04. Environmental Drought** | Surface Energy Balance & Drought | Liang (2001) broadband shortwave surface albedo ($\alpha$) & Temperature Vegetation Dryness Index (TVDI) trapezoid | Landsat, Sentinel-2 + LST |
| **05. Geological Analysis** | Mineral Alteration & Lithology | 8 diagnostic alteration ratios (ferric/ferrous iron, gossan, hydroxyl/clay alteration, alunite, silica). ASTER post-April 2008 SWIR degradation gate | ASTER, Landsat 4–9 |
| **06. Temporal Change** | Multi-Temporal Change & Burn Severity | dNDVI, dNBR with official USGS FIREMON 7-class Burn Severity classification, relative change %, standard deviation anomalies | Landsat, Sentinel-2 |

---

## Quick Start & Installation

### 1. Python Environment Setup
```bash
git clone https://github.com/ahmadibrahim4geo/ATIAF.git
cd ATIAF
pip install -e .
```

### 2. Verify Your Environment
Run the automated installation diagnostics to verify that your environment, packages, and host adapters are ready:
```bash
python tools/verify_installation.py
```

### 3. Usage in ArcGIS Pro
1. Open ArcGIS Pro.
2. In the **Catalog** pane, right-click **Toolboxes** &rarr; **Add Toolbox**.
3. Browse to `d:\My Software\ATIAF\arcgis_pro\ATIAF.pyt`.
4. All 6 tools are immediately available for geoprocessing, ModelBuilder, and Python scripting.

### 4. Usage in QGIS
1. Copy or symlink the `qgis/atyaf/` directory into your QGIS active profile plugins directory:
   - **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\atyaf`
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/atyaf`
2. Open QGIS and enable the plugin in **Plugins** &rarr; **Manage and Install Plugins** &rarr; **Installed** &rarr; check **ATIAF**.
3. All 6 algorithms will appear in the **Processing Toolbox** under `ATIAF | أطياف`.

---

## Verification & Testing Evidence

ATIAF adheres to strict completion evidence standards:

| Test Suite | Execution Command | Result |
|---|---|---|
| **Core & Engine Unit Tests** | `python -m unittest discover tests` | **93 tests passed (100%)** |
| **Native QGIS 4.2.3 Host Tests** | `& "C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" tests/native_qgis/test_qgis_provider.py` | **5 host tests passed** |
| **Package Structural QA** | `python tools/validate_package.py` | **Passed (313 md, 111 json)** |
| **Environment Verification** | `python tools/verify_installation.py` | **All 5 check tiers verified** |

---

## Documentation

- **Offline Documentation Portal:** Open [`docs/index.html`](docs/index.html) in any web browser.
- **Quick Start Guide:** [English](docs/en/QUICK_START.md) · [العربية](docs/ar/QUICK_START.md)
- **Scientific Methods & Citations:** [English](docs/en/SCIENTIFIC_METHODS.md) · [العربية](docs/ar/SCIENTIFIC_METHODS.md)
- **Sensor Download Guide:** [English](docs/en/SENSORS_AND_DOWNLOADS.md) · [العربية](docs/ar/SENSORS_AND_DOWNLOADS.md)
- **Advanced Modalities (SAR & Hyperspectral):** [English](docs/en/ADVANCED_MODALITIES.md) · [العربية](docs/ar/ADVANCED_MODALITIES.md)
- **Full Specification:** [English](PROJECT_SPECIFICATION.md) · [العربية](PROJECT_SPECIFICATION_AR.md)
- **Development Reports:** Chronological evidence in [`Reports/INDEX.md`](Reports/INDEX.md).

---

## Community & Contributing

Contributions, bug reports, and spectral index proposals are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md).

## License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.
Copyright &copy; 2026 Ahmed Ibrahim.
