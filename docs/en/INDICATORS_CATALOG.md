# ATIAF Comprehensive Scientific Indicators & Methods Catalog

**Advanced Thematic Imagery Analysis Framework (أطياف)**  
*Complete Scientific Reference, Sensor Support Matrix, Physical Formulas, and Practical Interpretation Guide*

---

## Table of Contents
1. [Introduction & Scientific Philosophy](#1-introduction--scientific-philosophy)
2. [Tool 01: Optical Spectral Indices (22 Indices)](#2-tool-01-optical-spectral-indices)
   - [Vegetation & Chlorophyll Family](#21-vegetation--chlorophyll-family)
   - [Water, Moisture & Snow Family](#22-water-moisture--snow-family)
   - [Soil & Built-Up Urban Family](#23-soil--built-up-urban-family)
   - [Tasseled Cap Orthogonal Transformations](#24-tasseled-cap-orthogonal-transformations)
3. [Tool 02: Land Surface Temperature & Emissivity](#3-tool-02-land-surface-temperature--emissivity)
4. [Tool 03: Urban Heat Islands & Thermal Comfort (UTFVI)](#4-tool-03-urban-heat-islands--thermal-comfort-utfvi)
5. [Tool 04: Environmental Drought & Surface Albedo](#5-tool-04-environmental-drought--surface-albedo)
6. [Tool 05: Geological Alteration & Mineral Indices](#6-tool-05-geological-alteration--mineral-indices)
7. [Tool 06: Multi-Temporal Change & Burn Severity](#7-tool-06-multi-temporal-change--burn-severity)
8. [Advanced Modalities: Radar (SAR) & Hyperspectral](#8-advanced-modalities-radar-sar--hyperspectral)
9. [Sensor & Mission Compatibility Summary Matrix](#9-sensor--mission-compatibility-summary-matrix)

---

## 1. Introduction & Scientific Philosophy
ATIAF (**أطياف**) provides a free-first, local-at-runtime, deterministic remote sensing computational core. All algorithms operate strictly on physical surface measurements (Bottom-Of-Atmosphere Surface Reflectance, Land Surface Temperature in Kelvin/Celsius, or Calibrated Radar Backscatter in Decibels).

### Core Quality Principles
- **No Double Scaling:** Pre-calibrated Surface Reflectance products (e.g., Landsat Collection 2 Level-2 or Sentinel-2 Level-2A) are detected via metadata and are never scaled twice.
- **Physical Sensor Gating:** Algorithms are strictly gated by physical sensor capability. For example, Land Surface Temperature is never calculated for Sentinel-2 because it lacks a thermal infrared sensor.
- **Quality-Aware Processing:** Valid pixel masks (excluding clouds, cloud shadows, cirrus, snow, and radiometric saturation) are applied before mathematical evaluation.

---

## 2. Tool 01: Optical Spectral Indices

### 2.1 Vegetation & Chlorophyll Family

#### NDVI — Normalized Difference Vegetation Index
- **Arabic Name:** مؤشر الفرق المعياري للغطاء النباتي
- **Formula:**
  $$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}}$$
- **Required Bands:** Red ($\approx 665\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B4, B5), Landsat 7 (B3, B4), Landsat 4-5 (B3, B4), Landsat 1-5 MSS (B5, B7), Sentinel-2 (B4, B8).
- **Physical Meaning & Practical Applications:**  
  Measures photosynthetic activity and canopy vigor by contrasting strong chlorophyll absorption in the Red region against strong mesophyll scattering in the Near-Infrared. Used globally for crop health monitoring, yield prediction, deforestation tracking, and phenology.
- **Value Interpretation Table:**
  | Value Range | Classification & Interpretation |
  |---|---|
  | $< 0.0$ | Open water bodies, clouds, deep shadows |
  | $0.00 - 0.15$ | Bare soil, desert sand, rocks, impervious urban surfaces |
  | $0.15 - 0.30$ | Sparse or senescent vegetation, shrublands, dry grass |
  | $0.30 - 0.60$ | Moderate vegetation cover, agricultural crops, grasslands |
  | $> 0.60$ | Dense, healthy, vigorous closed-canopy forest or peak crops |
- **Reference:** Rouse et al. (1974), *Monitoring the Vernal Advancement and Retrogradation of Natural Vegetation*.

---

#### GNDVI — Green Normalized Difference Vegetation Index
- **Arabic Name:** مؤشر الفرق المعياري الأخضر للغطاء النباتي
- **Formula:**
  $$\text{GNDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Green}}}{\rho_{\text{NIR}} + \rho_{\text{Green}}}$$
- **Required Bands:** Green ($\approx 560\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B3, B5), Landsat 7 (B2, B4), Landsat 4-5 (B2, B4), Sentinel-2 (B3, B8).
- **Physical Meaning & Practical Applications:**  
  Substitutes the Red band with Green, providing 4–5 times greater sensitivity to chlorophyll concentration variations in mature or dense canopies where standard NDVI saturates. Ideal for precision agriculture, nitrogen deficiency detection, and late-stage crop assessment.
- **Value Interpretation Table:**
  | Value Range | Classification |
  |---|---|
  | $< 0.0$ | Water bodies |
  | $0.0 - 0.2$ | Bare soil / dormant vegetation |
  | $0.2 - 0.5$ | Low to medium chlorophyll content |
  | $> 0.5$ | High chlorophyll concentration / peak active growth |
- **Reference:** Gitelson, A. A., & Merzlyak, M. N. (1996), *Remote Sensing of Environment*, 58(1), 31-48.

---

#### SAVI — Soil-Adjusted Vegetation Index
- **Arabic Name:** مؤشر الغطاء النباتي المعدل بتأثير التربة
- **Formula:**
  $$\text{SAVI} = \frac{(1 + L) \cdot (\rho_{\text{NIR}} - \rho_{\text{Red}})}{\rho_{\text{NIR}} + \rho_{\text{Red}} + L} \quad (L = 0.5)$$
- **Required Bands:** Red ($\approx 665\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2.
- **Physical Meaning & Practical Applications:**  
  Introduces an empirical soil-brightness correction factor ($L = 0.5$) that shifts the vegetation isolines to minimize background soil reflectance scattering. Crucial for semi-arid environments, early-stage crops, and arid rangelands with $<40\%$ vegetation cover.
- **Reference:** Huete, A. R. (1988), *Remote Sensing of Environment*, 25(3), 295-309.

---

#### MSAVI — Modified Soil-Adjusted Vegetation Index
- **Arabic Name:** مؤشر الغطاء النباتي المعدل للتربة الثاني
- **Formula:**
  $$\text{MSAVI} = \frac{2\rho_{\text{NIR}} + 1 - \sqrt{(2\rho_{\text{NIR}} + 1)^2 - 8(\rho_{\text{NIR}} - \rho_{\text{Red}})}}{2}$$
- **Required Bands:** Red ($\approx 665\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2.
- **Physical Meaning & Practical Applications:**  
  Completely eliminates the subjective manual selection of soil factor $L$ by calculating a continuous self-adjusting soil line function. Provides the highest accuracy in early crop emergence and hyper-arid zones.
- **Reference:** Qi, J., et al. (1994), *Remote Sensing of Environment*, 48(2), 119-126.

---

#### OSAVI — Optimized Soil-Adjusted Vegetation Index
- **Arabic Name:** مؤشر الغطاء النباتي المعدل الأمثل للتربة
- **Formula:**
  $$\text{OSAVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}} + 0.16}$$
- **Required Bands:** Red, NIR.
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2.
- **Physical Meaning & Practical Applications:**  
  Standardized optimization of SAVI with $L=0.16$, providing optimal soil background attenuation across agricultural canopy densities without requiring site calibration.
- **Reference:** Rondeaux, G., et al. (1996), *Remote Sensing of Environment*, 55(2), 95-107.

---

#### EVI — Enhanced Vegetation Index
- **Arabic Name:** مؤشر الغطاء النباتي المحسن
- **Formula:**
  $$\text{EVI} = 2.5 \cdot \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + 6.0\rho_{\text{Red}} - 7.5\rho_{\text{Blue}} + 1.0}$$
- **Required Bands:** Blue ($\approx 490\text{ nm}$), Red ($\approx 665\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B2, B4, B5), Landsat 7 (B1, B3, B4), Landsat 4-5 (B1, B3, B4), Sentinel-2 (B2, B4, B8).
- **Physical Meaning & Practical Applications:**  
  Optimizes the vegetation signal with improved sensitivity in high-biomass tropical rain forests and dense crops while decoupling the canopy background signal and reducing atmospheric aerosol influences via the Blue band.
- **Reference:** Huete, A., et al. (2002), *Remote Sensing of Environment*, 83(1-2), 195-213.

---

#### NDRE1 — Normalized Difference Red Edge Index 1
- **Arabic Name:** مؤشر الفرق المعياري لحافة الأحمر
- **Formula:**
  $$\text{NDRE1} = \frac{\rho_{\text{NIR}} - \rho_{\text{RedEdge1}}}{\rho_{\text{NIR}} + \rho_{\text{RedEdge1}}}$$
- **Required Bands:** Red Edge 1 ($\approx 705\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** **Sentinel-2 MSI (B5, B8)**. *(Automatically disabled on standard Landsat 4-8 which lack red-edge bands).*
- **Physical Meaning & Practical Applications:**  
  Capitalizes on the transition zone between Red absorption and NIR reflectance. Red-edge radiation penetrates deeper into multi-layered leaf canopies than red light, making NDRE the benchmark for nitrogen status, precision fertilization, and forest disease detection.
- **Reference:** Barnes, E. M., et al. (2000), *ASAE Annual International Meeting*.

---

#### VARI — Visible Atmospherically Resistant Index
- **Arabic Name:** المؤشر المرئي المقاوم لتأثيرات الغلاف الجوي
- **Formula:**
  $$\text{VARI} = \frac{\rho_{\text{Green}} - \rho_{\text{Red}}}{\rho_{\text{Green}} + \rho_{\text{Red}} - \rho_{\text{Blue}}}$$
- **Required Bands:** Blue, Green, Red (Visible only; no NIR required).
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2, RGB airborne/UAV sensors.
- **Physical Meaning & Practical Applications:**  
  Designed to estimate vegetation fraction using solely visible spectral channels while attenuating atmospheric scattering. Useful when NIR channels are saturated, uncalibrated, or on standard RGB imaging drones.
- **Reference:** Gitelson, A. A., et al. (2002), *Remote Sensing of Environment*, 82(2-3), 282-287.

---

#### GLI — Green Leaf Index
- **Arabic Name:** مؤشر الورق الأخضر
- **Formula:**
  $$\text{GLI} = \frac{(2\rho_{\text{Green}} - \rho_{\text{Red}} - \rho_{\text{Blue}})}{(2\rho_{\text{Green}} + \rho_{\text{Red}} + \rho_{\text{Blue}})}$$
- **Required Bands:** Blue, Green, Red.
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2, standard RGB imagery.
- **Physical Meaning & Practical Applications:**  
  Quantifies green leaf cover and turf quality directly from visible imagery. Values range from -1 (water/soil) to +1 (healthy green foliage).
- **Reference:** Louhaichi, M., et al. (2001), *International Journal of Remote Sensing*, 22(9), 1833-1844.

---

### 2.2 Water, Moisture & Snow Family

#### NDWI (McFeeters) — Normalized Difference Water Index
- **Arabic Name:** مؤشر الفرق المعياري للمياه (ماك فيترز)
- **Formula:**
  $$\text{NDWI}_{\text{McFeeters}} = \frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}}}$$
- **Required Bands:** Green ($\approx 560\text{ nm}$), NIR ($\approx 842\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B3, B5), Landsat 7 (B2, B4), Landsat 4-5 (B2, B4), Sentinel-2 (B3, B8).
- **Physical Meaning & Practical Applications:**  
  Maximizes water feature reflectance in the Green spectrum while minimizing Near-Infrared reflectance. Excellent for open water body mapping, reservoir volume tracking, shoreline delineation, and flood inundation mapping. Positive values ($> 0.0$) typically denote open water.
- **Reference:** McFeeters, S. K. (1996), *International Journal of Remote Sensing*, 17(7), 1425-1432.

---

#### MNDWI (Xu) — Modified Normalized Difference Water Index
- **Arabic Name:** مؤشر الفرق المعياري المعدل للمياه (شو)
- **Formula:**
  $$\text{MNDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$$
- **Required Bands:** Green ($\approx 560\text{ nm}$), SWIR-1 ($\approx 1610\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B3, B6), Landsat 7 (B2, B5), Landsat 4-5 (B2, B5), Sentinel-2 (B3, B11).
- **Physical Meaning & Practical Applications:**  
  Replaces NIR with Shortwave Infrared (SWIR-1). Because built-up urban features have significantly higher reflectance in SWIR than in NIR, MNDWI successfully suppresses urban built-up noise that often causes false positives in McFeeters NDWI. Highly recommended for urban water extraction.
- **Reference:** Xu, H. (2006), *International Journal of Remote Sensing*, 27(14), 3025-3033.

---

#### NDWI (Gao) / NDMI — Normalized Difference Moisture Index
- **Arabic Name:** مؤشر محتوى الرطوبة المعياري (جاو)
- **Formula:**
  $$\text{NDMI} = \frac{\rho_{\text{NIR}} - \rho_{\text{SWIR1}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR1}}}$$
- **Required Bands:** NIR ($\approx 842\text{ nm}$), SWIR-1 ($\approx 1610\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B5, B6), Landsat 7 (B4, B5), Landsat 4-5 (B4, B5), Sentinel-2 (B8, B11).
- **Physical Meaning & Practical Applications:**  
  Reflects canopy liquid water thickness and leaf internal structure. SWIR-1 radiation is strongly absorbed by water inside leaf spongy mesophyll tissue. Ideal for crop water stress detection, irrigation management, and forest wildfire vulnerability mapping.
- **Value Interpretation Table:**
  | NDMI Value | Canopy Moisture Condition |
  |---|---|
  | $< -0.2$ | Bare dry soil, rock, urban surfaces |
  | $-0.2 - 0.0$ | Very low moisture / severe water stress |
  | $0.0 - 0.2$ | Moderate moisture / slight drought stress |
  | $0.2 - 0.4$ | High moisture / healthy water content |
  | $> 0.4$ | Water-saturated vegetation / wetlands |
- **Reference:** Gao, B. C. (1996), *Remote Sensing of Environment*, 58(3), 257-266.

---

#### NDSI — Normalized Difference Snow Index
- **Arabic Name:** مؤشر الفرق المعياري للثلوج
- **Formula:**
  $$\text{NDSI} = \frac{\rho_{\text{Green}} - \rho_{\text{SWIR1}}}{\rho_{\text{Green}} + \rho_{\text{SWIR1}}}$$
- **Required Bands:** Green ($\approx 560\text{ nm}$), SWIR-1 ($\approx 1610\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B3, B6), Landsat 7 (B2, B5), Landsat 4-5 (B2, B5), Sentinel-2 (B3, B11).
- **Physical Meaning & Practical Applications:**  
  Capitalizes on the optical property of snow having very high visible reflectance but very low (absorbing) SWIR reflectance, whereas atmospheric water clouds remain highly reflective in both. Enables precise discrimination between snow cover and clouds. Values $\ge 0.4$ indicate snow cover.
- **Reference:** Hall, D. K., et al. (1995), *Remote Sensing of Environment*, 54(2), 127-140.

---

### 2.3 Soil & Built-Up Urban Family

#### NDBI — Normalized Difference Built-Up Index
- **Arabic Name:** مؤشر الفرق المعياري للمناطق العمرانية
- **Formula:**
  $$\text{NDBI} = \frac{\rho_{\text{SWIR1}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR1}} + \rho_{\text{NIR}}}$$
- **Required Bands:** NIR ($\approx 842\text{ nm}$), SWIR-1 ($\approx 1610\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B5, B6), Landsat 7 (B4, B5), Landsat 4-5 (B4, B5), Sentinel-2 (B8, B11).
- **Physical Meaning & Practical Applications:**  
  Exploits the higher reflectance of asphalt, concrete, tiles, and built-up structures in SWIR-1 compared to NIR. Widely used in urban sprawl analysis, impervious surface estimation, and smart city modeling. Positive values typically indicate built-up or bare urban areas.
- **Reference:** Zha, Y., et al. (2003), *International Journal of Remote Sensing*, 24(3), 583-594.

---

#### UI — Urban Index
- **Arabic Name:** المؤشر العمراني
- **Formula:**
  $$\text{UI} = \frac{\rho_{\text{SWIR2}} - \rho_{\text{NIR}}}{\rho_{\text{SWIR2}} + \rho_{\text{NIR}}}$$
- **Required Bands:** NIR ($\approx 842\text{ nm}$), SWIR-2 ($\approx 2190\text{ nm}$).
- **Supported Satellites:** Landsat 8-9 (B5, B7), Landsat 7 (B4, B7), Landsat 4-5 (B4, B7), Sentinel-2 (B8, B12).
- **Physical Meaning & Practical Applications:**  
  Utilizes the SWIR-2 channel for built-up classification, offering distinct contrast against surrounding bare agricultural soil compared to SWIR-1.
- **Reference:** Kawamura, M., et al. (1996), *International Archives of Photogrammetry and Remote Sensing*, 31, 247-252.

---

#### BSI — Bare Soil Index
- **Arabic Name:** مؤشر التربة المكشوفة
- **Formula:**
  $$\text{BSI} = \frac{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) - (\rho_{\text{NIR}} + \rho_{\text{Blue}})}{(\rho_{\text{SWIR1}} + \rho_{\text{Red}}) + (\rho_{\text{NIR}} + \rho_{\text{Blue}})}$$
- **Required Bands:** Blue, Red, NIR, SWIR-1 (4 bands).
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2.
- **Physical Meaning & Practical Applications:**  
  Separates bare soil and ploughed land from fallow, built-up surfaces, and vegetation by combining soil absorption/reflectance signatures across 4 bands. Crucial for land degradation, topsoil erosion risk, and post-harvest agricultural surveys.
- **Reference:** Rikimaru, T., et al. (2002), *International Archives of Photogrammetry and Remote Sensing*, 34(7), 1187-1192.

---

#### NBR & NBR2 — Normalized Burn Ratio
- **Arabic Name:** مؤشر نسبة الحريق المعيارية
- **Formulas:**
  $$\text{NBR} = \frac{\rho_{\text{NIR}} - \rho_{\text{SWIR2}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR2}}}, \quad \text{NBR2} = \frac{\rho_{\text{SWIR1}} - \rho_{\text{SWIR2}}}{\rho_{\text{SWIR1}} + \rho_{\text{SWIR2}}}$$
- **Required Bands:** NIR ($\approx 842\text{ nm}$), SWIR-1 ($\approx 1610\text{ nm}$), SWIR-2 ($\approx 2190\text{ nm}$).
- **Supported Satellites:** Landsat 8-9, Landsat 7, Landsat 4-5, Sentinel-2.
- **Physical Meaning & Practical Applications:**  
  Healthy green vegetation reflects strongly in NIR and absorbs in SWIR-2, whereas recently burned areas exhibit very low NIR reflectance and high SWIR-2 reflectance from charcoal, ash, and exposed soil. NBR is the gold standard for wildfire burn scar identification.
- **Reference:** Key, C. H., & Benson, N. C. (2006), *FIREMON: Fire Effects Monitoring and Inventory System*, USDA Forest Service.

---

### 2.4 Tasseled Cap Orthogonal Transformations
The Kauth-Thomas Tasseled Cap transformation rotates multispectral bands into three scientifically distinct, uncorrelated physical axes: **Brightness (TCB)**, **Greenness (TCG)**, and **Wetness (TCW)**.

- **TCB (Brightness):** Weighted total surface albedo (soil, rock, concrete).
- **TCG (Greenness):** Perpendicular vegetation contrast (chlorophyll and canopy biomass).
- **TCW (Wetness):** Canopy moisture, soil moisture, and surface liquid content.

ATIAF applies mission-specific, peer-reviewed transformation matrices:
- **Landsat 8-9 OLI (Baig et al. 2014):**
  $$\begin{aligned}
  \text{TCB} &= 0.3029 B_2 + 0.2786 B_3 + 0.4733 B_4 + 0.5599 B_5 + 0.5080 B_6 + 0.1872 B_7 \\
  \text{TCG} &= -0.2941 B_2 - 0.2430 B_3 - 0.5424 B_4 + 0.7276 B_5 + 0.0713 B_6 - 0.1608 B_7 \\
  \text{TCW} &= 0.1511 B_2 + 0.1973 B_3 + 0.3283 B_4 + 0.3407 B_5 - 0.7117 B_6 - 0.4572 B_7
  \end{aligned}$$
- **Landsat 7 ETM+ (Huang et al. 2002)**
- **Landsat 4-5 TM (Crist & Cicone 1984)**
- **Sentinel-2 MSI (Nedkov 2017)**

---

## 3. Tool 02: Land Surface Temperature & Emissivity

### Land Surface Temperature (LST)
- **Arabic Name:** درجة حرارة السطح
- **Output Units:** Kelvin (K) or Celsius (°C).
- **Supported Satellites:**
  - Landsat 8-9 OLI/TIRS Collection 2 Level-2 (Band 10 ST).
  - Landsat 7 ETM+ Collection 2 Level-2 (Band 6 ST).
  - Landsat 4-5 TM Collection 2 Level-2 (Band 6 ST).
  - ASTER AST_08 Surface Kinetic Temperature product.
  - **Strict Gate:** Sentinel-2 is rejected with a scientific diagnostic explaining the absence of thermal hardware.
- **Physical Meaning & Practical Applications:**  
  Measures the radiometric temperature of the terrestrial surface (soil, vegetation canopy, pavement). Essential for climate change studies, urban heat island analysis, agricultural evapotranspiration estimation, and geothermal prospecting.
- **Conversion Formulation (Landsat C2 L2):**
  $$T_K = \text{DN} \times 0.00341802 + 149.0, \quad T_{^\circ\text{C}} = T_K - 273.15$$

### Land Surface Emissivity (LSE) — Sobrino et al. (2004) Model
- **Arabic Name:** انبعاثية السطح الأرضي
- **Formula:**  
  Based on fractional vegetation cover ($P_v$) derived from NDVI:
  $$P_v = \left( \frac{\text{NDVI} - \text{NDVI}_{\text{soil}}}{\text{NDVI}_{\text{veg}} - \text{NDVI}_{\text{soil}}} \right)^2 \quad (\text{NDVI}_{\text{soil}}=0.2, \ \text{NDVI}_{\text{veg}}=0.5)$$
  $$\varepsilon = \begin{cases}
  0.985 & \text{if } \text{NDVI} < 0.0 \text{ (Open Water)} \\
  0.970 & \text{if } 0.0 \le \text{NDVI} < 0.2 \text{ (Bare Soil / Rock)} \\
  0.004 \cdot P_v + 0.986 & \text{if } 0.2 \le \text{NDVI} \le 0.5 \text{ (Mixed Vegetation)} \\
  0.990 & \text{if } \text{NDVI} > 0.5 \text{ (Dense Healthy Canopy)}
  \end{cases}$$
- **Reference:** Sobrino, J. A., et al. (2004), *Remote Sensing of Environment*, 90(4), 434-440.

---

## 4. Tool 03: Urban Heat Islands & Thermal Comfort (UTFVI)

### Urban Thermal Field Variance Index (UTFVI)
- **Arabic Name:** مؤشر تباين الحقل الحراري الحضري
- **Formula:**
  $$\text{UTFVI} = \frac{\text{LST} - \mu_{\text{LST}}}{\mu_{\text{LST}}}$$
  *(where $\mu_{\text{LST}}$ is the mean Land Surface Temperature across the scene or study area)*.
- **Physical Meaning & Practical Applications:**  
  Quantifies the microclimatic thermal impact of urban structures relative to the regional background baseline. It directly translates surface temperatures into standardized human and ecological comfort classifications.
- **6-Class Ecological Comfort Standard:**
  | UTFVI Value | Thermal Comfort Level | الحالة البيئية والحرارية |
  |---|---|---|
  | $< 0.000$ | Excellent | ممتاز — لا يوجد إجهاد حراري |
  | $0.000 - 0.005$ | Good | جيد — ظروف حرارية ملائمة |
  | $0.005 - 0.010$ | Normal | معتدل — إجهاد حراري طفيف |
  | $0.010 - 0.015$ | Bad | سيئ — إجهاد حراري ملحوظ |
  | $0.015 - 0.020$ | Worse | أسوأ — إجهاد حراري شديد |
  | $> 0.020$ | Worst | الأسوأ للغاية — خطر حراري حرج |
- **Reference:** Zhang, Y., et al. (2006), *International Journal of Remote Sensing*, 27(18), 3983-3998.

### Thermal Hotspot Anomaly Mapping
- **Formula:**  
  Identifies statistical thermal outliers exceeding two standard deviations above the regional mean:
  $$\text{Hotspot} = \left( \frac{\text{LST} - \mu_{\text{LST}}}{\sigma_{\text{LST}}} \ge 2.0 \right)$$
- **Applications:** Pinpointing industrial thermal discharge, unshaded asphalt parking lots, heat-vulnerable low-income neighborhoods, and geothermal anomalies.

---

## 5. Tool 04: Environmental Drought & Surface Albedo

### Broadband Shortwave Surface Albedo ($\alpha$) — Liang (2001) Model
- **Arabic Name:** البيدو السطح عريض النطاق
- **Formula (Landsat):**
  $$\alpha = 0.356\rho_{\text{Blue}} + 0.130\rho_{\text{Red}} + 0.373\rho_{\text{NIR}} + 0.085\rho_{\text{SWIR1}} + 0.072\rho_{\text{SWIR2}} - 0.0018$$
- **Physical Meaning & Practical Applications:**  
  The fraction of incoming solar shortwave radiation reflected by the surface ($0 \le \alpha \le 1$). Crucial for surface energy budget calculations, glacier melting studies, desertification tracking, and microclimate modeling.
- **Reference:** Liang, S. (2001), *Remote Sensing of Environment*, 76(2), 213-223.

### Temperature Vegetation Dryness Index (TVDI)
- **Arabic Name:** مؤشر جفاف الغطاء النباتي الحراري
- **Formula:**
  $$\text{TVDI} = \frac{\text{LST} - \text{LST}_{\text{min}}}{\text{LST}_{\text{max}} - \text{LST}_{\text{min}}}$$
  *(where $\text{LST}_{\text{max}} = a_1 + b_1 \cdot \text{NDVI}$ represents the Dry Edge and $\text{LST}_{\text{min}} = a_2 + b_2 \cdot \text{NDVI}$ represents the Wet Edge in the triangular/trapezoidal feature space)*.
- **Value Interpretation Table:**
  | TVDI Value | Soil & Vegetation Moisture Status |
  |---|---|
  | $0.0 - 0.2$ | Wet / Water Saturated (No drought stress) |
  | $0.2 - 0.4$ | Normal moisture conditions |
  | $0.4 - 0.6$ | Moderate drought stress |
  | $0.6 - 0.8$ | Severe drought stress |
  | $0.8 - 1.0$ | Extreme drought / complete desiccation |
- **Reference:** Sandholt, I., et al. (2002), *Remote Sensing of Environment*, 79(2-3), 213-224.

---

## 6. Tool 05: Geological Alteration & Mineral Indices

Designed for mineral exploration, lithological mapping, and hydrothermal alteration zone identification.

| Index Name | Arabic Name | Formula / Band Roles | Target Mineral & Geological Application |
|---|---|---|---|
| **Iron Oxide** | نسبة أكاسيد الحديد | $\rho_{\text{Red}} / \rho_{\text{Blue}}$ | Detects hematite, goethite, limonite in oxidized gossan caps |
| **Ferric Iron ($\text{Fe}^{3+}$)** | نسبة الحديد ثلاثي التكافؤ | $\rho_{\text{Red}} / \rho_{\text{Green}}$ | Hydrothermal alteration zones and iron leaching |
| **Ferrous Iron ($\text{Fe}^{2+}$)** | نسبة الحديد ثنائي التكافؤ | $\rho_{\text{SWIR1}} / \rho_{\text{NIR}}$ | Mafic and ultramafic silicates (biotite, chlorite, amphibole) |
| **Clay / Hydroxyl Alteration** | نسبة تحورات الطين والهيدروكسيل | $\rho_{\text{SWIR1}} / \rho_{\text{SWIR2}}$ | Argillic and phyllic alteration (kaolinite, alunite, illite, montmorillonite) |
| **Gossan / Laterite** | مؤشر الجوسان واللاتريت | $\rho_{\text{SWIR1}} / \rho_{\text{Red}}$ | Weathered capping overlying massive sulfide ore deposits |
| **ASTER Quartz Index (QI)** | مؤشر الكوارتز الحراري | $\frac{\text{TIR}_{11} \cdot \text{TIR}_{11}}{\text{TIR}_{10} \cdot \text{TIR}_{12}}$ | Silicification zones and quartz-rich rocks (granite, quartzite) |
| **ASTER Carbonate Index (CI)** | مؤشر الكربونات الحراري | $\text{TIR}_{13} / \text{TIR}_{14}$ | Limestone, dolomite, marble, and carbonatite exploration |
| **ASTER Mafic Index (MI)** | مؤشر الصخور المافية الحراري | $\text{TIR}_{12} / \text{TIR}_{13}$ | Basalt, gabbro, pyroxenite, and peridotite identification |

> [!IMPORTANT]
> **ASTER Post-April 2008 Hardware Safeguard:**  
> In April 2008, the ASTER SWIR sensor suffered an unrecoverable cooling system failure. ATIAF strictly enforces this physical cutoff: any ASTER SWIR ratio requested on scenes acquired after April 2008 is automatically blocked with an explanatory warning to prevent false mineral detections.

---

## 7. Tool 06: Multi-Temporal Change & Burn Severity

### dNDVI — Delta NDVI
$$\text{dNDVI} = \text{NDVI}_{T_2} - \text{NDVI}_{T_1}$$
- **Negative Values:** Vegetation loss, logging, pest infestation, drought, urban clearing.
- **Positive Values:** Vegetation recovery, reforestation, seasonal greening.

### dNBR — Delta Normalized Burn Ratio (USGS FIREMON Standard)
$$\text{dNBR} = \text{NBR}_{\text{Pre-Fire}} - \text{NBR}_{\text{Post-Fire}}$$
Classified according to the official **USGS FIREMON Burn Severity Assessment**:
| dNBR Value Range | USGS Burn Severity Class | التصنيف المعتمد لشدة الحريق |
|---|---|---|
| $< -0.250$ | High Post-Fire Regrowth | نمو نباتي كثيف بعد الحريق |
| $-0.250 \text{ to } -0.100$ | Low Post-Fire Regrowth | تجدد نباتي طفيف |
| $-0.100 \text{ to } +0.100$ | Unburned | منطقة سليمة غير محترقة |
| $+0.100 \text{ to } +0.270$ | Low Severity | حريق منخفض الشدة |
| $+0.270 \text{ to } +0.440$ | Moderate-Low Severity | حريق متوسط-منخفض الشدة |
| $+0.440 \text{ to } +0.660$ | Moderate-High Severity | حريق متوسط-مرتفع الشدة |
| $> +0.660$ | High Severity | حريق شديد التدمير (احتراق كامل للتاج والتربة) |

---

## 8. Advanced Modalities: Radar (SAR) & Hyperspectral

### 8.1 Synthetic Aperture Radar (SAR) — Sentinel-1 C-SAR
> [!CAUTION]
> **Fundamental Remote Sensing Boundary:**  
> Microwave radar measures surface roughness, dielectric permittivity, and geometric canopy volume. **Never route SAR data through optical reflectance equations.**

- **Radiometric Calibration to Decibels ($\text{dB}$):**
  $$\sigma^0 (\text{dB}) = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$$
  Normalizes exponential backscatter values into standard decibel scales (typically $-30\text{ dB}$ to $0\text{ dB}$).
- **Cross-Polarization Ratio ($VH / VV$):**  
  Calculates structural volume scattering versus surface roughness.
- **Dual-Pol Radar Vegetation Index (RVI):**
  $$\text{RVI} = \frac{4 \cdot \sigma^0_{VH}}{\sigma^0_{VV} + \sigma^0_{VH}}$$
  Provides all-weather, cloud-penetrating biomass monitoring.
- **Lee Speckle Filter:** Adaptive spatial window filter that removes granular radar speckle noise while preserving sharp urban and structural edges.

### 8.2 Hyperspectral Exploration (EnMAP / PRISMA)
- **Spectral Angle Mapper (SAM):**
  $$\theta = \arccos \left( \frac{\mathbf{v} \cdot \mathbf{r}}{\|\mathbf{v}\| \|\mathbf{r}\|} \right)$$
  Calculates the spectral angle (in radians) between pixel vector $\mathbf{v}$ and reference laboratory mineral spectrum $\mathbf{r}$, invariant to illumination shading.
- **Continuum Removal & Absorption Feature Depth:** Quantifies diagnostic mineral absorption dip depths (e.g., Al-OH at $2200\text{ nm}$, Fe-OH at $2250\text{ nm}$, carbonate at $2330\text{ nm}$).

---

## 9. Sensor & Mission Compatibility Summary Matrix

| Satellite / Mission | Sensor Family | Standard Products | Supported Tools in ATIAF |
|---|---|---|---|
| **Landsat 8 & 9** | OLI / TIRS | Collection 2 Level-2 (SR, ST) | Tools 01, 02, 03, 04, 05, 06 |
| **Landsat 7** | ETM+ | Collection 2 Level-2 (SR, ST) | Tools 01, 02, 03, 04, 05, 06 |
| **Landsat 4 & 5** | TM | Collection 2 Level-2 (SR, ST) | Tools 01, 02, 03, 04, 05, 06 |
| **Landsat 1, 2, 3, 4, 5** | MSS | Level-1 (DN / Rad) | Tool 01 (NDVI, SAVI only via expert mode) |
| **Sentinel-2A & 2B** | MSI | Level-2A (BOA), Level-1C (TOA) | Tools 01, 04 (Albedo), 05 (Opt ratios), 06 *(Tool 02/03 gated: no thermal)* |
| **Terra ASTER** | VNIR / SWIR / TIR | AST_07 (SR), AST_08 (LST) | Tools 01, 02, 05 (TIR QI/CI/MI; SWIR gated post-2008) |
| **Sentinel-1A & 1C** | C-SAR | Level-1 GRD (IW / SM) | Advanced Modalities (SAR dB, RVI, Lee filter) |
| **EnMAP / PRISMA** | Hyperspectral | Level-2A BOA Cube | Advanced Modalities (SAM, Absorption Depth) |
