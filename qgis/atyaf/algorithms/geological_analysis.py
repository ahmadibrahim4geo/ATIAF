# -*- coding: utf-8 -*-
"""QGIS Processing Algorithm: Geological Analysis (التحليل الجيولوجي ونطاقات التحول)."""

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
from atyaf_core.geology import GEOLOGICAL_CATALOG, GeologicalAnalysisEngine
from atyaf_core.mosaic import MosaicStrategy, QualityMosaicEngine


class GeologicalAnalysisAlgorithm(QgsProcessingAlgorithm):
    """Tool 05: Geological Analysis & Mineral Alteration for QGIS."""

    INPUT_FOLDER = "INPUT_FOLDER"
    APPLY_QA = "APPLY_QA"
    ENABLE_MOSAIC = "ENABLE_MOSAIC"
    INDICES = "INDICES"
    AOI = "AOI"
    CRS = "CRS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"

    def name(self):
        return "geological_analysis"

    def displayName(self):
        return "05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني"

    def group(self):
        return "Geology"

    def groupId(self):
        return "geology"

    def shortHelpString(self):
        return (
            "Calculates diagnostic mineral alteration ratios (Iron Oxide, Ferric Iron, Ferrous Iron, "
            "Clay Alteration, Gossan, ASTER QI/CI/MI) with sensor capability gating and ASTER post-April 2008 SWIR cutoff enforcement.\n\n"
            "أطياف: التحليلات الجيولوجية ونطاقات التحول المعدني مع فرض قيود التدهور التاريخي لمستشعر ASTER."
        )

    def initAlgorithm(self, config=None):
        if not QgsProcessing:
            return

        self.addParameter(QgsProcessingParameterFile(self.INPUT_FOLDER, "Imagery Input Folder | مجلد المرئية", behavior=QgsProcessingParameterFile.Folder))
        self.addParameter(QgsProcessingParameterBoolean(self.APPLY_QA, "Apply Quality Mask | تطبيق أقنعة الجودة", defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.ENABLE_MOSAIC, "Mosaic Multiple Scenes | دمج المشاهد (موزاييك)", defaultValue=False))

        self.index_keys = list(GEOLOGICAL_CATALOG.keys())
        options = [f"{k} — {GEOLOGICAL_CATALOG[k].name_en} ({GEOLOGICAL_CATALOG[k].name_ar})" for k in self.index_keys]
        self.addParameter(QgsProcessingParameterEnum(self.INDICES, "Geological Indices Selection | اختيار المؤشرات الجيولوجية", options=options, allowMultiple=True, defaultValue=[0]))

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
        selected_enum_indices = self.parameterAsEnums(parameters, self.INDICES, context)
        selected_ids = [self.index_keys[i] for i in selected_enum_indices if i < len(self.index_keys)]

        custom_out_val = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        custom_out = Path(custom_out_val).resolve() if custom_out_val else in_folder

        qgs_crs = self.parameterAsCrs(parameters, self.CRS, context)
        if qgs_crs and qgs_crs.isValid() and qgs_crs.isGeographic():
            raise QgsProcessingException("Invalid CRS: ATIAF requires projected metre CRS (Decision D-007).")

        feedback.pushInfo(f"[Notice] {GeologicalAnalysisEngine.SCIENTIFIC_DISCLAIMER}")

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            raise QgsProcessingException(f"No recognized satellite scenes found in: {in_folder}")

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
            res = GeologicalAnalysisEngine.run_geological_analysis(
                scene=scene, selected_index_ids=selected_ids, custom_destination=custom_out,
                aoi_geometry=aoi_geom, aoi_crs=aoi_crs, apply_qa_mask=apply_qa
            )
            for p in res["executed_products"]:
                t_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(t_path)
                product_scene_map[p["product_name"]].append((scene, Path(t_path)))
                feedback.pushInfo(f"Generated: {Path(t_path).name}")

            for sk in res["skipped_indices"]:
                feedback.pushInfo(f"Skipped {sk['id']}: {sk['reason']}")

        if enable_mosaic and len(scan_res.scenes) > 1 and not feedback.isCanceled():
            for prod_name, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths, product_name=prod_name, category="Geological_Analysis", output_root=custom_out
                    )
                    mosaic_path = mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path
                    all_output_rasters.append(mosaic_path)
                    feedback.pushInfo(f"Mosaic Generated: {Path(mosaic_path).name}")

        return {
            self.OUTPUT_FOLDER: str(custom_out),
            "OUTPUT_RASTERS": all_output_rasters,
        }

    def createInstance(self):
        return GeologicalAnalysisAlgorithm()
