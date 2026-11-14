# -*- coding: utf-8 -*-
"""ATIAF — Advanced Thematic Imagery Analysis Framework (أطياف)
Native ArcGIS Pro Python Toolbox (.pyt)

Author: ATIAF Open Source Geospatial Project
License: MIT
"""

import os
from pathlib import Path
import sys

# Ensure atyaf_core is importable from toolbox location
TOOLBOX_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path(".").resolve()
PROJECT_ROOT = TOOLBOX_DIR.parent if TOOLBOX_DIR.name == "arcgis_pro" else TOOLBOX_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import arcpy
except ImportError:
    arcpy = None

from atyaf_core.discovery import SceneScanner
from atyaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
from atyaf_core.raster import CRSManager


class Toolbox(object):
    def __init__(self):
        self.label = "ATIAF - Thematic Imagery Analysis Framework"
        self.alias = "atyaf"
        self.description = (
            "Bilingual scientific satellite imagery analysis framework for ArcGIS Pro. "
            "أطياف: منظومة التحليل العلمي للمرئيات الفضائية"
        )
        self.tools = [SpectralIndicesTool]


class SpectralIndicesTool(object):
    """Tool 01: Spectral Indices (المؤشرات الطيفية)
    Computes optical spectral indices (vegetation, water, soil, urban, burn, snow)
    with automated preprocessing, quality masking, optional mosaic, AOI polygon clipping,
    and reproducible scientific manifests.
    """

    def __init__(self):
        self.label = "01. Spectral Indices | المؤشرات الطيفية"
        self.description = (
            "Calculates validated optical spectral indices (NDVI, NDWI, MNDWI, NDBI, NBR, NDSI, SAVI, EVI, BSI) "
            "with sensor auto-detection, quality masking, true polygon clipping, and run manifests."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Constructs the 8 canonical parameters in the exact standard order specified in Section 3."""
        # 1. Sensor / Product (Auto-detect or manual selector)
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

        # 2. Imagery Input (single scene folder or parent folder)
        param_input = arcpy.Parameter(
            displayName="Imagery Input Folder | مجلد المرئية المفكوك أو المجلد الأب",
            name="input_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        ) if arcpy else None

        # 3. Preprocessing (QA Masking)
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

        # 5. Tool-specific calculations (Spectral indices multi-selection)
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

        # 7. Output options (LAST parameter: defaulted to input folder)
        param_output_folder = arcpy.Parameter(
            displayName="Output Folder (Last Parameter) | مجلد حفظ النتائج (آخر خيار)",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Optional",
            direction="Input",
        ) if arcpy else None

        # Add Results to Map (optional sub-option)
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
        """Tool runs with all ArcGIS Pro license tiers; Spatial Analyst is checked when needed."""
        return True

    def updateParameters(self, parameters):
        """Dynamically updates defaults and filters based on input folder."""
        if not arcpy:
            return

        param_sensor, param_input, _, _, param_indices, _, param_crs, param_output_folder, _ = parameters

        # Update default output folder to match input folder if not manually set
        if param_input and param_input.value:
            in_val = str(param_input.value)
            if param_output_folder and (not param_output_folder.value or not param_output_folder.altered):
                param_output_folder.value = in_val

            # Auto-detect sensor and filter available indices if directory exists
            in_path = Path(in_val)
            if in_path.is_dir():
                try:
                    scan_res = SceneScanner.scan(in_path)
                    if scan_res.scenes:
                        first_scene = scan_res.scenes[0]
                        # Filter available indices to those supported by the detected bands
                        supported = SpectralIndicesEngine.get_supported_indices_for_scene(first_scene)
                        if supported and param_indices:
                            allowed = [f"{s.id} — {s.name_en} ({s.name_ar})" for s in supported]
                            param_indices.filter.list = allowed
                except Exception:
                    pass

    def updateMessages(self, parameters):
        """Validates parameter constraints, enforcing Decision D-007 (projected metre CRS)."""
        if not arcpy:
            return

        param_sensor, param_input, _, _, _, _, param_crs, param_output_folder, _ = parameters

        # 1. Enforce Decision D-007: Reject geographic degree coordinate systems
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

        # 2. Validate input folder
        if param_input and param_input.value:
            in_path = Path(str(param_input.value))
            if not in_path.exists():
                param_input.setErrorMessage(f"Input path does not exist: {in_path}")
            elif not in_path.is_dir():
                param_input.setErrorMessage(f"Input path is not a directory: {in_path}")

    def execute(self, parameters, messages):
        """Executes the spectral indices analysis, logging scientific progress."""
        if not arcpy:
            raise RuntimeError("ArcPy runtime is required to execute in ArcGIS Pro.")

        param_sensor, param_input, param_qa_mask, param_mosaic, param_indices, param_aoi, param_crs, param_output_folder, param_add_to_map = parameters

        in_folder = Path(str(param_input.value)).resolve()
        custom_out = Path(str(param_output_folder.value)).resolve() if param_output_folder.value else None
        apply_qa = bool(param_qa_mask.value) if param_qa_mask else True
        add_map = bool(param_add_to_map.value) if param_add_to_map else False

        # Parse selected index IDs (e.g. 'NDVI' from 'NDVI — Normalized...')
        raw_indices = param_indices.valueAsText.split(";") if param_indices.valueAsText else []
        selected_ids = [s.strip("'\"").split(" — ")[0].strip() for s in raw_indices if s.strip()]

        arcpy.AddMessage("----------------------------------------------------------------------")
        arcpy.AddMessage("ATIAF — Advanced Thematic Imagery Analysis Framework (أطياف)")
        arcpy.AddMessage("Tool 01: Spectral Indices | المؤشرات الطيفية")
        arcpy.AddMessage("----------------------------------------------------------------------")
        arcpy.AddMessage(f"Input Directory: {in_folder}")
        arcpy.AddMessage(f"Selected Indices: {', '.join(selected_ids)}")

        # Discover scenes
        scan_res = SceneScanner.scan(in_folder)
        if not scan_res.scenes:
            arcpy.AddError(f"No recognized satellite products found in: {in_folder}")
            return

        arcpy.AddMessage(f"Discovered {len(scan_res.scenes)} scene(s).")

        # Handle AOI geometry if provided
        aoi_geom = None
        aoi_crs = None
        if param_aoi and param_aoi.value:
            try:
                # Extract Shapely geometry from feature set
                desc = arcpy.Describe(param_aoi.value)
                aoi_crs = desc.spatialReference.name
                features = []
                with arcpy.da.SearchCursor(param_aoi.value, ["SHAPE@"]) as cursor:
                    for row in cursor:
                        features.append(row[0])
                if features:
                    # Union all feature geometries
                    union_geom = features[0]
                    for f in features[1:]:
                        union_geom = union_geom.union(f)
                    from shapely import wkt
                    aoi_geom = wkt.loads(union_geom.WKT)
                    arcpy.AddMessage("AOI polygon boundary loaded successfully.")
            except Exception as e:
                arcpy.AddWarning(f"Could not parse AOI geometry: {e}. Processing full extent.")

        # Execute for each scene
        all_output_rasters = []
        for i, scene in enumerate(scan_res.scenes, start=1):
            arcpy.AddMessage(f"\n[{i}/{len(scan_res.scenes)}] Processing: {scene.metadata.scene_id}")
            arcpy.AddMessage(f"  Platform: {scene.metadata.platform}, Sensor: {scene.metadata.instrument}")

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
                arcpy.AddMessage(f"  -> Generated: {Path(target_path).name} (Valid pixels: {p['valid_pixels']})")

            for sk in res["skipped_indices"]:
                arcpy.AddWarning(f"  -> Skipped {sk['id']}: {sk['reason']}")

            arcpy.AddMessage(f"  Manifest written to: {res['run_dir']}")

        # Optionally add results to active map sequentially
        if add_map and all_output_rasters:
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                active_map = aprx.activeMap
                if active_map:
                    arcpy.AddMessage("\nAdding calculated products to active map...")
                    for raster_path in all_output_rasters:
                        if Path(raster_path).exists():
                            active_map.addDataFromPath(raster_path)
                            arcpy.AddMessage(f"  Added: {Path(raster_path).name}")
            except Exception as e:
                arcpy.AddWarning(f"Could not add layers to map: {e}")

        arcpy.AddMessage("\nATIAF processing completed successfully.")
