"""Utility to build synthetic satellite scene fixtures for offline testing."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "synthetic_scenes"

def create_synthetic_fixtures():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Landsat 8 C2 L2
    l8_dir = FIXTURES_DIR / "landsat8_c2_l2"
    l8_dir.mkdir(parents=True, exist_ok=True)
    l8_prefix = "LC08_L2SP_176039_20230520_20230527_02_T1"
    mtl_content = f"""GROUP = L1_METADATA_FILE
  GROUP = METADATA_FILE_INFO
    LANDSAT_PRODUCT_ID = "{l8_prefix}"
    PROCESSING_LEVEL = "L2SP"
    COLLECTION_NUMBER = 02
  END_GROUP = METADATA_FILE_INFO
  GROUP = IMAGE_ATTRIBUTES
    SPACECRAFT_ID = "LANDSAT_8"
    SENSOR_ID = "OLI_TIRS"
    DATE_ACQUIRED = "2023-05-20"
    SCENE_CENTER_TIME = "08:15:23.123456Z"
    SUN_ELEVATION = 62.45
    SUN_AZIMUTH = 135.21
    CLOUD_COVER = 1.25
  END_GROUP = IMAGE_ATTRIBUTES
END_GROUP = L1_METADATA_FILE
"""
    (l8_dir / f"{l8_prefix}_MTL.txt").write_text(mtl_content, encoding="utf-8")
    for suffix in ["_SR_B1.TIF", "_SR_B2.TIF", "_SR_B3.TIF", "_SR_B4.TIF", "_SR_B5.TIF", "_SR_B6.TIF", "_SR_B7.TIF", "_ST_B10.TIF", "_QA_PIXEL.TIF", "_QA_RADSAT.TIF"]:
        (l8_dir / f"{l8_prefix}{suffix}").write_bytes(b"DUMMY_TIFF_DATA")

    # 2. Landsat 7 C2 L2
    l7_dir = FIXTURES_DIR / "landsat7_c2_l2"
    l7_dir.mkdir(parents=True, exist_ok=True)
    l7_prefix = "LE07_L2SP_176039_20230612_20230708_02_T1"
    l7_mtl = f"""GROUP = L1_METADATA_FILE
  GROUP = METADATA_FILE_INFO
    LANDSAT_PRODUCT_ID = "{l7_prefix}"
    PROCESSING_LEVEL = "L2SP"
  END_GROUP = METADATA_FILE_INFO
  GROUP = IMAGE_ATTRIBUTES
    SPACECRAFT_ID = "LANDSAT_7"
    SENSOR_ID = "ETM"
    DATE_ACQUIRED = "2023-06-12"
    SCENE_CENTER_TIME = "08:10:00Z"
    SUN_ELEVATION = 65.10
    SUN_AZIMUTH = 120.30
    CLOUD_COVER = 0.50
  END_GROUP = IMAGE_ATTRIBUTES
END_GROUP = L1_METADATA_FILE
"""
    (l7_dir / f"{l7_prefix}_MTL.txt").write_text(l7_mtl, encoding="utf-8")
    for suffix in ["_SR_B1.TIF", "_SR_B2.TIF", "_SR_B3.TIF", "_SR_B4.TIF", "_SR_B5.TIF", "_SR_B7.TIF", "_ST_B6.TIF", "_QA_PIXEL.TIF"]:
        (l7_dir / f"{l7_prefix}{suffix}").write_bytes(b"DUMMY_TIFF_DATA")

    # 3. Sentinel-2 L2A SAFE
    s2_safe = FIXTURES_DIR / "S2A_MSIL2A_20230615T082611_N0509_R121_T36RUU_20230615T121345.SAFE"
    img_10m = s2_safe / "GRANULE" / "L2A_T36RUU_A041674_20230615T083457" / "IMG_DATA" / "R10m"
    img_20m = s2_safe / "GRANULE" / "L2A_T36RUU_A041674_20230615T083457" / "IMG_DATA" / "R20m"
    img_10m.mkdir(parents=True, exist_ok=True)
    img_20m.mkdir(parents=True, exist_ok=True)

    s2_xml = """<?xml version="1.0" encoding="UTF-8"?>
<n1:Level-2A_User_Product xmlns:n1="https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd">
  <General_Info>
    <PRODUCT_URI>S2A_MSIL2A_20230615T082611_N0509_R121_T36RUU_20230615T121345.SAFE</PRODUCT_URI>
    <SPACECRAFT_NAME>Sentinel-2A</SPACECRAFT_NAME>
    <PRODUCT_START_TIME>2023-06-15T08:26:11.024Z</PRODUCT_START_TIME>
  </General_Info>
  <Quality_Indicators_Info>
    <Cloud_Coverage_Assessment>2.41</Cloud_Coverage_Assessment>
  </Quality_Indicators_Info>
  <Geometric_Info>
    <Tile_Angles>
      <Mean_Sun_Angle>
        <ZENITH_ANGLE>24.5</ZENITH_ANGLE>
        <AZIMUTH_ANGLE>128.2</AZIMUTH_ANGLE>
      </Mean_Sun_Angle>
    </Tile_Angles>
  </Geometric_Info>
</n1:Level-2A_User_Product>
"""
    (s2_safe / "MTD_MSIL2A.xml").write_text(s2_xml, encoding="utf-8")
    for b in ["B02", "B03", "B04", "B08"]:
        (img_10m / f"T36RUU_20230615T082611_{b}_10m.jp2").write_bytes(b"DUMMY_JP2")
    for b in ["B05", "B06", "B07", "B8A", "B11", "B12", "SCL"]:
        (img_20m / f"T36RUU_20230615T082611_{b}_20m.jp2").write_bytes(b"DUMMY_JP2")

    # 4. Sentinel-2 L1C SAFE
    s2_l1c = FIXTURES_DIR / "S2B_MSIL1C_20230710T082609_N0509_R121_T36RUU_20230710T121345.SAFE"
    s2_l1c_img = s2_l1c / "GRANULE" / "L1C_T36RUU" / "IMG_DATA"
    s2_l1c_img.mkdir(parents=True, exist_ok=True)
    l1c_xml = """<?xml version="1.0" encoding="UTF-8"?>
<n1:Level-1C_User_Product xmlns:n1="https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-1C.xsd">
  <General_Info>
    <PRODUCT_URI>S2B_MSIL1C_20230710T082609_N0509_R121_T36RUU_20230710T121345.SAFE</PRODUCT_URI>
    <SPACECRAFT_NAME>Sentinel-2B</SPACECRAFT_NAME>
    <PRODUCT_START_TIME>2023-07-10T08:26:09.024Z</PRODUCT_START_TIME>
  </General_Info>
</n1:Level-1C_User_Product>
"""
    (s2_l1c / "MTD_MSIL1C.xml").write_text(l1c_xml, encoding="utf-8")
    for b in ["B02", "B03", "B04", "B08"]:
        (s2_l1c_img / f"T36RUU_20230710T082609_{b}.jp2").write_bytes(b"DUMMY_JP2")

    # 5. ASTER Pre-2008 (Valid SWIR)
    ast_pre = FIXTURES_DIR / "AST_07_00305202005123456"
    ast_pre.mkdir(parents=True, exist_ok=True)
    ast_pre_met = """CALENDARDATE = "2005-05-20"
SOLARZENITHANGLE = 22.4
SOLARAZIMUTHANGLE = 130.1
"""
    (ast_pre / "AST_07.met").write_text(ast_pre_met, encoding="utf-8")
    for b in ["B01.tif", "B02.tif", "B3N.tif", "B04.tif", "B05.tif", "TIR10.tif"]:
        (ast_pre / b).write_bytes(b"DUMMY_TIF")

    # 6. ASTER Post-2008 (Degraded SWIR)
    ast_post = FIXTURES_DIR / "AST_07_00305202012123456"
    ast_post.mkdir(parents=True, exist_ok=True)
    ast_post_met = """CALENDARDATE = "2012-05-20"
SOLARZENITHANGLE = 20.1
SOLARAZIMUTHANGLE = 125.0
"""
    (ast_post / "AST_07.met").write_text(ast_post_met, encoding="utf-8")
    for b in ["B01.tif", "B02.tif", "B3N.tif", "B04.tif", "B05.tif"]:
        (ast_post / b).write_bytes(b"DUMMY_TIF")

    # 7. Parent folder structure with scenes and non-scene folders
    parent_dir = FIXTURES_DIR / "parent_study_area"
    parent_dir.mkdir(parents=True, exist_ok=True)

    # Sub scene 1: Landsat 8
    sc1 = parent_dir / "Scene1_Landsat"
    sc1.mkdir(parents=True, exist_ok=True)
    (sc1 / "LC08_L2SP_176039_20230520_MTL.txt").write_text(mtl_content, encoding="utf-8")
    for suffix in ["_SR_B2.TIF", "_SR_B3.TIF", "_SR_B4.TIF", "_SR_B5.TIF"]:
        (sc1 / f"LC08_L2SP_176039_20230520{suffix}").write_bytes(b"DUMMY")

    # Sub scene 2: ASTER pre-2008
    sc2 = parent_dir / "Scene2_ASTER_20050520"
    sc2.mkdir(parents=True, exist_ok=True)
    (sc2 / "AST_07.met").write_text(ast_pre_met, encoding="utf-8")
    for b in ["B01.tif", "B02.tif", "B3N.tif"]:
        (sc2 / b).write_bytes(b"DUMMY")

    # Folders that MUST be ignored
    (parent_dir / "Work" / "Preprocessing_Cache").mkdir(parents=True, exist_ok=True)
    (parent_dir / "Results" / "Spectral_Indices").mkdir(parents=True, exist_ok=True)
    (parent_dir / "Reports").mkdir(parents=True, exist_ok=True)
    (parent_dir / "unrelated_notes").mkdir(parents=True, exist_ok=True)
    (parent_dir / "unrelated_notes" / "readme.txt").write_text("Hello notes", encoding="utf-8")

if __name__ == "__main__":
    create_synthetic_fixtures()
    print("Synthetic fixtures created successfully.")
