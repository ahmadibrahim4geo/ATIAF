# -*- coding: utf-8 -*-
"""QGIS Processing Algorithm: Temporal Analysis & Change Detection (التحليل الزمني وتغير الغطاء)."""

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
from atyaf_core.indices import SpectralIndicesEngine
from atyaf_core.temperature import SurfaceTemperatureEngine
from atyaf_core.temporal import ChangeDetectionEngine


class TemporalChangeAlgorithm(QgsProcessingAlgorithm):
    """Tool 06: Temporal Analysis & Change Detection for QGIS."""

    T1_FOLDER = "T1_FOLDER"
    T2_FOLDER = "T2_FOLDER"
    APPLY_QA = "APPLY_QA"
    METRIC = "METRIC"
    CALC_REL = "CALC_REL"
    CLASSIFY_SEV = "CLASSIFY_SEV"
    AOI = "AOI"
    CRS = "CRS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"

    def name(self):
        return "temporal_change"

    def displayName(self):
        return "06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي"

    def group(self):
        return "Temporal"

    def groupId(self):
        return "temporal"

    def shortHelpString(self):
        return (
            "Calculates multi-temporal differences (dNDVI, dNBR Burn Severity, dNDWI, dLST) between "
            "baseline (T1) and target (T2) satellite scenes with automated grid alignment and classification.\n\n"
            "أطياف: التحليل الزمني وتغيرات الغطاء الأرضي وشدة حرائق الغابات."
        )

    def initAlgorithm(self, config=None):
        if not QgsProcessing:
            return

        self.addParameter(QgsProcessingParameterFile(self.T1_FOLDER, "Baseline Scene Folder (Time 1) | مجلد فترة الأساس", behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterFile(self.T2_FOLDER, "Target Scene Folder (Time 2) | مجلد الفترة اللاحقة", behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_QA, "Apply Quality Mask | تطبيق أقنعة الجودة", defaultValue=True))

        self.metrics = [
            "NDVI (Vegetation Phenology & Deforestation)",
            "NBR (Burn Severity)",
            "NDWI (Water / Moisture Dynamics)",
            "LST (Thermal Difference)",
        ]
        self.addParameter(QgsProcessingParameterEnum(self.METRIC, "Change Metric Selection | مقياس التغير", options=self.metrics, defaultValue=0))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_REL, "Calculate Relative Percentage Change (%) | حساب نسبة التغير", defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.CLASSIFY_SEV, "Generate Thematic Severity Classification | تصنيف الفئات والحرائق", defaultValue=True))

        self.addParameter(QgsProcessingParameterFeatureSource(self.AOI, "Study Area AOI Polygon (Optional) | منطقة الدراسة", types=[QgsProcessing.TypeVectorPolygon], optional=True))
        self.addParameter(QgsProcessingParameterCrs(self.CRS, "Output Projected Coordinate System (Metres) | نظام الإحداثيات المسقط", optional=True))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_FOLDER, "Output Folder (Last Parameter) | مجلد حفظ النتائج", optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        t1_val = self.parameterAsString(parameters, self.T1_FOLDER, context)
        t2_val = self.parameterAsString(parameters, self.T2_FOLDER, context)
        if not t1_val or not t2_val:
            raise QgsProcessingException("Both Time 1 and Time 2 folders are required.")

        t1_path = Path(t1_val).resolve()
        t2_path = Path(t2_val).resolve()
        if not t1_path.is_dir() or not t2_path.is_dir():
            raise QgsProcessingException("Invalid directory paths for T1 or T2.")

        apply_qa = self.parameterAsBool(parameters, self.APPLY_QA, context)
        metric_idx = self.parameterAsEnum(parameters, self.METRIC, context)
        metric_code = ["NDVI", "NBR", "NDWI", "LST"][metric_idx]
        calc_rel = self.parameterAsBool(parameters, self.CALC_REL, context)
        classify_sev = self.parameterAsBool(parameters, self.CLASSIFY_SEV, context)

        custom_out_val = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        custom_out = Path(custom_out_val).resolve() if custom_out_val else t1_path

        qgs_crs = self.parameterAsCrs(parameters, self.CRS, context)
        if qgs_crs and qgs_crs.isValid() and qgs_crs.isGeographic():
            raise QgsProcessingException("Invalid CRS: ATIAF requires projected metre CRS (Decision D-007).")

        t1_scan = SceneScanner.scan(t1_path)
        t2_scan = SceneScanner.scan(t2_path)
        if not t1_scan.scenes or not t2_scan.scenes:
            raise QgsProcessingException("Valid satellite scenes required in both folders.")

        t1_scene, t2_scene = t1_scan.scenes[0], t2_scan.scenes[0]

        if metric_code == "LST":
            res_t1 = SurfaceTemperatureEngine.run_surface_temperature(scene=t1_scene, method="Official_L2_ST", output_unit="Celsius", custom_destination=custom_out, apply_qa_mask=apply_qa)
            res_t2 = SurfaceTemperatureEngine.run_surface_temperature(scene=t2_scene, method="Official_L2_ST", output_unit="Celsius", custom_destination=custom_out, apply_qa_mask=apply_qa)
        else:
            res_t1 = SpectralIndicesEngine.run_scene_indices(scene=t1_scene, selected_index_ids=[metric_code], custom_destination=custom_out, apply_qa_mask=apply_qa)
            res_t2 = SpectralIndicesEngine.run_scene_indices(scene=t2_scene, selected_index_ids=[metric_code], custom_destination=custom_out, apply_qa_mask=apply_qa)

        t1_raster = Path(res_t1["executed_products"][0]["full_path"])
        t2_raster = Path(res_t2["executed_products"][0]["full_path"])

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

        change_res = ChangeDetectionEngine.run_change_detection(
            t1_raster_path=t1_raster, t2_raster_path=t2_raster,
            t1_scene_id=t1_scene.metadata.scene_id, t2_scene_id=t2_scene.metadata.scene_id,
            t1_date=t1_scene.metadata.acquisition_date, t2_date=t2_scene.metadata.acquisition_date,
            metric_name=metric_code, output_root=custom_out,
            calc_relative=calc_rel, classify_severity=classify_sev,
            aoi_geometry=aoi_geom, aoi_crs=aoi_crs,
        )

        all_outputs = []
        for p in change_res["executed_products"]:
            t_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
            all_outputs.append(t_path)
            feedback.pushInfo(f"Generated: {Path(t_path).name}")

        return {
            self.OUTPUT_FOLDER: str(custom_out),
            "OUTPUT_RASTERS": all_outputs,
        }

    def createInstance(self):
        return TemporalChangeAlgorithm()
