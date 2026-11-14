# -*- coding: utf-8 -*-
"""ATIAF — Advanced Thematic Imagery Analysis Framework (أطياف)
Native ArcGIS Pro Python Toolbox (.pyt)

Author: ATIAF Open Source Geospatial Project
License: MIT
"""

from collections import defaultdict
import os
from pathlib import Path
import sys

# Ensure atiaf_core / atyaf_core is reliably importable from toolbox location
def _resolve_project_root():
    if "__file__" in globals() and globals()["__file__"]:
        p = Path(globals()["__file__"]).resolve().parent
        for candidate in [p, p.parent, p.parent.parent]:
            if (candidate / "atiaf_core").is_dir() or (candidate / "atyaf_core").is_dir():
                return candidate
    cwd = Path.cwd().resolve()
    for candidate in [cwd, cwd.parent, cwd.parent.parent]:
        if (candidate / "atiaf_core").is_dir() or (candidate / "atyaf_core").is_dir():
            return candidate
    known = Path(r"D:\My Software\ATIAF")
    if (known / "atiaf_core").is_dir() or (known / "atyaf_core").is_dir():
        return known
    return Path.cwd().resolve()

PROJECT_ROOT = _resolve_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import arcpy
except ImportError:
    arcpy = None

CORE_IMPORT_ERROR = None
try:
    from atiaf_core.discovery import SceneScanner
    from atiaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
    from atiaf_core.temperature import EmissivityEngine, SurfaceTemperatureEngine
    from atiaf_core.urban import ThermalUrbanEngine
    from atiaf_core.environment import EnvironmentalDroughtEngine
    from atiaf_core.geology import GEOLOGICAL_CATALOG, GeologicalAnalysisEngine
    from atiaf_core.mosaic import MosaicStrategy, QualityMosaicEngine
    from atiaf_core.temporal import ChangeDetectionEngine
    from atiaf_core.raster import CRSManager
except Exception as _err:
    CORE_IMPORT_ERROR = str(_err)
    SceneScanner = None
    INDEX_CATALOG = {}
    SpectralIndicesEngine = None
    EmissivityEngine = None
    SurfaceTemperatureEngine = None
    ThermalUrbanEngine = None
    EnvironmentalDroughtEngine = None
    GEOLOGICAL_CATALOG = {}
    GeologicalAnalysisEngine = None
    MosaicStrategy = None
    QualityMosaicEngine = None
    ChangeDetectionEngine = None
    CRSManager = None


class Toolbox(object):
    def __init__(self):
        self.label = "ATIAF - Thematic Imagery Analysis Framework | أطياف"
        self.alias = "atiaf"
        self.description = (
            "Bilingual scientific satellite imagery analysis framework for ArcGIS Pro. "
            "أطياف: منظومة التحليل العلمي للمرئيات الفضائية"
        )
        self.tools = [
            SpectralIndicesTool,
            SurfaceTemperatureTool,
            ThermalUrbanTool,
            EnvironmentalDroughtTool,
            GeologicalAnalysisTool,
            TemporalChangeTool,
        ]


# ============================================================================
# Tool 01: Spectral Indices (المؤشرات الطيفية)
# ============================================================================
class SpectralIndicesTool(object):
    """Tool 01: Spectral Indices (المؤشرات الطيفية)
    Computes optical spectral indices (vegetation, water, soil, urban, burn, snow)
    with automated preprocessing, quality masking, optional mosaic, AOI polygon clipping,
    and reproducible scientific manifests.
    """

    def __init__(self):
        self.label = "01. Spectral Indices | المؤشرات الطيفية"
        self.description = (
            "Calculates validated optical spectral indices (NDVI, NDWI, MNDWI, NDMI, MSAVI, OSAVI, VARI, GLI, TCB, TCG, TCW, NDBI, NBR, NDSI, SAVI, EVI, BSI) "
            "with sensor auto-detection, quality masking, true polygon clipping, and run manifests."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        # 1. Sensor / Product
        param_sensor = arcpy.Parameter(
            displayName="Sensor / Product | القمر والمستشعر ومستوى المنتج",
            name="sensor_product",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None
        if param_sensor:
            param_sensor.filter.type = "ValueList"
            param_sensor.filter.list = [
                "Auto-Detect from Metadata (تلقائي من الميتاداتا)",
                "Landsat 8-9 OLI/TIRS C2 L2",
                "Landsat 7 ETM+ C2 L2",
                "Landsat 4-5 TM C2 L2",
                "Landsat 1-5 MSS L1",
                "Sentinel-2 MSI L2A (BOA)",
                "Sentinel-2 MSI L1C (TOA)",
                "ASTER AST_07 Surface Reflectance",
                "Manual Expert Mapping (تعيين يدوي خبير)",
            ]
            param_sensor.value = "Auto-Detect from Metadata (تلقائي من الميتاداتا)"

        # 2. Input Folder
        param_input = arcpy.Parameter(
            displayName="Imagery Input Folder | مجلد المرئية المفكوك أو المجلد الأب",
            name="input_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        ) if arcpy else None

        # 3. QA Masking
        param_qa_mask = arcpy.Parameter(
            displayName="Apply Quality / Cloud / Shadow Mask | تطبيق أقنعة الجودة والسحب والظلال",
            name="apply_qa_mask",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True

        # 4. Mosaic option
        param_mosaic = arcpy.Parameter(
            displayName="Mosaic Multiple Scenes | دمج المشاهد المتعددة (موزاييك)",
            name="enable_mosaic",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None
        if param_mosaic:
            param_mosaic.value = False

        # 5. Spectral indices multi-selection
        param_indices = arcpy.Parameter(
            displayName="Spectral Indices Selection | اختيار المؤشرات الطيفية",
            name="indices_selection",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True,
        ) if arcpy else None
        if param_indices:
            param_indices.filter.type = "ValueList"
            param_indices.filter.list = [
                f"{k} — {v.name_en} ({v.name_ar})" for k, v in INDEX_CATALOG.items()
            ]

        # 6. AOI & Projection
        param_aoi = arcpy.Parameter(
            displayName="Study Area AOI Polygon (Optional) | منطقة الدراسة (اختياري)",
            name="aoi_features",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None

        param_crs = arcpy.Parameter(
            displayName="Output Projected Coordinate System (Metres) | نظام الإحداثيات المسقط بالمتر",
            name="output_crs",
            datatype="GPCoordinateSystem",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None

        # 7. Output Folder (LAST parameter)
        param_output_folder = arcpy.Parameter(
            displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج (آخر خيار)",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None

        # Add to Map
        param_add_to_map = arcpy.Parameter(
            displayName="Add Results to Active Map | إضافة النتائج إلى الخريطة",
            name="add_to_map",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [
            param_sensor,
            param_input,
            param_qa_mask,
            param_mosaic,
            param_indices,
            param_aoi,
            param_crs,
            param_output_folder,
            param_add_to_map,
        ]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        param_sensor, param_input, _, _, param_indices, _, param_crs, param_output_folder, _ = parameters
        if param_input and param_input.value:
            in_val = str(param_input.value)
            if param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
                param_output_folder.value = in_val
            in_path = Path(in_val)
            if in_path.is_dir():
                try:
                    scan_res = SceneScanner.scan(in_path)
                    if scan_res.scenes:
                        first_scene = scan_res.scenes[0]
                        supported = SpectralIndicesEngine.get_supported_indices_for_scene(first_scene)
                        if supported and param_indices:
                            allowed = [f"{s.id} — {s.name_en} ({s.name_ar})" for s in supported]
                            param_indices.filter.list = allowed
                except Exception:
                    pass

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(
                    f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). "
                    "Run tools\\setup_arcgis_pro_env.bat to install."
                )
            return
        param_sensor, param_input, _, _, _, _, param_crs, param_output_folder, _ = parameters
        if param_crs and param_crs.value:
            crs_str = str(param_crs.value)
            try:
                val_res = CRSManager.validate_projected_metre(crs_str)
                if not val_res.is_valid_projected_metre:
                    param_crs.setErrorMessage(
                        f"Invalid CRS: {val_res.message} "
                        "ATIAF requires a projected coordinate reference system with linear units in metres."
                    )
            except Exception as e:
                param_crs.setWarningMessage(f"Could not verify CRS units: {e}")

        if param_input and param_input.value:
            in_path = Path(str(param_input.value))
            if not in_path.exists():
                param_input.setErrorMessage(f"Input path does not exist: {in_path}")
            elif not in_path.is_dir():
                param_input.setErrorMessage(f"Input path is not a directory: {in_path}")

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime is required to execute in ArcGIS Pro.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(
                f"Cannot execute tool: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). "
                "Please run tools\\setup_arcgis_pro_env.bat in the project directory."
            )
            return

        param_sensor, param_input, param_qa_mask, param_mosaic, param_indices, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters

        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else None
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        enable_mosaic = bool(param_mosaic.value) if param_mosaic else False
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        raw_indices = param_indices.valueAsText.split(";") if param_indices.valueAsText else []
        selected_ids = [s.strip("'\"").split(" — ")[0].strip() for s in raw_indices if s.strip()]

        arcpy.AddMessage("----------------------------------------------------------------------")
        arcpy.AddMessage("ATIAF — Advanced Thematic Imagery Analysis Framework (أطياف)")
        arcpy.AddMessage("Tool 01: Spectral Indices | المؤشرات الطيفية")
        arcpy.AddMessage("----------------------------------------------------------------------")
        arcpy.AddMessage(f"Input Directory: {in_folder}")
        arcpy.AddMessage(f"Selected Indices: {', '.join(selected_ids)}")

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            arcpy.AddError(f"No recognized satellite products found in: {in_folder}")
            return

        arcpy.AddMessage(f"Discovered {len(scan_res.scenes)} scene(s).")

        aoi_geom = None
        aoi_crs = None
        if param_aoi and param_aoi.value:
            try:
                desc = arcpy.Describe(param_aoi.value)
                aoi_crs = desc.spatialReference.name
                features = []
                with arcpy.da.SearchCursor(param_aoi.value, ["SHAPE@"]) as cursor:
                    for row in cursor:
                        features.append(row[0])
                if features:
                    union_geom = features[0]
                    for f in features[1:]:
                        union_geom = union_geom.union(f)
                    from shapely import wkt
                    aoi_geom = wkt.loads(union_geom.WKT)
                    arcpy.AddMessage("AOI polygon boundary loaded successfully.")
            except Exception as e:
                arcpy.AddWarning(f"Could not parse AOI geometry: {e}. Processing full extent.")

        all_output_rasters = []
        product_scene_map = defaultdict(list)

        for i, scene in enumerate(scan_res.scenes, start=1):
            arcpy.AddMessage(f"\n[{i}/{len(scan_res.scenes)}] Processing: {scene.metadata.scene_id}")
            for w in scene.metadata.warnings:
                arcpy.AddWarning(f"  [Warning] {w}")

            res = SpectralIndicesEngine.run_scene_indices(
                scene=scene,
                selected_index_ids=selected_ids,
                custom_destination=custom_out,
                aoi_geometry=aoi_geom,
                aoi_crs=aoi_crs,
                apply_qa_mask=apply_qa,
            )

            for p in res["executed_products"]:
                target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(target_path)
                product_scene_map[p["acronym"]].append((scene, Path(target_path)))
                arcpy.AddMessage(f"  -> Generated: {Path(target_path).name} (Valid pixels: {p['valid_pixels']})")

            for sk in res["skipped_indices"]:
                arcpy.AddWarning(f"  -> Skipped {sk['id']}: {sk['reason']}")

            arcpy.AddMessage(f"  Manifest written to: {res['run_dir']}")

        if enable_mosaic and len(scan_res.scenes) > 1:
            mosaic_target_root = custom_out if custom_out else in_folder
            arcpy.AddMessage("\nInitiating Multi-Scene Quality-Aware Mosaic Blending...")
            for idx_id, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths,
                        product_name=idx_id,
                        category="Spectral_Indices",
                        output_root=mosaic_target_root,
                        strategy=MosaicStrategy.HIGHEST_QUALITY,
                        aoi_geometry=aoi_geom,
                        aoi_crs=aoi_crs,
                    )
                    mosaic_path = mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path
                    all_output_rasters.append(mosaic_path)
                    arcpy.AddMessage(f"  -> Mosaic Generated: {Path(mosaic_path).name}")

        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                active_map = aprx.activeMap
                if active_map:
                    for raster_path in all_output_rasters:
                        if Path(raster_path).exists():
                            active_map.addDataFromPath(raster_path)
            except Exception as e:
                arcpy.AddWarning(f"Could not add layers to map: {e}")

        arcpy.AddMessage("\nATIAF processing completed successfully.")


# ============================================================================
# Tool 02: Surface Temperature (درجة حرارة السطح)
# ============================================================================
class SurfaceTemperatureTool(object):
    """Tool 02: Surface Temperature & Land Surface Emissivity (درجة حرارة السطح والانبعاثية)"""

    def __init__(self):
        self.label = "02. Surface Temperature | درجة حرارة السطح"
        self.description = (
            "Calculates Land Surface Temperature (LST) and Land Surface Emissivity (LSE from NDVI) "
            "from thermal products (Landsat C2 L2 ST, ASTER AST_08) with strict sensor verification."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        param_sensor = arcpy.Parameter(
            displayName="Sensor / Product | القمر والمستشعر ومستوى المنتج",
            name="sensor_product", datatype="GPString", parameterType="Optional", direction="Input",
        ) if arcpy else None
        if param_sensor:
            param_sensor.filter.type = "ValueList"
            param_sensor.filter.list = [
                "Auto-Detect from Metadata (تلقائي من الميتاداتا)",
                "Landsat 8-9 OLI/TIRS C2 L2 ST", "Landsat 7 ETM+ C2 L2 ST",
                "Landsat 4-5 TM C2 L2 ST", "ASTER AST_08 Surface Kinetic Temperature",
                "Manual Expert Mapping (تعيين يدوي خبير)",
            ]
            param_sensor.value = "Auto-Detect from Metadata (تلقائي من الميتاداتا)"

        param_input = arcpy.Parameter(
            displayName="Imagery Input Folder | مجلد المرئية المفكوك أو المجلد الأب",
            name="input_folder", datatype="DEFolder", parameterType="Required", direction="Input",
        ) if arcpy else None

        param_qa_mask = arcpy.Parameter(
            displayName="Apply Quality Mask | تطبيق أقنعة الجودة والسحب والظلال",
            name="apply_qa_mask", datatype="GPBoolean", parameterType="Optional", direction="Input",
        ) if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True

        param_mosaic = arcpy.Parameter(
            displayName="Mosaic Multiple Scenes | دمج المشاهد المتعددة (موزاييك)",
            name="enable_mosaic", datatype="GPBoolean", parameterType="Optional", direction="Input",
        ) if arcpy else None
        if param_mosaic:
            param_mosaic.value = False

        param_mode = arcpy.Parameter(
            displayName="Calculation Mode | نمط الحساب",
            name="calc_mode", datatype="GPString", parameterType="Required", direction="Input",
        ) if arcpy else None
        if param_mode:
            param_mode.filter.type = "ValueList"
            param_mode.filter.list = [
                "Land Surface Temperature (LST) | درجة حرارة السطح",
                "Land Surface Emissivity (LSE from NDVI) | انبعاثية السطح",
                "Both LST & Emissivity | كلاهما (الحرارة والانبعاثية)",
            ]
            param_mode.value = "Land Surface Temperature (LST) | درجة حرارة السطح"

        param_unit = arcpy.Parameter(
            displayName="Temperature Output Unit | وحدة قياس درجة الحرارة",
            name="temp_unit", datatype="GPString", parameterType="Required", direction="Input",
        ) if arcpy else None
        if param_unit:
            param_unit.filter.type = "ValueList"
            param_unit.filter.list = ["Celsius (°C) | مئوية", "Kelvin (K) | كلفن"]
            param_unit.value = "Celsius (°C) | مئوية"

        param_aoi = arcpy.Parameter(
            displayName="Study Area AOI Polygon (Optional) | منطقة الدراسة (اختياري)",
            name="aoi_features", datatype="GPFeatureRecordSetLayer", parameterType="Optional", direction="Input",
        ) if arcpy else None

        param_crs = arcpy.Parameter(
            displayName="Output Projected Coordinate System (Metres) | نظام الإحداثيات المسقط بالمتر",
            name="output_crs", datatype="GPCoordinateSystem", parameterType="Optional", direction="Input",
        ) if arcpy else None

        param_output_folder = arcpy.Parameter(
            displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج (آخر خيار)",
            name="output_folder", datatype="DEFolder", parameterType="Optional", direction="Input",
        ) if arcpy else None

        param_add_to_map = arcpy.Parameter(
            displayName="Add Results to Active Map | إضافة النتائج إلى الخريطة",
            name="add_to_map", datatype="GPBoolean", parameterType="Optional", direction="Input",
        ) if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [param_sensor, param_input, param_qa_mask, param_mosaic, param_mode, param_unit, param_aoi, param_crs, param_output_folder, param_add_to_map]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        param_sensor, param_input, _, _, _, _, _, param_crs, param_output_folder, _ = parameters
        if param_input and param_input.value:
            in_val = str(param_input.value)
            if param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
                param_output_folder.value = in_val

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Run tools\\setup_arcgis_pro_env.bat to install.")
            return
        param_sensor, param_input, _, _, param_mode, _, _, param_crs, _, _ = parameters
        if param_crs and param_crs.value:
            crs_str = str(param_crs.value)
            try:
                val_res = CRSManager.validate_projected_metre(crs_str)
                if not val_res.is_valid_projected_metre:
                    param_crs.setErrorMessage(f"Invalid CRS: {val_res.message} ATIAF requires projected metre CRS.")
            except Exception as e:
                param_crs.setWarningMessage(f"Could not verify CRS units: {e}")

        if param_input and param_input.value:
            in_path = Path(str(param_input.value))
            if not in_path.exists() or not in_path.is_dir():
                param_input.setErrorMessage("Valid imagery directory required.")
            else:
                try:
                    scan_res = SceneScanner.scan(in_path)
                    if scan_res.scenes:
                        for sc in scan_res.scenes:
                            if not sc.has_thermal():
                                param_input.setErrorMessage(f"Scene '{sc.metadata.scene_id}' lacks thermal bands.")
                                break
                except Exception:
                    pass

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime is required.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(f"Cannot execute tool: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Please run tools\\setup_arcgis_pro_env.bat.")
            return
        param_sensor, param_input, param_qa_mask, param_mosaic, param_mode, param_unit, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters
        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else None
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        enable_mosaic = bool(param_mosaic.value) if param_mosaic else False
        add_map = bool(param_add_to_map.value) if param_add_to_map else False
        mode_text = str(param_mode.valueAsText)
        unit_text = "Celsius" if "Celsius" in str(param_unit.valueAsText) else "Kelvin"

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            arcpy.AddError(f"No recognized satellite products in: {in_folder}")
            return

        all_output_rasters = []
        product_scene_map = defaultdict(list)

        for scene in scan_res.scenes:
            if not scene.has_thermal():
                continue
            methods = ["Emissivity_NDVI"] if "Emissivity" in mode_text and "Both" not in mode_text else (["Official_L2_ST", "Emissivity_NDVI"] if "Both" in mode_text else ["Official_L2_ST"])
            for m in methods:
                res = SurfaceTemperatureEngine.run_surface_temperature(
                    scene=scene, method=m, output_unit=unit_text, custom_destination=custom_out, apply_qa_mask=apply_qa
                )
                for p in res["executed_products"]:
                    target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                    all_output_rasters.append(target_path)
                    product_scene_map[p["product_name"]].append((scene, Path(target_path)))

        if enable_mosaic and len(scan_res.scenes) > 1:
            mosaic_target_root = custom_out if custom_out else in_folder
            for prod_name, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths, product_name=prod_name, category="Surface_Temperature", output_root=mosaic_target_root
                    )
                    all_output_rasters.append(mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path)

        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.activeMap:
                    for r_path in all_output_rasters:
                        if Path(r_path).exists():
                            aprx.activeMap.addDataFromPath(r_path)
            except Exception:
                pass


# ============================================================================
# Tool 03: Thermal & Urban Analysis (التحليل الحراري والحضري)
# ============================================================================
class ThermalUrbanTool(object):
    """Tool 03: Thermal & Urban Analysis (التحليل الحراري والحضري والجزر الحرارية)
    Calculates Urban Thermal Field Variance Index (UTFVI), thermal hotspots, and surface
    urban heat island (SUHI) intensity with thermal comfort zone classification.
    """

    def __init__(self):
        self.label = "03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية"
        self.description = (
            "Calculates Urban Thermal Field Variance Index (UTFVI), Thermal Hotspots (z >= 2.0 sigma), "
            "and thermal comfort classifications from thermal satellite products."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        param_sensor = arcpy.Parameter(displayName="Sensor / Product", name="sensor_product", datatype="GPString", parameterType="Optional", direction="Input") if arcpy else None
        param_input = arcpy.Parameter(displayName="Imagery Input Folder | مجلد المرئية", name="input_folder", datatype="DEFolder", parameterType="Required", direction="Input") if arcpy else None
        param_qa_mask = arcpy.Parameter(displayName="Apply Quality Mask | تطبيق أقنعة الجودة", name="apply_qa_mask", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True
        param_mosaic = arcpy.Parameter(displayName="Mosaic Multiple Scenes | دمج المشاهد (موزاييك)", name="enable_mosaic", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_mosaic:
            param_mosaic.value = False

        param_aoi = arcpy.Parameter(displayName="Study Area AOI Polygon (Optional)", name="aoi_features", datatype="GPFeatureRecordSetLayer", parameterType="Optional", direction="Input") if arcpy else None
        param_crs = arcpy.Parameter(displayName="Output Projected Coordinate System (Metres)", name="output_crs", datatype="GPCoordinateSystem", parameterType="Optional", direction="Input") if arcpy else None
        param_output_folder = arcpy.Parameter(displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج", name="output_folder", datatype="DEFolder", parameterType="Optional", direction="Input") if arcpy else None
        param_add_to_map = arcpy.Parameter(displayName="Add Results to Active Map", name="add_to_map", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [param_sensor, param_input, param_qa_mask, param_mosaic, param_aoi, param_crs, param_output_folder, param_add_to_map]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        _, param_input, _, _, _, _, param_output_folder, _ = parameters
        if param_input and param_input.value and param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
            param_output_folder.value = str(param_input.value)

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Run tools\\setup_arcgis_pro_env.bat to install.")
            return
        _, param_input, _, _, _, param_crs, _, _ = parameters
        if param_crs and param_crs.value:
            val_res = CRSManager.validate_projected_metre(str(param_crs.value))
            if not val_res.is_valid_projected_metre:
                param_crs.setErrorMessage(f"Invalid CRS: {val_res.message}")
        if param_input and param_input.value:
            in_path = Path(str(param_input.value))
            if in_path.is_dir():
                try:
                    scan = SceneScanner.scan(in_path)
                    for sc in scan.scenes:
                        if not sc.has_thermal():
                            param_input.setErrorMessage(f"Scene '{sc.metadata.scene_id}' lacks thermal bands. UTFVI/Hotspot analysis impossible.")
                            break
                except Exception:
                    pass

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime required.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(f"Cannot execute: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Please run tools\\setup_arcgis_pro_env.bat.")
            return
        _, param_input, param_qa_mask, param_mosaic, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters
        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else in_folder
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        scan_res = SceneScanner.scan(in_folder)
        all_output_rasters = []
        for sc in scan_res.scenes:
            if not sc.has_thermal():
                continue
            res = ThermalUrbanEngine.run_thermal_urban_analysis(scene=sc, custom_destination=custom_out, apply_qa_mask=apply_qa)
            for p in res["executed_products"]:
                target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(target_path)
                arcpy.AddMessage(f"Generated: {Path(target_path).name}")

        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.activeMap:
                    for r in all_output_rasters:
                        aprx.activeMap.addDataFromPath(r)
            except Exception:
                pass


# ============================================================================
# Tool 04: Environmental & Drought Analysis (التحليل البيئي ومؤشرات الجفاف)
# ============================================================================
class EnvironmentalDroughtTool(object):
    """Tool 04: Environmental & Drought Analysis (التحليل البيئي ومؤشرات الجفاف)
    Calculates broadband shortwave surface albedo (Liang 2001) and Temperature
    Vegetation Dryness Index (TVDI).
    """

    def __init__(self):
        self.label = "04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف"
        self.description = (
            "Calculates shortwave broadband surface albedo (Liang 2001) and Temperature "
            "Vegetation Dryness Index (TVDI) for drought and environmental monitoring."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        param_sensor = arcpy.Parameter(displayName="Sensor / Product", name="sensor_product", datatype="GPString", parameterType="Optional", direction="Input") if arcpy else None
        param_input = arcpy.Parameter(displayName="Imagery Input Folder | مجلد المرئية", name="input_folder", datatype="DEFolder", parameterType="Required", direction="Input") if arcpy else None
        param_qa_mask = arcpy.Parameter(displayName="Apply Quality Mask | تطبيق أقنعة الجودة", name="apply_qa_mask", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True
        param_mosaic = arcpy.Parameter(displayName="Mosaic Multiple Scenes | دمج المشاهد (موزاييك)", name="enable_mosaic", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_mosaic:
            param_mosaic.value = False

        param_albedo = arcpy.Parameter(displayName="Calculate Broadband Surface Albedo (Liang 2001) | حساب البيدو السطح", name="calc_albedo", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_albedo:
            param_albedo.value = True
        param_tvdi = arcpy.Parameter(displayName="Calculate TVDI Dryness Index | حساب مؤشر الجفاف TVDI", name="calc_tvdi", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_tvdi:
            param_tvdi.value = True

        param_aoi = arcpy.Parameter(displayName="Study Area AOI Polygon (Optional)", name="aoi_features", datatype="GPFeatureRecordSetLayer", parameterType="Optional", direction="Input") if arcpy else None
        param_crs = arcpy.Parameter(displayName="Output Projected Coordinate System (Metres)", name="output_crs", datatype="GPCoordinateSystem", parameterType="Optional", direction="Input") if arcpy else None
        param_output_folder = arcpy.Parameter(displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج", name="output_folder", datatype="DEFolder", parameterType="Optional", direction="Input") if arcpy else None
        param_add_to_map = arcpy.Parameter(displayName="Add Results to Active Map", name="add_to_map", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [param_sensor, param_input, param_qa_mask, param_mosaic, param_albedo, param_tvdi, param_aoi, param_crs, param_output_folder, param_add_to_map]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        _, param_input, _, _, _, _, _, _, param_output_folder, _ = parameters
        if param_input and param_input.value and param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
            param_output_folder.value = str(param_input.value)

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Run tools\\setup_arcgis_pro_env.bat to install.")
            return
        _, _, _, _, _, _, _, param_crs, _, _ = parameters
        if param_crs and param_crs.value:
            val_res = CRSManager.validate_projected_metre(str(param_crs.value))
            if not val_res.is_valid_projected_metre:
                param_crs.setErrorMessage(f"Invalid CRS: {val_res.message}")

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime required.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(f"Cannot execute: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Please run tools\\setup_arcgis_pro_env.bat.")
            return
        _, param_input, param_qa_mask, param_mosaic, param_albedo, param_tvdi, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters
        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else in_folder
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        do_alb = bool(param_albedo.value) if param_albedo else True
        do_tvdi = bool(param_tvdi.value) if param_tvdi else True
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        scan_res = SceneScanner.scan(in_folder)
        all_output_rasters = []
        for sc in scan_res.scenes:
            res = EnvironmentalDroughtEngine.run_environmental_analysis(
                scene=sc, calculate_albedo=do_alb, calculate_tvdi=do_tvdi, custom_destination=custom_out, apply_qa_mask=apply_qa
            )
            for p in res["executed_products"]:
                target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(target_path)
                arcpy.AddMessage(f"Generated: {Path(target_path).name}")

        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.activeMap:
                    for r in all_output_rasters:
                        aprx.activeMap.addDataFromPath(r)
            except Exception:
                pass


# ============================================================================
# Tool 05: Geological Analysis & Mineral Alteration (التحليل الجيولوجي)
# ============================================================================
class GeologicalAnalysisTool(object):
    """Tool 05: Geological Analysis & Mineral Alteration (التحليل الجيولوجي ونطاقات التحول المعدني)"""

    def __init__(self):
        self.label = "05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني"
        self.description = (
            "Calculates diagnostic mineral alteration ratios (Iron Oxide, Ferric Iron, Ferrous Iron, Clay Alteration, "
            "Gossan, ASTER QI/CI/MI) with sensor capability gating and ASTER post-April 2008 SWIR cutoff enforcement."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        param_sensor = arcpy.Parameter(displayName="Sensor / Product", name="sensor_product", datatype="GPString", parameterType="Optional", direction="Input") if arcpy else None
        param_input = arcpy.Parameter(displayName="Imagery Input Folder | مجلد المرئية", name="input_folder", datatype="DEFolder", parameterType="Required", direction="Input") if arcpy else None
        param_qa_mask = arcpy.Parameter(displayName="Apply Quality Mask | تطبيق أقنعة الجودة", name="apply_qa_mask", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True
        param_mosaic = arcpy.Parameter(displayName="Mosaic Multiple Scenes | دمج المشاهد (موزاييك)", name="enable_mosaic", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_mosaic:
            param_mosaic.value = False

        param_indices = arcpy.Parameter(displayName="Geological Indices Selection", name="indices_selection", datatype="GPString", parameterType="Required", direction="Input", multiValue=True) if arcpy else None
        if param_indices:
            param_indices.filter.type = "ValueList"
            param_indices.filter.list = [f"{k} — {v.name_en} ({v.name_ar}) [{v.target_mineral}]" for k, v in GEOLOGICAL_CATALOG.items()]

        param_aoi = arcpy.Parameter(displayName="Study Area AOI Polygon (Optional)", name="aoi_features", datatype="GPFeatureRecordSetLayer", parameterType="Optional", direction="Input") if arcpy else None
        param_crs = arcpy.Parameter(displayName="Output Projected Coordinate System (Metres)", name="output_crs", datatype="GPCoordinateSystem", parameterType="Optional", direction="Input") if arcpy else None
        param_output_folder = arcpy.Parameter(displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج", name="output_folder", datatype="DEFolder", parameterType="Optional", direction="Input") if arcpy else None
        param_add_to_map = arcpy.Parameter(displayName="Add Results to Active Map", name="add_to_map", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [param_sensor, param_input, param_qa_mask, param_mosaic, param_indices, param_aoi, param_crs, param_output_folder, param_add_to_map]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        _, param_input, _, _, param_indices, _, _, param_output_folder, _ = parameters
        if param_input and param_input.value and param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
            param_output_folder.value = str(param_input.value)

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Run tools\\setup_arcgis_pro_env.bat to install.")
            return
        _, _, _, _, _, _, param_crs, _, _ = parameters
        if param_crs and param_crs.value:
            val_res = CRSManager.validate_projected_metre(str(param_crs.value))
            if not val_res.is_valid_projected_metre:
                param_crs.setErrorMessage(f"Invalid CRS: {val_res.message}")

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime required.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(f"Cannot execute: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Please run tools\\setup_arcgis_pro_env.bat.")
            return
        _, param_input, param_qa_mask, param_mosaic, param_indices, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters
        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else in_folder
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        enable_mosaic = bool(param_mosaic.value) if param_mosaic else False
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        raw_indices = param_indices.valueAsText.split(";") if param_indices.valueAsText else []
        selected_ids = [s.strip("'\"").split(" — ")[0].strip() for s in raw_indices if s.strip()]

        scan_res = SceneScanner.scan(in_folder)
        all_output_rasters = []
        product_scene_map = defaultdict(list)

        for sc in scan_res.scenes:
            res = GeologicalAnalysisEngine.run_geological_analysis(
                scene=sc, selected_index_ids=selected_ids, custom_destination=custom_out, apply_qa_mask=apply_qa
            )
            for p in res["executed_products"]:
                target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(target_path)
                product_scene_map[p["product_name"]].append((sc, Path(target_path)))

        if enable_mosaic and len(scan_res.scenes) > 1:
            mosaic_target_root = custom_out if custom_out else in_folder
            for prod_name, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths, product_name=prod_name, category="Geological_Analysis", output_root=mosaic_target_root
                    )
                    all_output_rasters.append(mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path)

        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.activeMap:
                    for r in all_output_rasters:
                        aprx.activeMap.addDataFromPath(r)
            except Exception:
                pass


# ============================================================================
# Tool 06: Temporal Analysis & Change Detection (التحليل الزمني وتغير الغطاء)
# ============================================================================
class TemporalChangeTool(object):
    """Tool 06: Temporal Analysis & Change Detection (التحليل الزمني وتغير الغطاء الأرضي)"""

    def __init__(self):
        self.label = "06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي"
        self.description = (
            "Calculates multi-temporal differences (dNDVI, dNBR Burn Severity, dNDWI, dLST) between "
            "baseline (T1) and target (T2) satellite scenes with automated grid alignment."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        param_sensor = arcpy.Parameter(displayName="Sensor Family", name="sensor_product", datatype="GPString", parameterType="Optional", direction="Input") if arcpy else None
        param_t1 = arcpy.Parameter(displayName="Baseline Scene Folder (Time 1)", name="t1_folder", datatype="DEFolder", parameterType="Required", direction="Input") if arcpy else None
        param_t2 = arcpy.Parameter(displayName="Target Scene Folder (Time 2)", name="t2_folder", datatype="DEFolder", parameterType="Required", direction="Input") if arcpy else None
        param_qa_mask = arcpy.Parameter(displayName="Apply Quality Mask", name="apply_qa_mask", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_qa_mask:
            param_qa_mask.value = True

        param_metric = arcpy.Parameter(displayName="Change Metric Selection", name="metric_selection", datatype="GPString", parameterType="Required", direction="Input") if arcpy else None
        if param_metric:
            param_metric.filter.type = "ValueList"
            param_metric.filter.list = [
                "NDVI (Vegetation Phenology & Deforestation)",
                "NBR (Burn Severity)",
                "NDWI (Water / Moisture Dynamics)",
                "LST (Thermal Difference)",
            ]
            param_metric.value = "NDVI (Vegetation Phenology & Deforestation)"

        param_rel = arcpy.Parameter(displayName="Calculate Relative Percentage Change (%)", name="calc_relative", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_rel:
            param_rel.value = True
        param_classify = arcpy.Parameter(displayName="Generate Thematic Severity Classification", name="classify_severity", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_classify:
            param_classify.value = True

        param_aoi = arcpy.Parameter(displayName="Study Area AOI Polygon (Optional)", name="aoi_features", datatype="GPFeatureRecordSetLayer", parameterType="Optional", direction="Input") if arcpy else None
        param_crs = arcpy.Parameter(displayName="Output Projected Coordinate System (Metres)", name="output_crs", datatype="GPCoordinateSystem", parameterType="Optional", direction="Input") if arcpy else None
        param_output_folder = arcpy.Parameter(displayName="Output Folder (Last Parameter)", name="output_folder", datatype="DEFolder", parameterType="Optional", direction="Input") if arcpy else None
        param_add_to_map = arcpy.Parameter(displayName="Add Results to Active Map", name="add_to_map", datatype="GPBoolean", parameterType="Optional", direction="Input") if arcpy else None
        if param_add_to_map:
            param_add_to_map.value = False

        return [param_sensor, param_t1, param_t2, param_qa_mask, param_metric, param_rel, param_classify, param_aoi, param_crs, param_output_folder, param_add_to_map]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if not arcpy:
            return
        _, param_t1, _, _, _, _, _, _, _, param_output_folder, _ = parameters
        if param_t1 and param_t1.value and param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
            param_output_folder.value = str(param_t1.value)

    def updateMessages(self, parameters):
        if not arcpy:
            return
        if CORE_IMPORT_ERROR:
            if parameters and parameters[0]:
                parameters[0].setErrorMessage(f"ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Run tools\\setup_arcgis_pro_env.bat to install.")
            return
        _, _, _, _, _, _, _, _, param_crs, _, _ = parameters
        if param_crs and param_crs.value:
            val_res = CRSManager.validate_projected_metre(str(param_crs.value))
            if not val_res.is_valid_projected_metre:
                param_crs.setErrorMessage(f"Invalid CRS: {val_res.message}")

    def execute(self, parameters, messages):
        if not arcpy:
            raise RuntimeError("ArcPy runtime required.")
        if CORE_IMPORT_ERROR:
            messages.addErrorMessage(f"Cannot execute: ATIAF Core dependencies missing ({CORE_IMPORT_ERROR}). Please run tools\\setup_arcgis_pro_env.bat.")
            return
        _, param_t1, param_t2, param_qa_mask, param_metric, param_rel, param_classify, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters
        t1_path = Path(str(param_t1.value)).resolve()
        t2_path = Path(str(param_t2.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else t1_path
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        calc_rel = bool(param_rel.value) if param_rel else True
        classify_sev = bool(param_classify.value) if param_classify else True
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        metric_raw = str(param_metric.valueAsText)
        metric_code = "NDVI"
        if "NBR" in metric_raw:
            metric_code = "NBR"
        elif "NDWI" in metric_raw:
            metric_code = "NDWI"
        elif "LST" in metric_raw:
            metric_code = "LST"

        t1_scan = SceneScanner.scan(t1_path)
        t2_scan = SceneScanner.scan(t2_path)
        if not t1_scan.scenes or not t2_scan.scenes:
            arcpy.AddError("Valid satellite scenes required in both folders.")
            return

        t1_scene, t2_scene = t1_scan.scenes[0], t2_scan.scenes[0]

        if metric_code == "LST":
            res_t1 = SurfaceTemperatureEngine.run_surface_temperature(scene=t1_scene, method="Official_L2_ST", output_unit="Celsius", custom_destination=custom_out, apply_qa_mask=apply_qa)
            res_t2 = SurfaceTemperatureEngine.run_surface_temperature(scene=t2_scene, method="Official_L2_ST", output_unit="Celsius", custom_destination=custom_out, apply_qa_mask=apply_qa)
        else:
            res_t1 = SpectralIndicesEngine.run_scene_indices(scene=t1_scene, selected_index_ids=[metric_code], custom_destination=custom_out, apply_qa_mask=apply_qa)
            res_t2 = SpectralIndicesEngine.run_scene_indices(scene=t2_scene, selected_index_ids=[metric_code], custom_destination=custom_out, apply_qa_mask=apply_qa)

        t1_raster = Path(res_t1["executed_products"][0]["full_path"])
        t2_raster = Path(res_t2["executed_products"][0]["full_path"])

        change_res = ChangeDetectionEngine.run_change_detection(
            t1_raster_path=t1_raster, t2_raster_path=t2_raster, t1_scene_id=t1_scene.metadata.scene_id, t2_scene_id=t2_scene.metadata.scene_id,
            t1_date=t1_scene.metadata.acquisition_date, t2_date=t2_scene.metadata.acquisition_date, metric_name=metric_code,
            output_root=custom_out, calc_relative=calc_rel, classify_severity=classify_sev,
        )

        if add_map:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.activeMap:
                    for p in change_res["executed_products"]:
                        r_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                        if Path(r_path).exists():
                            aprx.activeMap.addDataFromPath(r_path)
            except Exception:
                pass
