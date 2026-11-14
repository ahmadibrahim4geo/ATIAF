# -*- coding: utf-8 -*-
"""QGIS Processing Algorithm: Thermal & Urban Analysis (التحليل الحراري والحضري)."""

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
        QgsProcessingParameterFeatureSource,
        QgsProcessingParameterFile,
        QgsProcessingParameterFolderDestination,
    )
except ImportError:
    QgsProcessingAlgorithm = object
    QgsProcessing = None

from atyaf_core.discovery import SceneScanner
from atyaf_core.urban import ThermalUrbanEngine


class ThermalUrbanAlgorithm(QgsProcessingAlgorithm):
    """Tool 03: Thermal & Urban Analysis (التحليل الحراري والحضري والجزر الحرارية) for QGIS."""

    INPUT_FOLDER = "INPUT_FOLDER"
    APPLY_QA = "APPLY_QA"
    AOI = "AOI"
    CRS = "CRS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"

    def name(self):
        return "thermal_urban"

    def displayName(self):
        return "03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية"

    def group(self):
        return "Thermal"

    def groupId(self):
        return "thermal"

    def shortHelpString(self):
        return (
            "Calculates Urban Thermal Field Variance Index (UTFVI), Thermal Hotspots (z >= 2.0 sigma), "
            "and thermal comfort classifications from thermal satellite products.\n\n"
            "أطياف: تحليل الجزر الحرارية الحضرية (UTFVI) والبؤر الحرارية الشديدة."
        )

    def initAlgorithm(self, config=None):
        if not QgsProcessing:
            return

        self.addParameter(QgsProcessingParameterFile(self.INPUT_FOLDER, "Imagery Input Folder | مجلد المرئية", behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_QA, "Apply Quality Mask | تطبيق أقنعة الجودة", defaultValue=True))
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
        custom_out_val = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        custom_out = Path(custom_out_val).resolve() if custom_out_val else in_folder

        qgs_crs = self.parameterAsCrs(parameters, self.CRS, context)
        if qgs_crs and qgs_crs.isValid() and qgs_crs.isGeographic():
            raise QgsProcessingException("Invalid CRS: ATIAF requires projected metre CRS (Decision D-007).")

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            raise QgsProcessingException(f"No recognized satellite scenes found in: {in_folder}")

        for sc in scan_res.scenes:
            if not sc.has_thermal():
                raise QgsProcessingException(f"Scene '{sc.metadata.scene_id}' lacks thermal bands.")

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
        for scene in scan_res.scenes:
            if feedback.isCanceled():
                break
            res = ThermalUrbanEngine.run_thermal_urban_analysis(
                scene=scene, custom_destination=custom_out, aoi_geometry=aoi_geom, aoi_crs=aoi_crs, apply_qa_mask=apply_qa
            )
            for p in res["executed_products"]:
                t_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(t_path)
                feedback.pushInfo(f"Generated: {Path(t_path).name}")

        return {
            self.OUTPUT_FOLDER: str(custom_out),
            "OUTPUT_RASTERS": all_output_rasters,
        }

    def createInstance(self):
        return ThermalUrbanAlgorithm()
