# Satellite Sensors Guide & Free Data Acquisition Portals

**Advanced Thematic Imagery Analysis Framework (أطياف)**  
*How to download, extract, and use free satellite data in ATIAF without coding or API keys*

---

## 1. Quick Data Flow Overview
ATIAF operates on a **zero-cloud, local-first** principle:
1. **Download:** You download satellite scenes freely from official agencies (USGS, Copernicus, NASA).
2. **Extract:** Unpack the downloaded `.tar`, `.zip`, or `.tar.gz` archive completely into a normal folder.
3. **Select:** In ArcGIS Pro or QGIS, simply browse and pick that unpacked scene folder (or a parent directory with multiple scenes).
4. **Run:** ATIAF's automated metadata scanner detects the satellite mission, sensor, processing level, calibration coefficients, and band roles automatically!

---

## 2. Supported Missions & Recommended Free Portals

### 2.1 Landsat 8 & 9 (OLI / TIRS)
- **Official Free Portal:** [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- **Recommended Data Product:** `Landsat Collection 2 Level-2` (Surface Reflectance + Surface Temperature)
- **Spatial Resolution:** $30\text{ m}$ (Optical Reflectance & delivered Thermal grid)
- **Supported ATIAF Tools:** Tools 01, 02, 03, 04, 05, 06.
- **Scene Folder Structure (Unpacked):**
  ```text
  LC08_L2SP_176039_20230520_20230527_02_T1/
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_MTL.txt   <-- Metadata (Essential)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B2.TIF  <-- Blue (482 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B3.TIF  <-- Green (561 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B4.TIF  <-- Red (654 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B5.TIF  <-- NIR (865 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B6.TIF  <-- SWIR-1 (1608 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_SR_B7.TIF  <-- SWIR-2 (2200 nm)
  ├── LC08_L2SP_176039_20230520_20230527_02_T1_ST_B10.TIF <-- Thermal ST (10.9 µm)
  └── LC08_L2SP_176039_20230520_20230527_02_T1_QA_PIXEL.TIF <-- Cloud Mask
  ```

---

### 2.2 Sentinel-2A & 2B (MSI)
- **Official Free Portal:** [Copernicus Data Space Ecosystem (CDSE)](https://dataspace.copernicus.eu/browser/)
- **Recommended Data Product:** `Sentinel-2 Level-2A (BOA Surface Reflectance)`
- **Spatial Resolution:** $10\text{ m}$ (B2, B3, B4, B8), $20\text{ m}$ (Red Edge, SWIR), $60\text{ m}$ (Atmospheric)
- **Supported ATIAF Tools:** Tools 01, 04 (Albedo), 05 (Optical Ratios), 06.
- **Important Physical Boundary:** Sentinel-2 does not possess a thermal sensor. Tools 02 (LST) and 03 (Thermal Urban) are automatically blocked with a clear scientific message.
- **Scene Folder Structure (Unpacked `.SAFE`):**
  ```text
  S2A_MSIL2A_20230520T082601_N0509_R064_T36RUU_20230520T121500.SAFE/
  ├── MTD_MSIL2A.xml                                      <-- Root XML Metadata
  └── GRANULE/
      └── L2A_T36RUU_A041302_20230520T083424/
          ├── MTD_TL.xml
          └── IMG_DATA/
              ├── R10m/ (B02_10m.jp2, B03_10m.jp2, B04_10m.jp2, B08_10m.jp2)
              └── R20m/ (B05_20m.jp2, B06_20m.jp2, B07_20m.jp2, B11_20m.jp2, B12_20m.jp2, SCL_20m.jp2)
  ```

---

### 2.3 Terra ASTER (Advanced Spaceborne Thermal Emission and Reflection Radiometer)
- **Official Free Portal:** [NASA Earthdata Search](https://search.earthdata.nasa.gov/)
- **Recommended Data Products:**
  - `AST_07` / `AST_07XT` (Surface Reflectance VNIR/SWIR)
  - `AST_08` (Surface Kinetic Temperature TIR)
- **Spatial Resolution:** $15\text{ m}$ (VNIR), $30\text{ m}$ (SWIR), $90\text{ m}$ (TIR)
- **Special Historical Notice:** In April 2008, the ASTER SWIR sensor's cryocooler failed. ATIAF permits SWIR ratios only on scenes acquired before May 2008.

---

### 2.4 Sentinel-1A & 1C (C-SAR Radar)
- **Official Free Portal:** [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/) or [Alaska Satellite Facility (ASF Vertex)](https://search.asf.alaska.edu/)
- **Recommended Data Product:** `Sentinel-1 Level-1 GRD (Ground Range Detected)`
- **Spatial Resolution:** $\approx 10\text{ m}$ (Interferometric Wide Swath)
- **Supported Capabilities in ATIAF:** Radiometric calibration ($\sigma^0$ in dB), Cross-pol ratio ($VH/VV$), Radar Vegetation Index ($RVI$), and Lee speckle filtering.

---

## 3. Step-by-Step Acquisition Guide

1. **Create a Free Account:**  
   - Visit [USGS EarthExplorer](https://earthexplorer.usgs.gov/) or [Copernicus Browser](https://dataspace.copernicus.eu/browser/). Registration takes 2 minutes and is 100% free.
2. **Define Area of Interest (AOI):**  
   - Draw a polygon or upload a KML/Shapefile over your study site.
3. **Set Cloud Cover Filter:**  
   - Set maximum cloud cover to $< 10\%$ or $< 20\%$ for clean optical calculations.
4. **Select Dataset:**  
   - For Landsat: *Landsat -> Landsat Collection 2 Level-2 -> Landsat 8-9 OLI/TIRS C2 L2*.
   - For Sentinel: *Sentinel-2 -> Level-2A*.
5. **Download Product Bundle:**  
   - Download the full scene bundle (`.tar` for Landsat, `.zip` for Sentinel).
6. **Extract Archive:**  
   - Use 7-Zip, WinRAR, or native Windows extractor to unpack the archive completely.
7. **Point ATIAF to Folder:**  
   - Select the resulting unpacked folder in the ATIAF tool in ArcGIS Pro or QGIS!
