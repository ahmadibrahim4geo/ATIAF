"""Thermal & Urban Analysis execution engine (Tool 03)."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import rasterio

from atyaf_core.discovery.models import SceneInfo
from atyaf_core.raster.clip import PolygonClipEngine
from atyaf_core.raster.workspace import WorkspaceManager
from atyaf_core.temperature.engine import SurfaceTemperatureEngine


class ThermalUrbanEngine:
    """Calculates Urban Thermal Field Variance Index (UTFVI), Thermal Hotspots,
    and Surface Urban Heat Island (SUHI) metrics.
    """

    UTFVI_CLASSES = [
        {"class_id": 1, "name_en": "None", "name_ar": "لا توجد جزيرة حرارية", "min": -10.0, "max": 0.0},
        {"class_id": 2, "name_en": "Weak", "name_ar": "ضعيفة", "min": 0.0, "max": 0.005},
        {"class_id": 3, "name_en": "Middle", "name_ar": "متوسطة", "min": 0.005, "max": 0.010},
        {"class_id": 4, "name_en": "Strong", "name_ar": "قوية", "min": 0.010, "max": 0.015},
        {"class_id": 5, "name_en": "Stronger", "name_ar": "شديدة", "min": 0.015, "max": 0.020},
        {"class_id": 6, "name_en": "Strongest", "name_ar": "شديدة جداً", "min": 0.020, "max": 10.0},
    ]

    @classmethod
    def calc_utfvi(cls, lst_kelvin: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates UTFVI = (LST - mean(LST)) / mean(LST) in Kelvin, and classifies it (1 to 6)."""
        valid_mask = ~np.isnan(lst_kelvin) & (lst_kelvin > 0)
        vals = lst_kelvin[valid_mask]

        utfvi_arr = np.full_like(lst_kelvin, np.nan, dtype=np.float32)
        classified_arr = np.zeros(lst_kelvin.shape, dtype=np.uint8)

        if len(vals) == 0:
            return utfvi_arr, classified_arr

        mean_lst = float(np.mean(vals))
        if mean_lst <= 0:
            return utfvi_arr, classified_arr

        utfvi_arr[valid_mask] = ((lst_kelvin[valid_mask] - mean_lst) / mean_lst).astype(np.float32)

        for c in cls.UTFVI_CLASSES:
            c_mask = valid_mask & (utfvi_arr >= c["min"]) & (utfvi_arr < c["max"])
            classified_arr[c_mask] = c["class_id"]

        return utfvi_arr, classified_arr

    @classmethod
    def calc_thermal_hotspots(cls, lst: np.ndarray, z_threshold: float = 2.0) -> np.ndarray:
        """Flags pixels where (LST - mean) / std >= z_threshold (default 2.0 sigma)."""
        valid_mask = ~np.isnan(lst)
        vals = lst[valid_mask]
        hotspots = np.zeros(lst.shape, dtype=np.uint8)
        if len(vals) == 0:
            return hotspots

        mu = float(np.mean(vals))
        sigma = float(np.std(vals))
        if sigma <= 0:
            return hotspots

        z_scores = (lst - mu) / sigma
        hotspots[valid_mask & (z_scores >= z_threshold)] = 1
        return hotspots

    @classmethod
    def run_thermal_urban_analysis(
        cls,
        scene: SceneInfo,
        custom_destination: Optional[Path] = None,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
        apply_qa_mask: bool = True,
    ) -> Dict[str, Any]:
        """Runs the thermal and urban analysis suite on an identified satellite scene."""
        if not scene.has_thermal():
            raise ValueError(
                f"Scene '{scene.metadata.scene_id}' lacks thermal bands. "
                "Urban Heat Island analysis requires thermal infrared measurements."
            )

        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            scene_path=scene.scene_path,
            custom_destination=custom_destination,
        )

        urban_results_dir = results_dir / "Thermal_Analysis"
        urban_results_dir.mkdir(parents=True, exist_ok=True)

        # 1. Compute LST in Kelvin first
        lst_res = SurfaceTemperatureEngine.run_surface_temperature(
            scene=scene,
            method="Official_L2_ST",
            output_unit="Kelvin",
            custom_destination=custom_destination,
            apply_qa_mask=apply_qa_mask,
        )
        lst_k_path = Path(lst_res["executed_products"][0]["full_path"])

        with rasterio.open(lst_k_path) as ds:
            profile = ds.meta.copy()
            lst_k = ds.read(1).astype(np.float32)
            if ds.nodata is not None:
                lst_k[lst_k == ds.nodata] = np.nan

        # 2. Compute UTFVI & classification
        utfvi, utfvi_classes = cls.calc_utfvi(lst_k)

        # 3. Compute Hotspots
        hotspots = cls.calc_thermal_hotspots(lst_k, z_threshold=2.0)

        # 4. Save Products
        executed_products = []

        # A. Continuous UTFVI
        utfvi_file = urban_results_dir / f"UTFVI_{scene.metadata.scene_id}_FULL.tif"
        out_prof = profile.copy()
        out_prof.update({"dtype": "float32", "nodata": -9999.0})
        utfvi_nodata = np.where(np.isnan(utfvi), -9999.0, utfvi).astype(np.float32)
        with rasterio.open(utfvi_file, "w", **out_prof) as dst:
            dst.write(utfvi_nodata, 1)

        utfvi_clip = None
        if aoi_geometry is not None:
            utfvi_clip_file = urban_results_dir / f"UTFVI_{scene.metadata.scene_id}_AOI_CLIP.tif"
            PolygonClipEngine.clip_raster_file(
                src_raster_path=utfvi_file, dst_raster_path=utfvi_clip_file, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs, crop=True, nodata=-9999.0
            )
            utfvi_clip = str(utfvi_clip_file)

        valid_utfvi = utfvi[~np.isnan(utfvi)]
        stats_utfvi = {
            "min": float(np.min(valid_utfvi)) if len(valid_utfvi) > 0 else 0.0,
            "max": float(np.max(valid_utfvi)) if len(valid_utfvi) > 0 else 0.0,
            "mean": float(np.mean(valid_utfvi)) if len(valid_utfvi) > 0 else 0.0,
            "std": float(np.std(valid_utfvi)) if len(valid_utfvi) > 0 else 0.0,
        }

        executed_products.append({
            "product_name": "UTFVI",
            "full_path": str(utfvi_file),
            "clipped_path": utfvi_clip,
            "statistics": stats_utfvi,
            "valid_pixels": int(len(valid_utfvi)),
        })

        # B. UTFVI Classification
        class_file = urban_results_dir / f"UTFVI_CLASSIFICATION_{scene.metadata.scene_id}_FULL.tif"
        class_prof = profile.copy()
        class_prof.update({"dtype": "uint8", "nodata": 0})
        with rasterio.open(class_file, "w", **class_prof) as dst:
            dst.write(utfvi_classes, 1)

        class_clip = None
        if aoi_geometry is not None:
            class_clip_file = urban_results_dir / f"UTFVI_CLASSIFICATION_{scene.metadata.scene_id}_AOI_CLIP.tif"
            PolygonClipEngine.clip_raster_file(
                src_raster_path=class_file, dst_raster_path=class_clip_file, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs, crop=True, nodata=0
            )
            class_clip = str(class_clip_file)

        executed_products.append({
            "product_name": "UTFVI_Classification",
            "classes": cls.UTFVI_CLASSES,
            "full_path": str(class_file),
            "clipped_path": class_clip,
            "valid_pixels": int(np.count_nonzero(utfvi_classes > 0)),
        })

        # C. Hotspots
        hotspot_file = urban_results_dir / f"THERMAL_HOTSPOTS_{scene.metadata.scene_id}_FULL.tif"
        hotspot_prof = profile.copy()
        hotspot_prof.update({"dtype": "uint8", "nodata": 0})
        with rasterio.open(hotspot_file, "w", **hotspot_prof) as dst:
            dst.write(hotspots, 1)

        hotspot_clip = None
        if aoi_geometry is not None:
            hotspot_clip_file = urban_results_dir / f"THERMAL_HOTSPOTS_{scene.metadata.scene_id}_AOI_CLIP.tif"
            PolygonClipEngine.clip_raster_file(
                src_raster_path=hotspot_file, dst_raster_path=hotspot_clip_file, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs, crop=True, nodata=0
            )
            hotspot_clip = str(hotspot_clip_file)

        executed_products.append({
            "product_name": "Thermal_Hotspots",
            "full_path": str(hotspot_file),
            "clipped_path": hotspot_clip,
            "valid_pixels": int(np.count_nonzero(hotspots > 0)),
        })

        # Run Manifest
        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=scene.metadata.scene_id,
            tool_name="03_Thermal_Urban_Analysis",
            parameters={
                "apply_qa_mask": apply_qa_mask,
                "has_aoi": aoi_geometry is not None,
            },
            output_products=executed_products,
            qa_summary={"executed_products_count": len(executed_products)},
        )

        return {
            "scene_id": scene.metadata.scene_id,
            "results_dir": str(urban_results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
        }
