# -*- coding: utf-8 -*-
"""QGIS Processing Algorithm: Surface Temperature (درجة حرارة السطح)."""

from collections import defaultdict
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from qgis.core import (
        QgsProcessing,
        QgsProcessingAlgorithm,
        QgsProcessingException,
        QgsProcessingParameterBoolean,
        QgsProcessingParameterCrs,
        QgsProcessingParameterEnum,
        QgsProcessingParameterFeatureSource,
        QgsProcessingParameterFile,
        QgsProcessingParameterFolderDestination,
    )
except ImportError:
    QgsProcessingAlgorithm = object
    QgsProcessing = None

from atyaf_core.discovery import SceneScanner
from atyaf_core.mosaic import MosaicStrategy, QualityMosaicEngine
from atyaf_core.temperature import EmissivityEngine, SurfaceTemperatureEngine


class SurfaceTemperatureAlgorithm(QgsProcessingAlgorithm):
    """Tool 02: Surface Temperature & Land Surface Emissivity (درجة حرارة السطح والانبعاثية) for QGIS."""

    INPUT_FOLDER = "INPUT_FOLDER"
    APPLY_QA = "APPLY_QA"
    ENABLE_MOSAIC = "ENABLE_MOSAIC"
    CALC_MODE = "CALC_MODE"
    TEMP_UNIT = "TEMP_UNIT"
    AOI = "AOI"
    CRS = "CRS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"

    def name(self):
        return "surface_temperature"

    def displayName(self):
        return "02. Surface Temperature | درجة حرارة السطح"

    def group(self):
        return "Thermal"

    def groupId(self):
        return "thermal"

    def shortHelpString(self):
        return (
            "Calculates Land Surface Temperature (LST) and Land Surface Emissivity (LSE from NDVI) "
            "from thermal products (Landsat C2 L2 ST, ASTER AST_08) with strict sensor verification.\n\n"
            "أطياف: حساب درجة حرارة السطح (LST) وانبعاثية السطح مع التحقق الفيزيائي الصارم من المستشعرات الحرارية."
        )

    def initAlgorithm(self, config=None):
        if not QgsProcessing:
            return

        self.addParameter(QgsProcessingParameterFile(self.INPUT_FOLDER, "Imagery Input Folder | مجلد المرئية", behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_QA, "Apply Quality Mask | تطبيق أقنعة الجودة", defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.ENABLE_MOSAIC, "Mosaic Multiple Scenes | دمج المشاهد (موزاييك)", defaultValue=False))

        self.modes = [
            "Land Surface Temperature (LST) | درجة حرارة السطح",
            "Land Surface Emissivity (LSE from NDVI) | انبعاثية السطح",
            "Both LST & Emissivity | كلاهما (الحرارة والانبعاثية)",
        ]
        self.addParameter(QgsProcessingParameterEnum(self.CALC_MODE, "Calculation Mode | نمط الحساب", options=self.modes, defaultValue=0))

        self.units = ["Celsius (°C) | مئوية", "Kelvin (K) | كلفن"]
        self.addParameter(QgsProcessingParameterEnum(self.TEMP_UNIT, "Temperature Output Unit | وحدة قياس الحرارة", options=self.units, defaultValue=0))

        self.addParameter(QgsProcessingParameterFeatureSource(self.AOI, "Study Area AOI Polygon (Optional) | منطقة الدراسة", types=[QgsProcessing.TypeVectorPolygon], optional=True))
        self.addParameter(QgsProcessingParameterCrs(self.CRS, "Output Projected Coordinate System (Metres) | نظام الإحداثيات المسقط", optional=True))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_FOLDER, "Output Folder (Last Parameter) | مجلد حفظ النتائج", optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        in_folder_val = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        if not in_folder_val:
            raise QgsProcessingException("Input imagery folder is required.")
        in_folder = Path(in_folder_val).resolve()
        if not in_folder.is_dir():
            raise QgsProcessingException(f"Invalid directory: {in_folder}")

        apply_qa = self.parameterAsBool(parameters, self.APPLY_QA, context)
        enable_mosaic = self.parameterAsBool(parameters, self.ENABLE_MOSAIC, context)
        mode_idx = self.parameterAsEnum(parameters, self.CALC_MODE, context)
        mode_str = self.modes[mode_idx]
        unit_idx = self.parameterAsEnum(parameters, self.TEMP_UNIT, context)
        unit_str = "Celsius" if unit_idx == 0 else "Kelvin"

        custom_out_val = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        custom_out = Path(custom_out_val).resolve() if custom_out_val else in_folder

        qgs_crs = self.parameterAsCrs(parameters, self.CRS, context)
        if qgs_crs and qgs_crs.isValid() and qgs_crs.isGeographic():
            raise QgsProcessingException("Invalid CRS: ATIAF strictly requires a projected metre CRS (Decision D-007).")

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            raise QgsProcessingException(f"No recognized satellite scenes found in: {in_folder}")

        # Check thermal bands presence
        for sc in scan_res.scenes:
            if not sc.has_thermal():
                raise QgsProcessingException(
                    f"Scene '{sc.metadata.scene_id}' ({sc.metadata.platform}) lacks thermal infrared bands. "
                    "Land Surface Temperature (LST) cannot be computed for Sentinel-2 or optical-only products."
                )

        aoi_geom = None
        aoi_crs = None
        aoi_source = self.parameterAsSource(parameters, self.AOI, context)
        if aoi_source:
            aoi_crs = aoi_source.sourceCrs().authid()
            features = list(aoi_source.getFeatures())
            if features:
                from shapely import wkt
                union_geom = None
                for feat in features:
                    if feat.hasGeometry():
                        sh_geom = wkt.loads(feat.geometry().asWkt())
                        union_geom = sh_geom if union_geom is None else union_geom.union(sh_geom)
                aoi_geom = union_geom

        all_output_rasters = []
        product_scene_map = defaultdict(list)

        for scene in scan_res.scenes:
            if feedback.isCanceled():
                break

            methods = []
            if "Emissivity" in mode_str and "Both" not in mode_str:
                methods = ["Emissivity_NDVI"]
            elif "Both" in mode_str:
                methods = ["Official_L2_ST", "Emissivity_NDVI"]
            else:
                methods = ["Official_L2_ST"]

            for m in methods:
                res = SurfaceTemperatureEngine.run_surface_temperature(
                    scene=scene,
                    method=m,
                    output_unit=unit_str,
                    custom_destination=custom_out,
                    aoi_geometry=aoi_geom,
                    aoi_crs=aoi_crs,
                    apply_qa_mask=apply_qa,
                )
                for p in res["executed_products"]:
                    target_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                    all_output_rasters.append(target_path)
                    product_scene_map[p["product_name"]].append((scene, Path(target_path)))
                    feedback.pushInfo(f"Generated: {Path(target_path).name}")

        if enable_mosaic and len(scan_res.scenes) > 1 and not feedback.isCanceled():
            for prod_name, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths,
                        product_name=prod_name,
                        category="Surface_Temperature",
                        output_root=custom_out,
                        strategy=MosaicStrategy.HIGHEST_QUALITY,
                        aoi_geometry=aoi_geom,
                        aoi_crs=aoi_crs,
                    )
                    mosaic_path = mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path
                    all_output_rasters.append(mosaic_path)
                    feedback.pushInfo(f"Mosaic Generated: {Path(mosaic_path).name}")

        return {
            self.OUTPUT_FOLDER: str(custom_out),
            "OUTPUT_RASTERS": all_output_rasters,
        }

    def createInstance(self):
        return SurfaceTemperatureAlgorithm()
