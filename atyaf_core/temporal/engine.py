"""Temporal Analysis & Change Detection engine (Tool 06)."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

from atyaf_core.raster.clip import PolygonClipEngine
from atyaf_core.raster.workspace import WorkspaceManager


class ChangeDetectionEngine:
    """Calculates spectral and thermal differences, percentage change, and thematic
    classifications (e.g. USGS Burn Severity, standard deviation change classes) across two epochs.
    """

    USGS_BURN_SEVERITY_CLASSES = [
        {"class_id": 1, "name_en": "High Post-Fire Regrowth", "name_ar": "نمو نباتي مرتفع بعد الحريق", "min": -10.0, "max": -0.25},
        {"class_id": 2, "name_en": "Low Post-Fire Regrowth", "name_ar": "نمو نباتي منخفض بعد الحريق", "min": -0.25, "max": -0.10},
        {"class_id": 3, "name_en": "Unburned", "name_ar": "غير محترق", "min": -0.10, "max": 0.10},
        {"class_id": 4, "name_en": "Low Severity", "name_ar": "شدة احتراق منخفضة", "min": 0.10, "max": 0.27},
        {"class_id": 5, "name_en": "Moderate-Low Severity", "name_ar": "شدة احتراق متوسطة-منخفضة", "min": 0.27, "max": 0.44},
        {"class_id": 6, "name_en": "Moderate-High Severity", "name_ar": "شدة احتراق متوسطة-مرتفعة", "min": 0.44, "max": 0.66},
        {"class_id": 7, "name_en": "High Severity", "name_ar": "شدة احتراق مرتفعة", "min": 0.66, "max": 10.0},
    ]

    @classmethod
    def classify_burn_severity(cls, dnbr: np.ndarray) -> np.ndarray:
        """Classifies dNBR (Pre - Post) into USGS Burn Severity classes (1 to 7)."""
        classified = np.zeros(dnbr.shape, dtype=np.uint8)
        valid = ~np.isnan(dnbr)

        for c in cls.USGS_BURN_SEVERITY_CLASSES:
            mask = valid & (dnbr >= c["min"]) & (dnbr < c["max"])
            classified[mask] = c["class_id"]

        return classified

    @classmethod
    def classify_std_change(cls, delta: np.ndarray) -> np.ndarray:
        """Classifies continuous change into 5 statistical standard deviation classes:
        1: Significant Decrease (< -1.5 sigma)
        2: Moderate Decrease (-1.5 sigma to -0.5 sigma)
        3: Stable (-0.5 sigma to +0.5 sigma)
        4: Moderate Increase (+0.5 sigma to +1.5 sigma)
        5: Significant Increase (> +1.5 sigma)
        """
        classified = np.zeros(delta.shape, dtype=np.uint8)
        valid = ~np.isnan(delta)
        vals = delta[valid]
        if len(vals) == 0:
            return classified

        mu = float(np.mean(vals))
        sigma = float(np.std(vals))

        if sigma == 0:
            classified[valid] = 3
            return classified

        classified[valid & (delta < mu - 1.5 * sigma)] = 1
        classified[valid & (delta >= mu - 1.5 * sigma) & (delta < mu - 0.5 * sigma)] = 2
        classified[valid & (delta >= mu - 0.5 * sigma) & (delta <= mu + 0.5 * sigma)] = 3
        classified[valid & (delta > mu + 0.5 * sigma) & (delta <= mu + 1.5 * sigma)] = 4
        classified[valid & (delta > mu + 1.5 * sigma)] = 5

        return classified

    @classmethod
    def run_change_detection(
        cls,
        t1_raster_path: Path,
        t2_raster_path: Path,
        t1_scene_id: str,
        t2_scene_id: str,
        t1_date: str,
        t2_date: str,
        metric_name: str,             # e.g., 'NDVI', 'NBR', 'LST'
        output_root: Path,
        calc_relative: bool = True,
        classify_severity: bool = False,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Calculates multi-temporal differences between two aligned raster layers."""
        # 1. Output directory setup: Results/Temporal_Change/<metric_name>_T1_T2/
        change_slug = f"Delta_{metric_name}_{t1_scene_id}_to_{t2_scene_id}"
        results_dir = output_root / "Results" / "Temporal_Change" / metric_name
        results_dir.mkdir(parents=True, exist_ok=True)
        reports_dir = output_root / "Reports"

        # 2. Read T1 as reference geometry
        with rasterio.open(t1_raster_path) as ref_ds:
            ref_meta = ref_ds.meta.copy()
            ref_transform = ref_ds.transform
            ref_crs = ref_ds.crs
            height, width = ref_ds.height, ref_ds.width
            t1_arr = ref_ds.read(1).astype(np.float32)
            if ref_ds.nodata is not None:
                t1_arr[t1_arr == ref_ds.nodata] = np.nan

        # 3. Read and reproject T2 onto T1 grid
        t2_aligned = np.full((height, width), np.nan, dtype=np.float32)
        with rasterio.open(t2_raster_path) as t2_ds:
            t2_raw = t2_ds.read(1).astype(np.float32)
            if t2_ds.nodata is not None:
                t2_raw[t2_raw == t2_ds.nodata] = np.nan

            reproject(
                source=t2_raw,
                destination=t2_aligned,
                src_transform=t2_ds.transform,
                src_crs=t2_ds.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=Resampling.bilinear,
                src_nodata=np.nan,
                dst_nodata=np.nan,
            )

        # 4. Calculate Absolute Difference:
        # Standard delta is T2 - T1 (except dNBR in burn severity which is Pre - Post = T1 - T2)
        if metric_name.upper() == "NBR" and classify_severity:
            delta_arr = t1_arr - t2_aligned  # dNBR = NBR_pre - NBR_post
        else:
            delta_arr = t2_aligned - t1_arr

        # Valid mask
        valid_mask = ~np.isnan(t1_arr) & ~np.isnan(t2_aligned)
        delta_arr[~valid_mask] = np.nan

        # 5. Output products list
        executed_products: List[Dict[str, Any]] = []

        # Write Absolute Delta GeoTIFF
        delta_file = results_dir / f"{change_slug}_DIFF_FULL.tif"
        out_profile = {
            "driver": "GTiff",
            "width": width,
            "height": height,
            "count": 1,
            "dtype": "float32",
            "crs": ref_crs,
            "transform": ref_transform,
            "nodata": -9999.0,
        }
        delta_nodata = np.where(np.isnan(delta_arr), -9999.0, delta_arr).astype(np.float32)
        with rasterio.open(delta_file, "w", **out_profile) as dst:
            dst.write(delta_nodata, 1)

        delta_clipped = None
        if aoi_geometry is not None:
            delta_clip_file = results_dir / f"{change_slug}_DIFF_AOI_CLIP.tif"
            PolygonClipEngine.clip_raster_file(
                src_raster_path=delta_file,
                dst_raster_path=delta_clip_file,
                aoi_geometry=aoi_geometry,
                aoi_crs=aoi_crs,
                crop=True,
                nodata=-9999.0,
            )
            delta_clipped = str(delta_clip_file)

        delta_vals = delta_arr[valid_mask]
        delta_stats = {
            "min": float(np.min(delta_vals)) if len(delta_vals) > 0 else 0.0,
            "max": float(np.max(delta_vals)) if len(delta_vals) > 0 else 0.0,
            "mean": float(np.mean(delta_vals)) if len(delta_vals) > 0 else 0.0,
            "std": float(np.std(delta_vals)) if len(delta_vals) > 0 else 0.0,
        }

        executed_products.append({
            "product_name": f"Delta_{metric_name}",
            "type": "absolute_difference",
            "full_path": str(delta_file),
            "clipped_path": delta_clipped,
            "statistics": delta_stats,
            "valid_pixels": int(np.count_nonzero(valid_mask)),
        })

        # 6. Relative Percentage Change
        if calc_relative:
            with np.errstate(divide="ignore", invalid="ignore"):
                # (T2 - T1) / abs(T1) * 100
                denom = np.abs(t1_arr)
                rel_change = np.where(denom < 1e-4, np.nan, (delta_arr / denom) * 100.0)
            rel_change[~valid_mask] = np.nan

            rel_file = results_dir / f"{change_slug}_REL_PCT_FULL.tif"
            rel_nodata = np.where(np.isnan(rel_change), -9999.0, rel_change).astype(np.float32)
            with rasterio.open(rel_file, "w", **out_profile) as dst:
                dst.write(rel_nodata, 1)

            rel_clipped = None
            if aoi_geometry is not None:
                rel_clip_file = results_dir / f"{change_slug}_REL_PCT_AOI_CLIP.tif"
                PolygonClipEngine.clip_raster_file(
                    src_raster_path=rel_file,
                    dst_raster_path=rel_clip_file,
                    aoi_geometry=aoi_geometry,
                    aoi_crs=aoi_crs,
                    crop=True,
                    nodata=-9999.0,
                )
                rel_clipped = str(rel_clip_file)

            executed_products.append({
                "product_name": f"Relative_Change_{metric_name}",
                "type": "relative_percentage",
                "full_path": str(rel_file),
                "clipped_path": rel_clipped,
                "valid_pixels": int(np.count_nonzero(~np.isnan(rel_change))),
            })

        # 7. Burn Severity Classification (if metric is NBR)
        if metric_name.upper() == "NBR" and classify_severity:
            burn_arr = cls.classify_burn_severity(delta_arr)
            burn_file = results_dir / f"{change_slug}_BURN_SEVERITY_FULL.tif"
            burn_profile = out_profile.copy()
            burn_profile.update({"dtype": "uint8", "nodata": 0})

            with rasterio.open(burn_file, "w", **burn_profile) as dst:
                dst.write(burn_arr, 1)

            burn_clipped = None
            if aoi_geometry is not None:
                burn_clip_file = results_dir / f"{change_slug}_BURN_SEVERITY_AOI_CLIP.tif"
                PolygonClipEngine.clip_raster_file(
                    src_raster_path=burn_file,
                    dst_raster_path=burn_clip_file,
                    aoi_geometry=aoi_geometry,
                    aoi_crs=aoi_crs,
                    crop=True,
                    nodata=0,
                )
                burn_clipped = str(burn_clip_file)

            executed_products.append({
                "product_name": "Burn_Severity_Classification",
                "type": "thematic_classification",
                "classes": cls.USGS_BURN_SEVERITY_CLASSES,
                "full_path": str(burn_file),
                "clipped_path": burn_clipped,
                "valid_pixels": int(np.count_nonzero(burn_arr > 0)),
            })

        # 8. Run Manifest
        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=f"{t1_scene_id}__to__{t2_scene_id}",
            tool_name="06_Temporal_Change_Detection",
            parameters={
                "metric_name": metric_name,
                "t1_scene_id": t1_scene_id,
                "t2_scene_id": t2_scene_id,
                "t1_date": t1_date,
                "t2_date": t2_date,
                "calc_relative": calc_relative,
                "classify_severity": classify_severity,
                "has_aoi": aoi_geometry is not None,
            },
            output_products=executed_products,
            qa_summary={
                "t1_scene": t1_scene_id,
                "t2_scene": t2_scene_id,
                "mean_delta": delta_stats["mean"],
                "std_delta": delta_stats["std"],
                "valid_pixels": int(np.count_nonzero(valid_mask)),
            },
            extra_metadata={
                "change_metric": metric_name,
                "baseline_epoch": {"scene_id": t1_scene_id, "date": t1_date},
                "target_epoch": {"scene_id": t2_scene_id, "date": t2_date},
            },
        )

        return {
            "t1_scene_id": t1_scene_id,
            "t2_scene_id": t2_scene_id,
            "results_dir": str(results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
            "delta_statistics": delta_stats,
        }
