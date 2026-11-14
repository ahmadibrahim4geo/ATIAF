# Advanced Modalities: Radar (SAR) and Hyperspectral Gating

This document outlines the scientific specifications, modality classifications, and strict gating rules enforced in ATIAF for Synthetic Aperture Radar (SAR) and Hyperspectral sensors, in accordance with Specification Sections 1, 2, and 5.

---

## 1. Scientific Modality Classifications

Remote sensing sensors operate across fundamentally distinct physical regimes:

| Modality | Physical Measurement | Primary Sensors | Allowed Tool Domains | Strict Exclusions |
|---|---|---|---|---|
| **Multispectral** | Optical Surface Reflectance ($\rho$) | Landsat OLI/ETM/TM, Sentinel-2 MSI, ASTER VNIR/SWIR | Spectral Indices, Geological Ratios, Temporal Change | Thermal (if no thermal band) |
| **Thermal Infrared** | Radiance ($L_{\lambda}$) & Temperature (K, °C) | Landsat TIRS, ASTER TIR, ECOSTRESS | Surface Temperature, Urban Heat Islands, TVDI | Optical reflectance indices |
| **Hyperspectral** | Contiguous Narrow-band Reflectance | EnMAP, PRISMA, EMIT, DESIS | Mineral Unmixing, SAM, Absorption Depths | L1 TOA cubes without atmospheric correction |
| **SAR (Radar)** | Active Microwave Backscatter ($\sigma^0, \gamma^0, \beta^0$) | Sentinel-1 C-SAR, ALOS-2 PALSAR-2, NISAR | Polarimetric Calibration, RVI, Decomposition, Coherence | **Never route through optical/thermal tools** |

---

## 2. SAR (Synthetic Aperture Radar) Modality Rules

### The Non-Negotiable Gating Rule
> **"Never route SAR through optical equations."** (Specification Section 2)

Optical spectral indices (NDVI, MNDWI, SAVI, EVI, etc.) assume solar illumination reflected by surface materials governed by electronic transitions and vibrational molecular bonds. SAR measures coherent microwave pulses backscattered by physical surface roughness, dielectric permittivity (moisture), and volumetric canopy structure. Applying optical index equations to SAR backscatter is physically invalid and strictly blocked by `ModalityRouter`.

### Calibration and Decibel (dB) Scaling
SAR data is calibrated to normalized radar cross section:
$$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$$

### Cross-Polarization Ratio
Measures volumetric vs surface scattering:
$$\text{Ratio} = \frac{\sigma^0_{VH}}{\sigma^0_{VV}} \quad \text{or} \quad \sigma^0_{VH,\text{dB}} - \sigma^0_{VV,\text{dB}}$$

### Dual-Polarization Radar Vegetation Index (RVI)
For Sentinel-1 dual-pol acquisitions ($VV, VH$):
$$RVI = \frac{4 \cdot \sigma^0_{VH}}{\sigma^0_{VV} + \sigma^0_{VH}}$$
Ranges from ~0 (bare smooth soil, calm water) to ~1 (dense multi-layered forest canopies).

### Speckle Reduction
Coherent radar fading (speckle) requires spatial adaptive filtering:
- **Lee Filter:** Preserves edges while smoothing homogeneous zones based on local variance $\sigma_I^2$ and theoretical noise variance $\sigma_v^2 = \frac{1}{\text{num\_looks}}$.
- **Refined Lee & Gamma-MAP:** Directional windowing to preserve linear features (roads, shorelines).

---

## 3. Hyperspectral Modality Rules

### Continuous Datacubes and Atmospheric Gating
Hyperspectral sensors provide contiguous narrow-band spectra (5–10 nm FWHM). ATIAF enforces:
1. **Level-2 Surface Reflectance Requirement:** Uncalibrated Top-of-Atmosphere (TOA) radiance cubes (e.g. EnMAP L1B, PRISMA L1) are strictly rejected from mineral unmixing. Atmospheric absorption completely distorts narrow mineral absorption features.
2. **Water Vapor Masking:** Bands within atmospheric absorption windows (1350–1450 nm and 1800–1950 nm) are masked as unreliable unless corrected by validated local hygrometric models.

### Spectral Angle Mapper (SAM)
Computes the generalized $n$-dimensional angle between an image pixel spectrum $\mathbf{t}$ and a reference laboratory spectrum $\mathbf{r}$:
$$\alpha = \arccos\left(\frac{\mathbf{t} \cdot \mathbf{r}}{\|\mathbf{t}\| \|\mathbf{r}\|}\right)$$
SAM is illumination-invariant; scaling the brightness of a spectrum preserves $\alpha = 0$.

### Diagnostic Mineral Absorption Feature Depth
Measures continuum-removed absorption depth:
$$D = 1 - \frac{R(\lambda_0)}{R_{\text{continuum}}(\lambda_0)}$$

Standard diagnostic absorption features:
- **Al-OH Alteration (2205 nm):** Kaolinite, Alunite, Illite, Muscovite.
- **Mg-OH / Carbonate (2345 nm):** Chlorite, Talc, Epidote, Calcite, Dolomite.
- **Fe3+ Iron Oxides (900 nm):** Goethite, Hematite.
