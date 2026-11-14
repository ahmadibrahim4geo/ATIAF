# Scientific Methods, Mathematical Formulations & Provenance Reference

**Advanced Thematic Imagery Analysis Framework (ATIAF | أطياف)**  
*Authoritative engineering reference for validated algorithms, sensor physics, and physical models*

> [!NOTE]
> For the comprehensive, user-friendly encyclopedia with individual satellite bands and value interpretation guides, please consult the [Master Indicators Catalog](INDICATORS_CATALOG.md).

---

## 1. Physical Units & Scaling Standards
All analytical operations in ATIAF operate strictly on true physical surface values:
1. **Surface Reflectance ($\rho$):** Floating-point values normalized to $[0.0, 1.0]$.
   - Landsat Collection 2 Level-2 Surface Reflectance is scaled by:
     $$\rho = \text{DN} \times 0.0000275 - 0.2$$
   - Sentinel-2 Level-2A BOA Reflectance is scaled by:
     $$\rho = \text{DN} / 10000.0$$
   - Products already scaled or delivered as floating-point are detected via metadata and are never scaled twice.
2. **Land Surface Temperature ($T$):** Floating-point temperature in Kelvin ($K$) or Celsius ($^\circ\text{C}$).
   - Landsat Collection 2 Level-2 ST is scaled by:
     $$T_K = \text{DN} \times 0.00341802 + 149.0, \quad T_{^\circ\text{C}} = T_K - 273.15$$
3. **Radar Backscatter ($\sigma^0$):** Decibels ($\text{dB}$) derived from linear power:
   $$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$$

---

## 2. Mathematical Formulations by Tool Family

### Tool 01: Optical Spectral Indices
- **NDVI (Normalized Difference Vegetation Index):**
  $$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}}$$
- **GNDVI (Green Normalized Difference Vegetation Index):**
  $$\text{GNDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Green}}}{\rho_{\text{NIR}} + \rho_{\text{Green}}}$$
- **SAVI (Soil-Adjusted Vegetation Index):**
  $$\text{SAVI} = \frac{(1 + L)(\rho_{\text{NIR}} - \rho_{\text{Red}})}{\rho_{\text{NIR}} + \rho_{\text{Red}} + L} \quad (L = 0.5)$$
- **MSAVI (Modified Soil-Adjusted Vegetation Index):**
  $$\text{MSAVI} = \frac{2\rho_{\text{NIR}} + 1 - \sqrt{(2\rho_{\text{NIR}} + 1)^2 - 8(\rho_{\text{NIR}} - \rho_{\text{Red}})}}{2}$$
- **OSAVI (Optimized Soil-Adjusted Vegetation Index):**
  $$\text{OSAVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}} + 0.16}$$
- **EVI (Enhanced Vegetation Index):**
  $$\text{EVI} = 2.5 \cdot \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + 6.0\rho_{\text{Red}} - 7.5\rho_{\text{Blue}} + 1.0}$$
- **NDRE1 (Normalized Difference Red Edge 1):**
  $$\text{NDRE1} = \frac{\rho_{\text{NIR}} - \rho_{\text{RedEdge1}}}{\rho_{\text{NIR}} + \rho_{\text{RedEdge1}}}$$
- **VARI (Visible Atmospherically Resistant Index):**
  $$\text{VARI} = \frac{\rho_{\text{Green}} - \rho_{\text{Red}}}{\rho_{\text{Green}} + \rho_{\text{Red}} - \rho_{\text{Blue}}}$$
- **GLI (Green Leaf Index):**
  $$\text{GLI} = \frac{2\rho_{\text{Green}} - \rho_{\text{Red}} - \rho_{\text{Blue}}}{2\rho_{\text{Green}} + \rho_{\text{Red}} + \rho_{\text{Blue}}}$$
- **NDWI (McFeeters Water Index):**
  $$\text{NDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}}}$$
- **MNDWI (Xu Modified Water Index):**
  $$\text{MNDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$$
- **NDMI / NDWI Gao (Moisture Index):**
  $$\text{NDMI} = \frac{\rho_{\text{NIR}} - \rho_{\text{SWIR1}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR1}}}$$
- **NDBI (Normalized Difference Built-Up Index):**
  $$\text{NDBI} = \frac{\rho_{\text{SWIR1}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR1}} + \rho_{\text{NIR}}}$$
- **UI (Urban Index):**
  $$\text{UI} = \frac{\rho_{\text{SWIR2}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR2}} + \rho_{\text{NIR}}}$$
- **BSI (Bare Soil Index):**
  $$\text{BSI} = \frac{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) - (\rho_{\text{NIR}} + \rho_{\text{Blue}})}{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) + (\rho_{\text{NIR}} + \rho_{\text{Blue}})}$$
- **NBR & NBR2 (Normalized Burn Ratio):**
  $$\text{NBR} = \frac{\rho_{\text{NIR}} - \rho_{\text{SWIR2}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR2}}}, \quad \text{NBR2} = \frac{\rho_{\text{SWIR1}} - \rho_{\text{SWIR2}}}{\rho_{\text{SWIR1}} + \rho_{\text{SWIR2}}}$$
- **NDSI (Normalized Difference Snow Index):**
  $$\text{NDSI} = \frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$$
- **Tasseled Cap Transformations (TCB, TCG, TCW):** Orthogonal rotation matrices specific to Landsat 8-9 (Baig et al. 2014), Landsat 7 (Huang et al. 2002), Landsat 4-5 (Crist & Cicone 1984), and Sentinel-2 (Nedkov 2017).

---

### Tool 02: Land Surface Temperature & Emissivity
- **Sobrino et al. (2004) NDVI Thresholds Model:**
  $$P_v = \left( \frac{\text{NDVI} - 0.2}{0.5 - 0.2} \right)^2$$
  $$\varepsilon = \begin{cases}
  0.985 & \text{if } \text{NDVI} < 0.0 \\
  0.970 & \text{if } 0.0 \le \text{NDVI} < 0.2 \\
  0.004 \cdot P_v + 0.986 & \text{if } 0.2 \le \text{NDVI} \le 0.5 \\
  0.990 & \text{if } \text{NDVI} > 0.5
  \end{cases}$$
- **Thermal Sensor Presence:** Strictly required. Sentinel-2 cannot compute LST.

---

### Tool 03: Urban Thermal Field Variance Index (UTFVI)
$$\text{UTFVI} = \frac{\text{LST} - \mu_{\text{LST}}}{\mu_{\text{LST}}}$$
Classified into 6 ecological comfort zones from Excellent ($<0$) to Worst ($>0.020$).
Thermal Hotspots identify pixels where:
$$z = \frac{\text{LST} - \mu_{\text{LST}}}{\sigma_{\text{LST}}} \ge 2.0$$

---

### Tool 04: Environmental Drought & Albedo
- **Liang (2001) Shortwave Broadband Surface Albedo ($\alpha$):**
  $$\alpha = 0.356\rho_{\text{Blue}} + 0.130\rho_{\text{Red}} + 0.373\rho_{\text{NIR}} + 0.085\rho_{\text{SWIR1}} + 0.072\rho_{\text{SWIR2}} - 0.0018$$
- **Temperature Vegetation Dryness Index (TVDI):**
  $$\text{TVDI} = \frac{\text{LST} - \text{LST}_{\text{min}}}{\text{LST}_{\text{max}} - \text{LST}_{\text{min}}}$$

---

### Tool 05: Geological Alterations & Mineral Indices
- **Iron Oxide:** $\rho_{\text{Red}} / \rho_{\text{Blue}}$
- **Ferric Iron:** $\rho_{\text{Red}} / \rho_{\text{Green}}$
- **Ferrous Iron:** $\rho_{\text{SWIR1}} / \rho_{\text{NIR}}$
- **Clay / Hydroxyl Alteration:** $\rho_{\text{SWIR1}} / \rho_{\text{SWIR2}}$
- **Gossan / Laterite:** $\rho_{\text{SWIR1}} / \rho_{\text{Red}}$
- **ASTER Quartz Index (QI):** $(\text{TIR}_{11} \cdot \text{TIR}_{11}) / (\text{TIR}_{10} \cdot \text{TIR}_{12})$
- **ASTER Carbonate Index (CI):** $\text{TIR}_{13} / \text{TIR}_{14}$
- **ASTER Mafic Index (MI):** $\text{TIR}_{12} / \text{TIR}_{13}$

---

### Tool 06: Multi-Temporal Change Detection
- **dNBR (USGS FIREMON 7-Class Standard):**
  $$\text{dNBR} = \text{NBR}_{\text{pre}} - \text{NBR}_{\text{post}}$$
- **dNDVI / dLST:**
  $$\Delta M = M_{T_2} - M_{T_1}$$
- **Relative Change (%):**
  $$\text{RelChange} = \frac{M_{T_2} - M_{T_1}}{|M_{T_1}| + 10^{-6}} \times 100\%$$

---

### Advanced Modalities: Radar SAR & Hyperspectral
- **Sentinel-1 SAR:** $\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$, Cross-Pol Ratio $= VH/VV$, Dual-Pol RVI $= 4 \cdot VH / (VV + VH)$, spatial Lee speckle filter.
- **Hyperspectral (EnMAP / PRISMA):** Spectral Angle Mapper (SAM) angle in radians $\theta = \arccos \frac{\mathbf{v} \cdot \mathbf{r}}{\|\mathbf{v}\| \|\mathbf{r}\|}$, absorption feature depth analysis.
