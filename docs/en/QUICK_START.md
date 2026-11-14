# ATIAF Quick Start Guide

**Advanced Thematic Imagery Analysis Framework (أطياف)**  
*Run your first satellite analysis in ArcGIS Pro or QGIS in under 5 minutes*

---

## 1. Prerequisites & Environment Check
Make sure Python dependencies are installed. You can verify your environment anytime with:
```powershell
python tools/verify_installation.py
```
This runs a 5-tier diagnostic checking NumPy, Rasterio, Shapely, PyProj, `atyaf_core` engines, the ArcGIS Pro `.pyt` syntax, and the QGIS plugin.

---

## 2. Using ATIAF in ArcGIS Pro (3.x)

1. **Add the Toolbox:**
   - If first time, run `Setup_ArcGIS_Pro_Environment.bat` inside `ArcGIS Pro Tools/` to install dependencies.
   - In ArcGIS Pro, open the **Catalog** pane (`View -> Catalog Pane`).
   - Right-click **Toolboxes** -> **Add Toolbox**.
   - Navigate to `d:\My Software\ATIAF\ArcGIS Pro Tools\` and select `ATIAF.pyt`.
2. **Open a Tool:**
   - Expand `ATIAF.pyt`. You will see all 6 canonical tools:
     - `01. Spectral Indices | المؤشرات الطيفية`
     - `02. Surface Temperature | درجة حرارة السطح`
     - `03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية`
     - `04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف`
     - `05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني`
     - `06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي`
3. **Configure Tool Parameters:**
   - **Sensor / Product:** Leave as `Auto-Detect from Metadata` (default).
   - **Imagery Input Folder:** Browse and select your unpacked satellite scene folder (e.g., `LC08_L2SP_...`).
   - **Apply Quality Mask:** Checked (default: True, removes clouds/shadows).
   - **Mosaic Multiple Scenes:** Check if processing a parent folder with multiple adjacent scenes.
   - **Indices Selection:** Check the desired indices (e.g., NDVI, MNDWI, NDMI).
   - **Study Area AOI Polygon (Optional):** Pick a polygon feature layer to clip directly during calculation.
   - **Output Projected CRS:** Pick any projected coordinate system with linear units in **metres** (e.g., your local UTM zone). *Note: Unprojected degrees (EPSG:4326) are strictly rejected per Decision D-007.*
   - **Output Folder (Last Parameter):** Defaults to your input folder. Change only if you want outputs elsewhere.
   - **Add Results to Map:** Check to display generated GeoTIFFs immediately in your active map.
4. **Click Run:**
   - The tool calculates all indices using windowed block processing.
   - Outputs are saved in `Results/<Category>/<Method>/...`.
   - The HTML report is generated at `Results/Reports/Runs/<RUN_ID>/report.html`.
   - The cumulative dashboard is updated at `Results/Reports/index.html`.

---

## 3. Using ATIAF in QGIS (3.x / 4.x)

1. **Enable the Plugin:**
   - Copy or symlink `QGIS Tools/atiaf` into your QGIS plugins folder:
     - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\atiaf`
   - In QGIS, go to **Plugins -> Manage and Install Plugins -> Installed**, and enable **ATIAF (أطياف)**.
2. **Open the Processing Toolbox:**
   - Open the **Processing Toolbox** (`Processing -> Toolbox` or `Ctrl+Alt+T`).
   - Locate the **ATIAF | أطياف** provider group.
3. **Execute an Algorithm:**
   - Double-click any of the 6 algorithms.
   - Select your unpacked imagery folder, configure options, and click **Run**.
4. **Inspect Results:**
   - Results are automatically layered into the QGIS Layers panel.
   - Open `Results/Reports/index.html` in any web browser to review the scientific run report!
