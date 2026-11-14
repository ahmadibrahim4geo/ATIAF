# -*- coding: utf-8 -*-
"""QGIS Processing Algorithm: Spectral Indices (المؤشرات الطيفية)."""

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
from atyaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
from atyaf_core.mosaic import MosaicStrategy, QualityMosaicEngine
from atyaf_core.raster import CRSManager


class SpectralIndicesAlgorithm(QgsProcessingAlgorithm):
    """Tool 01: Spectral Indices (المؤشرات الطيفية) for QGIS."""

    INPUT_FOLDER = "INPUT_FOLDER"
    APPLY_QA = "APPLY_QA"
    ENABLE_MOSAIC = "ENABLE_MOSAIC"
    INDICES = "INDICES"
    AOI = "AOI"
    CRS = "CRS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"

    def name(self):
        return "spectral_indices"

    def displayName(self):
        return "01. Spectral Indices | المؤشرات الطيفية"

    def group(self):
        return "Indices"

    def groupId(self):
        return "indices"

    def shortHelpString(self):
        return (
            "Calculates validated optical spectral indices (NDVI, NDWI, MNDWI, NDMI, MSAVI, OSAVI, "
            "VARI, GLI, TCB, TCG, TCW, NDBI, NBR, NDSI, SAVI, EVI, BSI) from satellite imagery "
            "with sensor auto-detection, quality masking, true polygon clipping, and run manifests.\n\n"
            "أطياف: حساب المؤشرات الطيفية البصرية العلمية مع التحقق التلقائي من الأقمار والمستشعرات."
        )

    def initAlgorithm(self, config=None):
        if not QgsProcessing:
            return

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                "Imagery Input Folder | مجلد المرئية المفكوك أو المجلد الأب",
                behavior=QgsProcessingParameterFile.Folder,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.APPLY_QA,
                "Apply Quality / Cloud / Shadow Mask | تطبيق أقنعة الجودة والسحب والظلال",
                defaultValue=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ENABLE_MOSAIC,
                "Mosaic Multiple Scenes | دمج المشاهد المتعددة (موزاييك)",
                defaultValue=False,
            )
        )

        self.index_keys = list(INDEX_CATALOG.keys())
        index_options = [f"{k} — {INDEX_CATALOG[k].name_en} ({INDEX_CATALOG[k].name_ar})" for k in self.index_keys]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INDICES,
                "Spectral Indices Selection | اختيار المؤشرات الطيفية",
                options=index_options,
                allowMultiple=True,
                defaultValue=[0],  # Default to NDVI
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.AOI,
                "Study Area AOI Polygon (Optional) | منطقة الدراسة (اختياري)",
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                "Output Projected Coordinate System (Metres) | نظام الإحداثيات المسقط بالمتر",
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                "Output Folder (Last Parameter) | مجلد حفظ النتائج (آخر خيار)",
                optional=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        in_folder_val = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        if not in_folder_val:
            raise QgsProcessingException("Input imagery folder is required.")
        in_folder = Path(in_folder_val).resolve()
        if not in_folder.is_dir():
            raise QgsProcessingException(f"Input path is not a valid directory: {in_folder}")

        apply_qa = self.parameterAsBool(parameters, self.APPLY_QA, context)
        enable_mosaic = self.parameterAsBool(parameters, self.ENABLE_MOSAIC, context)
        selected_enum_indices = self.parameterAsEnums(parameters, self.INDICES, context)
        selected_ids = [self.index_keys[i] for i in selected_enum_indices if i < len(self.index_keys)]

        custom_out_val = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        custom_out = Path(custom_out_val).resolve() if custom_out_val else in_folder

        # Decision D-007: Enforce projected metre CRS
        qgs_crs = self.parameterAsCrs(parameters, self.CRS, context)
        if qgs_crs and qgs_crs.isValid():
            crs_auth = qgs_crs.authid()
            if qgs_crs.isGeographic():
                raise QgsProcessingException(
                    f"Invalid CRS '{crs_auth}': ATIAF strictly rejects unprojected geographic degrees (EPSG:4326). "
                    "A projected coordinate reference system with linear units in metres is required (Decision D-007)."
                )

        feedback.pushInfo("----------------------------------------------------------------------")
        feedback.pushInfo("ATIAF QGIS Processing — Tool 01: Spectral Indices (أطياف)")
        feedback.pushInfo(f"Input Directory: {in_folder}")
        feedback.pushInfo(f"Selected Indices: {', '.join(selected_ids)}")

        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            raise QgsProcessingException(f"No recognized satellite products discovered in: {in_folder}")

        feedback.pushInfo(f"Discovered {len(scan_res.scenes)} scene(s).")

        # AOI geometry
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
                feedback.pushInfo("Loaded study area AOI polygon geometry.")

        all_output_rasters = []
        product_scene_map = defaultdict(list)

        total_scenes = len(scan_res.scenes)
        for i, scene in enumerate(scan_res.scenes, start=1):
            if feedback.isCanceled():
                break

            feedback.setProgress(int((i - 1) / total_scenes * 100))
            feedback.pushInfo(f"[{i}/{total_scenes}] Processing: {scene.metadata.scene_id}")

            res = SpectralIndicesEngine.run_scene_indices(
                scene=scene,
                selected_index_ids=selected_ids,
                custom_destination=custom_out,
                aoi_geometry=aoi_geom,
                aoi_crs=aoi_crs,
                apply_qa_mask=apply_qa,
            )

            for p in res["executed_products"]:
                t_path = p["clipped_path"] if p["clipped_path"] else p["full_path"]
                all_output_rasters.append(t_path)
                product_scene_map[p["acronym"]].append((scene, Path(t_path)))
                feedback.pushInfo(f"  -> Generated: {Path(t_path).name}")

            for sk in res["skipped_indices"]:
                feedback.pushInfo(f"  -> Skipped {sk['id']}: {sk['reason']}")

        # Multi-Scene Mosaic Blending
        if enable_mosaic and len(scan_res.scenes) > 1 and not feedback.isCanceled():
            feedback.pushInfo("\nInitiating Multi-Scene Quality-Aware Mosaic Blending...")
            for idx_id, scene_paths in product_scene_map.items():
                if len(scene_paths) > 1:
                    mos_res = QualityMosaicEngine.run_mosaic(
                        scene_products=scene_paths,
                        product_name=idx_id,
                        category="Spectral_Indices",
                        output_root=custom_out,
                        strategy=MosaicStrategy.HIGHEST_QUALITY,
                        aoi_geometry=aoi_geom,
                        aoi_crs=aoi_crs,
                    )
                    mosaic_path = mos_res.clipped_path if mos_res.clipped_path else mos_res.full_path
                    all_output_rasters.append(mosaic_path)
                    feedback.pushInfo(f"  -> Mosaic Generated: {Path(mosaic_path).name}")

        feedback.setProgress(100)
        feedback.pushInfo("ATIAF Spectral Indices processing completed successfully.")

        return {
            self.OUTPUT_FOLDER: str(custom_out),
            "OUTPUT_RASTERS": all_output_rasters,
        }

    def createInstance(self):
        return SpectralIndicesAlgorithm()
