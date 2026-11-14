# ATIAF — ArcGIS Pro Tools (أطياف)

Native ArcGIS Pro Python Toolbox (`ATIAF.pyt`) providing enterprise-grade, deterministic, 100% offline satellite remote sensing analysis inside ArcGIS Pro 3.x.

---

## 🛠️ Included Tools (صندوق الأدوات)

The toolbox exposes **6 independent canonical tools**:

1. **`01. Spectral Indices | المؤشرات الطيفية`**: Automated optical spectral indices (NDVI, NDWI, MNDWI, NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW, NDBI, NBR, NDSI, SAVI, EVI, BSI) with sensor auto-detection, quality masking, and AOI polygon clipping.
2. **`02. Surface Temperature | درجة حرارة السطح`**: Radiative transfer Land Surface Temperature (LST) and fractional vegetation emissivity modeling (Sobrino et al. 2004) with strict thermal capability gating.
3. **`03. Thermal & Urban Analysis | التحليل الحراري والحضري`**: Urban Thermal Field Variance Index (UTFVI), 6-class thermal comfort mapping, and thermal hotspot delineation (Z-score $\ge 2.0$).
4. **`04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف`**: Liang (2001) broadband surface albedo and Temperature Vegetation Dryness Index (TVDI).
5. **`05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي`**: 8 diagnostic alteration ratios (Clay, Ferrous, Iron Oxide, Hydrothermal, Gossan, Carbonate) with ASTER post-April 2008 SWIR cutoff enforcement.
6. **`06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي`**: Differenced indices (dNDVI, dLST), USGS Burn Severity classification (dNBR), and relative percentage change.

---

## 🚀 Quick Setup & Usage in ArcGIS Pro

### Step 1: Prepare Environment (One-Time Setup)
To ensure ArcGIS Pro's internal Python runtime has the required scientific libraries (`rasterio`, `shapely`, `pyproj`):
- Simply double-click **`Setup_ArcGIS_Pro_Environment.bat`** in this directory, **OR**
- In ArcGIS Pro, open **View** &rarr; **Python Window** and run:
  ```python
  import subprocess, sys
  subprocess.run([sys.executable, "-m", "pip", "install", "--user", "rasterio", "shapely", "pyproj"])
  ```

### Step 2: Add Toolbox in ArcGIS Pro
1. Open ArcGIS Pro.
2. In the **Catalog Pane** (`View -> Catalog Pane`), right-click on **Toolboxes** &rarr; **Add Toolbox**.
3. Browse to this directory (`ArcGIS Pro Tools/`) and select **`ATIAF.pyt`**.
4. Expand `ATIAF.pyt` to view and run any of the 6 tools!
