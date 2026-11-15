<p align="center"><img src="documentation/assets/atiaf-logo.png" width="380" alt="ATIAF logo"></p>
<p align="center"><img src="documentation/assets/atiaf-banner.png" width="100%" alt="Illustrative ATIAF workflow banner"></p>

# ATIAF

[![License: MIT](https://img.shields.io/badge/License-MIT-075f9c.svg)](LICENSE)
[![Development version](https://img.shields.io/badge/version-1.0.2.dev1-d99b26.svg)](CHANGELOG.md)
[![Headless checks](https://github.com/ahmadibrahim4geo/ATIAF/actions/workflows/structure-check.yml/badge.svg)](https://github.com/ahmadibrahim4geo/ATIAF/actions/workflows/structure-check.yml)

**Advanced Thematic Imagery Analysis Framework** · MIT · Local satellite imagery analysis.

[العربية](README.ar.md) · [Documentation portal](documentation/index.html) · [Quick start](documentation/en/QUICK_START.md) · [Evidence](Reports/INDEX.md)

One engine, **`atiaf_core` with I**, serves separate native ArcGIS Pro and QGIS adapters. Computation uses your locally downloaded/unpacked images, without provider login, API keys or automatic imagery downloads.

**1.0.2.dev1 is a development recovery build.** Earlier v1.0.0 stable-readiness claims are superseded by [report 0015](Reports/0015_recovery_audit.md). Synthetic tests, native host execution, real satellite products and clean installation are separate evidence levels. See [current state](PROJECT_STATE.md).

## At a glance

| Platform | Entry point | Scope |
|---|---|---|
| ArcGIS Pro | Native English/Arabic Python toolboxes | Requires your separately installed, licensed Pro environment |
| QGIS | Installable Processing provider ZIP | Uses your independently installed QGIS and its scientific dependencies |
| Shared Python core | `atiaf_core/` | One source for discovery, science gates, processing and provenance |
| Documentation | [Offline Index](index.html) · [English](documentation/en/QUICK_START.md) · [العربية](documentation/ar/QUICK_START.md) | Bilingual use guides, formulas, output interpretation and evidence |

**Local by design:** choose a sensor/product, supply imagery or explicit manual bands, select calculations, optionally mosaic/clip, choose a native projected metre CRS, then save. Work/Results accumulate without replacing earlier products. Optional map loading happens sequentially.

## First run

1. Keep the repository together. In Pro open [ATIAF.pyt](ArcGIS%20Pro%20Tools/ATIAF.pyt) for English or [ATIAF_AR.pyt](ArcGIS%20Pro%20Tools/ATIAF_AR.pyt) for Arabic. [Installation](documentation/en/INSTALLATION.md).
2. For QGIS build with `python tools/build_qgis_plugin.py`, install `QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev1.zip` using the native plugin manager, enable ATIAF and reopen old dialogs. Source stays under QGIS Tools/atiaf; the ZIP bundles core and bilingual HTML help. Tool language follows QGIS.
3. Follow **sensor/product → input → QA → optional mosaic → explicit calculations → optional polygon AOI → native projected metre CRS → optional map loading → output folder LAST**. No calculations are selected by default.
4. For NDVI select Landsat C2 L2 SR with red, NIR and QA assets. Check NDVI, leave mosaic off and AOI empty, reuse a suitable known source CRS, and inspect the raster plus `Results/Reports/index.html`.

### Obtain the QGIS package

After a successful [Headless package verification workflow](https://github.com/ahmadibrahim4geo/ATIAF/actions/workflows/structure-check.yml), download the **ATIAF-QGIS-development** artifact and extract its outer Actions archive to find the installable plugin ZIP. GitHub requires sign-in to download workflow artifacts. These are development builds, not stable releases.

To build locally from the repository root:

```bash
git clone https://github.com/ahmadibrahim4geo/ATIAF.git
cd ATIAF
python tools/build_qgis_plugin.py
```

The builder preserves existing packages. Use `--output` with a new filename for another build. Install the resulting ZIP in QGIS → Plugins → Manage and Install Plugins → Install from ZIP. Keep Pro/QGIS Python stacks separate; see [installation requirements](documentation/en/INSTALLATION.md).

## Six independent tools

| Tool | Choices | Current restrictions |
|---|---|---|
| Spectral Indices | Individual optical methods including NDVI, SAVI, EVI, MNDWI, NDMI, NDBI, NBR | Reflectance, bands, level and QA required; Tasseled Cap/Gao variant gated for review |
| Surface Temperature | One LST choice, Celsius/Kelvin; optional local NDVI/RTE derivation | Official ST or explicit local calibrated thermal/atmospheric/emissivity inputs; no optical-only LST; field accuracy unvalidated |
| Thermal & Urban | UTFVI/classification, hotspots, or both | Official LST; SUHI gated for urban/rural references |
| Environmental & Drought | TM/ETM+ broadband albedo | Current coefficients restricted to Landsat 4/5/7; TVDI/historical models gated |
| Geological & Mineral | Individual optical alteration ratios | Appropriate bands; indications do not confirm deposits; ASTER TIR methods gated |
| Temporal & Change | NDVI, NBR or LST difference | One scene per epoch, matching sensor/level, ordered known dates; T2 minus T1 |

Catalog presence is not runnable support. Incompatible selections stop with a reason. [Formula cards and sources](documentation/en/INDICATORS_CATALOG.md).

New development controls: [manual band selection](documentation/en/MANUAL_BANDS.md), thematic groups without calculation search, EVI2/NIRv, [NDVI-assisted thermal requirements](documentation/en/SURFACE_TEMPERATURE.md) and optional local NDVI classes. Generated EN/AR interpretation explains units/ranges/limitations; local classes preserve continuous data and are not an international classification standard. Source/numerical/native fixture evidence remains distinct from real-acquisition validation.

## Read the result, not just the color

The [calculation catalog](documentation/en/INDICATORS_CATALOG.md) documents the physical meaning, units, ranges and caveats of each method. For NDVI, high greenness is not a standalone plant-health diagnosis; negative values do not uniquely identify water. Optional local classes record your thresholds and rationale while retaining the continuous raster. Scientific reports keep input filenames, calibration, formulas, parameters and output paths.

## Validation and support

Observed local evidence for this development version: **140 headless tests, 11 native QGIS checks and 8 native ArcGIS Pro checks passed on synthetic fixtures**. Package/source identity, relocated QGIS execution and offline desktop/mobile documentation were also checked. [Detailed evidence](Reports/0021_consolidated_tools_interpretation_and_native_evidence.md).

Real acquisitions/field accuracy, clean-machine installation and complete interactive journeys remain unverified. Sentinel-1/SAR and hyperspectral helpers are preliminary, not complete native tools. Gated methods are documented as such; a catalog entry is not a promise of support for every scene.

## Development

In a separate compatible developer environment:

```bash
python -m pip install .
python tools/build_documentation.py
python tools/validate_package.py
python -m unittest discover tests
```

Native GIS tests run separately in their vendor runtimes. Never install arbitrary binary packages into Pro/QGIS to make a headless check pass. See [contributing](.github/CONTRIBUTING.md), [security/private data](.github/SECURITY.md) and [citation metadata](CITATION.cff). Cite each scientific method's original research alongside this software.

## Repository guide

| Folder | Purpose |
|---|---|
| `atiaf_core/` | Sole shared processing engine; no second implementation with Y |
| `ArcGIS Pro Tools/`, `QGIS Tools/` | Separate thin host adapters |
| `documentation/` | EN/AR help, offline HTML portal, assets; specifications/decisions/roadmaps in `project/` |
| `scientific_library/` | Scientific candidates, sensors and provenance; separate from runnable support |
| `tools/` | Developer maintenance, validation, environment checks and packaging; not GIS analysis tools |
| `tests/` | Synthetic regressions and native host checks |
| `Development_Plans/`, `Reports/` | Numbered plans and immutable evidence |

All tools append to shared `Work/` and `Results/`, preserve earlier products, and use a scene-named folder under a custom destination. Mosaic requires compatible same-day scenes. [Output details](documentation/en/TOOL_UI_AND_WORKSPACE.md).

Original code is MIT. Supplied logo/banner are used at the owner's request; the banner illustrates a workflow and is not runtime evidence. No bulk Index DataBase or external formula catalog is redistributed. [Licenses](development_resources/THIRD_PARTY_LICENSE_POLICY.md) · [Sources](development_resources/SOURCES.md) · [Agent contract](AGENTS.md).
