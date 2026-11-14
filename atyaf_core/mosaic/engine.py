"""Quality-aware multi-scene mosaic blending engine with provenance tracking."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

from atyaf_core.discovery.models import SceneInfo
from atyaf_core.mosaic.models import MosaicResult, MosaicStrategy, SceneContribution
from atyaf_core.raster.clip import PolygonClipEngine
from atyaf_core.raster.workspace import WorkspaceManager


class QualityMosaicEngine:
    """Combines multiple independent scene results into a scientifically valid mosaic
    using quality ranking, temporal selection, and source pixel provenance tracking.
    """

    @classmethod
    def generate_mosaic_set_id(cls, scene_ids: List[str]) -> str:
        """Generates a deterministic stable mosaic set identifier based on sorted scene IDs."""
        sorted_scenes = sorted(scene_ids)
        hash_digest = hashlib.sha256(";;".join(sorted_scenes).encode("utf-8")).hexdigest()[:8]
        return f"Mosaic_{hash_digest}"

    @classmethod
    def run_mosaic(
        cls,
        scene_products: List[Tuple[SceneInfo, Path]],
        product_name: str,
        category: str,
        output_root: Path,
        strategy: MosaicStrategy = MosaicStrategy.HIGHEST_QUALITY,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
    ) -> MosaicResult:
        """Mosaics a collection of scene product rasters into a combined output with provenance tracking."""
        if not scene_products:
            raise ValueError("No input scene products provided for mosaic.")

        scene_ids = [sc.metadata.scene_id for sc, _ in scene_products]
        mosaic_set_id = cls.generate_mosaic_set_id(scene_ids)

        # 1. Determine destination folder structure:
        # Results/Mosaic_<set_id>/<category>/<product_name>/
        results_root = output_root / "Results" / mosaic_set_id / category / product_name
        results_root.mkdir(parents=True, exist_ok=True)
        reports_dir = output_root / "Reports"

        # 2. Inspect bounds, resolution, and CRS of all input rasters
        datasets_info = []
        target_crs = None
        min_res_x, min_res_y = float("inf"), float("inf")
        min_x, min_y, max_x, max_y = float("inf"), float("inf"), float("-inf"), float("-inf")

        for idx, (scene, r_path) in enumerate(scene_products, start=1):
            with rasterio.open(r_path) as ds:
                if target_crs is None:
                    target_crs = ds.crs
                elif ds.crs != target_crs:
                    pass  # reproject handles differing CRSs

                b = ds.bounds
                min_x = min(min_x, b.left)
                min_y = min(min_y, b.bottom)
                max_x = max(max_x, b.right)
                max_y = max(max_y, b.top)

                res_x, res_y = abs(ds.res[0]), abs(ds.res[1])
                min_res_x = min(min_res_x, res_x)
                min_res_y = min(min_res_y, res_y)

                datasets_info.append({
                    "numeric_id": idx,
                    "scene_id": scene.metadata.scene_id,
                    "date": scene.metadata.acquisition_date,
                    "path": r_path,
                })

        # 3. Construct unified target grid and affine transform
        target_transform = rasterio.transform.from_origin(min_x, max_y, min_res_x, min_res_y)
        width = int(round((max_x - min_x) / min_res_x))
        height = int(round((max_y - min_y) / min_res_y))

        if width <= 0 or height <= 0:
            raise ValueError(f"Computed mosaic dimensions invalid: {width}x{height}")

        # Allocation
        mosaic_arr = np.full((height, width), np.nan, dtype=np.float32)
        provenance_arr = np.zeros((height, width), dtype=np.uint16)
        count_arr = np.zeros((height, width), dtype=np.int32)
        sum_arr = np.zeros((height, width), dtype=np.float64)

        # Sort scenes based on strategy if necessary
        ordered_items = list(enumerate(scene_products, start=1))
        if strategy == MosaicStrategy.LATEST_DATE:
            # Sort ascending by date so latest is applied last and wins
            ordered_items.sort(key=lambda item: item[1][0].metadata.acquisition_date)

        # 4. Reproject each scene onto target grid and blend
        for numeric_id, (scene, r_path) in ordered_items:
            scene_dst = np.full((height, width), np.nan, dtype=np.float32)
            with rasterio.open(r_path) as src_ds:
                src_arr = src_ds.read(1).astype(np.float32)
                src_nodata = src_ds.nodata
                if src_nodata is not None:
                    src_arr[src_arr == src_nodata] = np.nan

                reproject(
                    source=src_arr,
                    destination=scene_dst,
                    src_transform=src_ds.transform,
                    src_crs=src_ds.crs,
                    dst_transform=target_transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear,
                    src_nodata=np.nan,
                    dst_nodata=np.nan,
                )

            valid_mask = ~np.isnan(scene_dst)

            if strategy == MosaicStrategy.MEAN_VALID:
                sum_arr[valid_mask] += scene_dst[valid_mask]
                count_arr[valid_mask] += 1
                # Provenance records the scene
                provenance_arr[valid_mask] = numeric_id
            elif strategy == MosaicStrategy.LATEST_DATE:
                mosaic_arr[valid_mask] = scene_dst[valid_mask]
                provenance_arr[valid_mask] = numeric_id
            else:  # HIGHEST_QUALITY or FIRST_VALID
                unfilled_mask = valid_mask & np.isnan(mosaic_arr)
                mosaic_arr[unfilled_mask] = scene_dst[unfilled_mask]
                provenance_arr[unfilled_mask] = numeric_id

        if strategy == MosaicStrategy.MEAN_VALID:
            valid_counts = count_arr > 0
            with np.errstate(divide="ignore", invalid="ignore"):
                mosaic_arr = np.where(valid_counts, (sum_arr / np.maximum(count_arr, 1)).astype(np.float32), np.nan)

        # 5. Compute statistics
        valid_pixels = int(np.count_nonzero(~np.isnan(mosaic_arr)))
        nodata_pixels = int(np.count_nonzero(np.isnan(mosaic_arr)))
        valid_vals = mosaic_arr[~np.isnan(mosaic_arr)]

        if len(valid_vals) > 0:
            stats = {
                "min": float(np.min(valid_vals)),
                "max": float(np.max(valid_vals)),
                "mean": float(np.mean(valid_vals)),
                "std": float(np.std(valid_vals)),
            }
        else:
            stats = {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0}

        # 6. Write primary mosaic GeoTIFF
        mosaic_filename = f"{product_name}_MOSAIC_FULL.tif"
        full_mosaic_path = results_root / mosaic_filename

        profile = {
            "driver": "GTiff",
            "width": width,
            "height": height,
            "count": 1,
            "dtype": "float32",
            "crs": target_crs,
            "transform": target_transform,
            "nodata": -9999.0,
        }

        mosaic_arr_nodata = np.where(np.isnan(mosaic_arr), -9999.0, mosaic_arr).astype(np.float32)
        with rasterio.open(full_mosaic_path, "w", **profile) as dst:
            dst.write(mosaic_arr_nodata, 1)

        # 7. Write provenance raster (Source_Scene_ID.tif)
        provenance_filename = f"{product_name}_MOSAIC_Source_Scene_ID.tif"
        provenance_path = results_root / provenance_filename
        prov_profile = profile.copy()
        prov_profile.update({"dtype": "uint16", "nodata": 0})

        with rasterio.open(provenance_path, "w", **prov_profile) as dst:
            dst.write(provenance_arr, 1)

        # 8. Optional AOI Polygon Clipping
        clipped_path = None
        if aoi_geometry is not None:
            clipped_filename = f"{product_name}_MOSAIC_AOI_CLIP.tif"
            clipped_full_path = results_root / clipped_filename
            PolygonClipEngine.clip_raster_file(
                src_raster_path=full_mosaic_path,
                dst_raster_path=clipped_full_path,
                aoi_geometry=aoi_geometry,
                aoi_crs=aoi_crs,
                crop=True,
                nodata=-9999.0,
            )
            clipped_path = str(clipped_full_path)

        # 9. Create run manifest in Reports/
        contributions = [
            {
                "numeric_id": d["numeric_id"],
                "scene_id": d["scene_id"],
                "acquisition_date": d["date"],
                "input_raster": str(d["path"]),
            }
            for d in datasets_info
        ]

        WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=mosaic_set_id,
            tool_name="MultiScene_Quality_Mosaic",
            parameters={
                "product_name": product_name,
                "strategy": strategy.value,
                "scene_count": len(scene_products),
                "has_aoi": aoi_geometry is not None,
            },
            output_products=[
                {
                    "product_name": f"{product_name}_MOSAIC",
                    "category": category,
                    "full_path": str(full_mosaic_path),
                    "clipped_path": clipped_path,
                    "provenance_path": str(provenance_path),
                    "statistics": stats,
                    "valid_pixels": valid_pixels,
                    "nodata_pixels": nodata_pixels,
                }
            ],
            qa_summary={
                "scene_count": len(scene_products),
                "valid_pixels": valid_pixels,
                "nodata_pixels": nodata_pixels,
            },
            extra_metadata={
                "mosaic_strategy": strategy.value,
                "scene_contributions": contributions,
            },
        )

        return MosaicResult(
            mosaic_id=mosaic_set_id,
            product_name=product_name,
            category=category,
            full_path=str(full_mosaic_path),
            clipped_path=clipped_path,
            provenance_path=str(provenance_path),
            scene_contributions=contributions,
            statistics=stats,
            valid_pixels=valid_pixels,
            nodata_pixels=nodata_pixels,
        )
