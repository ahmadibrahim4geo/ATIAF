# PLAN-0012 — Interactive Documentation Portal & Comprehensive Scientific Indicators Catalog

- **Plan ID:** PLAN-0012
- **Revision:** r1
- **Status:** Completed
- **Related Reports:** [0012_interactive_docs_portal_and_scientific_catalog.md](../../Reports/0012_interactive_docs_portal_and_scientific_catalog.md)
- **Previous Plan:** [PLAN-0011 (Completed)](../Completed/PLAN-0011_comprehensive_audit_and_hardening.md)

---

## 1. Executive Summary & User Requirements
The user identified that existing documentation, while structurally present, does not sufficiently guide a remote sensing practitioner or end-user through:
1. The exact scientific purpose, physical meaning, and real-world practical applications of every index and indicator calculated by ATIAF.
2. The specific satellites, sensors, and required spectral bands (and wavelengths) supported for each indicator.
3. How to interpret the resulting numeric values and map classifications.
4. An intuitive, professional, interactive, searchable HTML documentation portal (`docs/index.html`) suitable for GitHub Pages deployment and project showcase.

This plan delivers a complete transformation of the documentation ecosystem in both English and Arabic.

---

## 2. Scope & Implementation Deliverables

### Task 1: Comprehensive Scientific Indicators Catalog in Markdown
Create `docs/en/INDICATORS_CATALOG.md` and `docs/ar/INDICATORS_CATALOG.md` detailing all calculation families:
- **22 Optical Spectral Indices:** NDVI, GNDVI, SAVI, EVI, NDRE1, NDWI (McFeeters), NDWI (Gao), MNDWI (Xu), NDBI, UI, NBR, NBR2, NDSI, BSI, NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW.
- **Surface Temperature & Emissivity:** LST (Kelvin & Celsius), Emissivity (Sobrino 2004 NDVI thresholds model), Brightness Temperature (Planck inversion).
- **Urban Heat Islands:** UTFVI (Urban Thermal Field Variance Index with 6 ecological comfort classes), Thermal Hotspots ($z \ge 2.0\sigma$), SUHI.
- **Environmental Drought:** Liang (2001) Broadband Shortwave Surface Albedo ($\alpha$), TVDI (Temperature Vegetation Dryness Index).
- **8 Diagnostic Geological Alteration Ratios:** Iron Oxide, Ferric Iron, Ferrous Iron, Clay/Hydroxyl Alteration, Gossan, ASTER Thermal Quartz (QI), Carbonate (CI), Mafic (MI).
- **Multi-Temporal Change Detection:** dNDVI, dLST, dNBR (USGS FIREMON 7-class burn severity), Relative Change %.
- **Advanced Modalities:** SAR Radar (Sentinel-1 dB backscatter, cross-pol ratio, Dual-pol RVI, Lee speckle filter); Hyperspectral (SAM angle, absorption feature depths).

For every indicator, the documentation will detail:
- Acronym, English Name, Arabic Name.
- Physical Definition & Real-World Practical Applications (agriculture, water management, urban planning, disaster response, mineral exploration, forestry).
- Mathematical Formula & Scientific Citation.
- Supported Satellites/Sensors (Landsat 8-9 OLI/TIRS, Landsat 7 ETM+, Landsat 4-5 TM, Landsat 1-5 MSS, Sentinel-2 MSI, ASTER, Sentinel-1 C-SAR, EnMAP/PRISMA) & Minimum Product Level.
- Required Band Roles & Wavelengths (nm).
- Value Range & Scientific Interpretation Table.

### Task 2: Core Documentation Overhaul (`docs/en/` & `docs/ar/`)
- Upgrade `SCIENTIFIC_METHODS.md`: Reflect fully implemented and validated models with direct references to the new catalog.
- Upgrade `SENSORS_AND_DOWNLOADS.md`: Provide practical step-by-step guides for free scene downloads (USGS EarthExplorer, Copernicus Data Space Ecosystem, NASA Earthdata), scene folder extraction, and auto-discovery.
- Upgrade `QUICK_START.md`: Clear, illustrated walkthrough for first-time users running tools in ArcGIS Pro and QGIS.

### Task 3: Interactive GitHub Pages Portal (`docs/index.html`)
Redesign `docs/index.html` into a world-class, responsive, client-side interactive single-page documentation portal:
- **Modern Layout:** Clean typography, dark gradient hero header, brand badge, responsive grid, zero external CDN dependencies (100% offline-compatible and GitHub Pages ready).
- **Interactive Live Search & Filterable Indicators Explorer:**
  - Real-time text search (searches acronyms, English names, Arabic names, applications, sensors).
  - Domain filter pills (Vegetation, Water, Urban/Soil, Thermal, Drought, Geology, Wildfire/Change, Radar/Hyperspectral).
  - Satellite/Sensor filter pills (Landsat 8/9, Landsat 7, Landsat 4/5, Sentinel-2, ASTER, Sentinel-1).
  - Indicator cards displaying application summaries, formulas, band roles, and interpretation guides.
- **Interactive Step-by-Step Host Setup Guides:**
  - Tabbed interface for ArcGIS Pro (`.pyt`), QGIS Processing Plugin (`qgis/atyaf`), and Python CLI.
- **Bilingual Experience:** Seamless English / Arabic switching with full RTL support.

---

## 3. Acceptance Criteria
- [ ] `docs/en/INDICATORS_CATALOG.md` and `docs/ar/INDICATORS_CATALOG.md` created with comprehensive coverage of all indices and tools.
- [ ] `docs/en/SCIENTIFIC_METHODS.md`, `docs/ar/SCIENTIFIC_METHODS.md`, `QUICK_START.md`, and `SENSORS_AND_DOWNLOADS.md` updated.
- [ ] `docs/index.html` fully upgraded into an interactive, searchable, filterable bilingual GitHub Pages portal.
- [ ] `python tools/validate_package.py` passes without errors.
- [ ] All 99 unit tests pass cleanly (`python -m unittest discover tests`).
- [ ] All 5 native QGIS tests pass cleanly (`python-qgis.bat tests/native_qgis/test_qgis_provider.py`).
- [ ] Delivery report `Reports/0012_interactive_docs_portal_and_scientific_catalog.md` authored.
- [ ] All indexes (`Development_Plans/INDEX.md`, `Reports/INDEX.md`, `PROJECT_STATE.md`) and Agent Journal updated.
