"""Environmental & Drought Analysis execution engine (Tool 04)."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import rasterio
from atiaf_core.raster.safe_io import atomic_raster

from atiaf_core.discovery.models import BandRole, SceneInfo
from atiaf_core.indices.engine import SpectralIndicesEngine
from atiaf_core.raster.clip import PolygonClipEngine
from atiaf_core.raster.windowed import WindowedRasterEngine
from atiaf_core.raster.workspace import WorkspaceManager
from atiaf_core.temperature.engine import SurfaceTemperatureEngine


class EnvironmentalDroughtEngine:
    """Calculates broadband surface albedo, Temperature Vegetation Dryness Index (TVDI),
    and Vegetation Health Index (VHI) for agricultural and environmental monitoring.
    """

    @classmethod
    def calc_broadband_albedo(cls, bands: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculates shortwave broadband surface albedo using Liang (2001) formulation:
        alpha = 0.356*Blue + 0.130*Red + 0.373*NIR + 0.085*SWIR1 + 0.072*SWIR2 - 0.0018
        """
        b = bands["blue"]
        r = bands["red"]
        nir = bands["nir"]
        s1 = bands["swir1"]
        s2 = bands["swir2"]

        albedo = 0.356 * b + 0.130 * r + 0.373 * nir + 0.085 * s1 + 0.072 * s2 - 0.0018
        return np.clip(albedo, 0.0, 1.0)

    @classmethod
    def calc_tvdi(cls, lst_celsius: np.ndarray, ndvi: np.ndarray) -> np.ndarray:
        """Calculates Temperature Vegetation Dryness Index (TVDI) normalized across valid space:
        TVDI = (LST - LST_min) / (LST_max - LST_min), clamped to [0.0, 1.0].
        Values near 0 indicate moist/well-watered conditions; values near 1 indicate drought stress.
        """
        valid_mask = ~np.isnan(lst_celsius) & ~np.isnan(ndvi)
        tvdi = np.full_like(lst_celsius, np.nan, dtype=np.float32)

        vals = lst_celsius[valid_mask]
        if len(vals) == 0:
            return tvdi

        min_t = float(np.min(vals))
        max_t = float(np.max(vals))
        range_t = max_t - min_t

        if range_t <= 0:
            tvdi[valid_mask] = 0.5
            return tvdi

        norm_t = (lst_celsius - min_t) / range_t
        tvdi[valid_mask] = np.clip(norm_t[valid_mask], 0.0, 1.0).astype(np.float32)
        return tvdi

    @classmethod
    def run_environmental_analysis(
        cls,
        scene: SceneInfo,
        calculate_albedo: bool = True,
        calculate_tvdi: bool = True,
        custom_destination: Optional[Path] = None,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
        apply_qa_mask: bool = True,
        block_size: int = 512,
    ) -> Dict[str, Any]:
        """Runs the environmental and drought analysis suite for an identified scene."""
        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            scene_path=scene.scene_path,
            custom_destination=custom_destination,
        )

        env_results_dir = results_dir / "Environmental_Analysis"
        env_results_dir.mkdir(parents=True, exist_ok=True)

        executed_products: List[Dict[str, Any]] = []

        # 1. Broadband Surface Albedo
        if calculate_albedo:
            required_roles = [BandRole.BLUE, BandRole.RED, BandRole.NIR, BandRole.SWIR_1, BandRole.SWIR_2]
            if all(scene.has_role(r) for r in required_roles):
                albedo_file = WorkspaceManager.unique_path(env_results_dir / f"ALBEDO_{scene.metadata.scene_id}_FULL.tif")
                band_inputs = {
                    "blue": scene.bands[BandRole.BLUE].file_path,
                    "red": scene.bands[BandRole.RED].file_path,
                    "nir": scene.bands[BandRole.NIR].file_path,
                    "swir1": scene.bands[BandRole.SWIR_1].file_path,
                    "swir2": scene.bands[BandRole.SWIR_2].file_path,
                }

                def albedo_block(blocks: Dict[str, np.ndarray]) -> np.ndarray:
                    scaled_blocks = {}
                    for k, role in [("blue", BandRole.BLUE), ("red", BandRole.RED), ("nir", BandRole.NIR), ("swir1", BandRole.SWIR_1), ("swir2", BandRole.SWIR_2)]:
                        raw = blocks[k].astype(np.float32)
                        asset = scene.bands[role]
                        scaled = raw * asset.scale_factor + asset.offset
                        if asset.nodata is not None:
                            scaled[raw == asset.nodata] = np.nan
                        if asset.valid_min is not None:
                            scaled[raw < asset.valid_min] = np.nan
                        if asset.valid_max is not None:
                            scaled[raw > asset.valid_max] = np.nan
                        valid_px = np.isfinite(scaled)
                        scaled[valid_px & (scaled < 0.0001)] = 0.0001
                        scaled_blocks[k] = scaled
                    return cls.calc_broadband_albedo(scaled_blocks)

                calc_meta = WindowedRasterEngine.process_bands(
                    band_paths=band_inputs,
                    output_path=albedo_file,
                    compute_fn=albedo_block,
                    output_nodata=-9999.0,
                    block_size=block_size,
                )

                albedo_clip = None
                if aoi_geometry is not None:
                    albedo_clip_file = WorkspaceManager.unique_path(env_results_dir / f"ALBEDO_{scene.metadata.scene_id}_AOI_CLIP.tif")
                    PolygonClipEngine.clip_raster_file(
                        src_raster_path=albedo_file, dst_raster_path=albedo_clip_file, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs, crop=True, nodata=-9999.0
                    )
                    albedo_clip = str(albedo_clip_file)

                executed_products.append({
                    "product_name": "Broadband_Albedo",
                    "full_path": str(albedo_file),
                    "clipped_path": albedo_clip,
                    "statistics": calc_meta["statistics"],
                    "valid_pixels": calc_meta["valid_pixels"],
                })

        # 2. Temperature Vegetation Dryness Index (TVDI)
        if calculate_tvdi:
            if scene.has_thermal() and scene.has_role(BandRole.RED) and scene.has_role(BandRole.NIR):
                # Obtain LST and NDVI
                lst_res = SurfaceTemperatureEngine.run_surface_temperature(
                    scene=scene, method="Official_L2_ST", output_unit="Celsius", custom_destination=custom_destination, apply_qa_mask=apply_qa_mask
                )
                ndvi_res = SpectralIndicesEngine.run_scene_indices(
                    scene=scene, selected_index_ids=["NDVI"], custom_destination=custom_destination, apply_qa_mask=apply_qa_mask
                )

                lst_path = Path(lst_res["executed_products"][0]["full_path"])
                ndvi_path = Path(ndvi_res["executed_products"][0]["full_path"])

                with rasterio.open(lst_path) as ds_lst, rasterio.open(ndvi_path) as ds_ndvi:
                    profile = ds_lst.meta.copy()
                    lst_arr = ds_lst.read(1).astype(np.float32)
                    ndvi_arr = ds_ndvi.read(1).astype(np.float32)
                    if ds_lst.nodata is not None:
                        lst_arr[lst_arr == ds_lst.nodata] = np.nan
                    if ds_ndvi.nodata is not None:
                        ndvi_arr[ndvi_arr == ds_ndvi.nodata] = np.nan

                tvdi_arr = cls.calc_tvdi(lst_arr, ndvi_arr)

                tvdi_file = WorkspaceManager.unique_path(env_results_dir / f"TVDI_{scene.metadata.scene_id}_FULL.tif")
                tvdi_prof = profile.copy()
                tvdi_prof.update({"dtype": "float32", "nodata": -9999.0})
                tvdi_nodata = np.where(np.isnan(tvdi_arr), -9999.0, tvdi_arr).astype(np.float32)
                with atomic_raster(tvdi_file, "w", **tvdi_prof) as dst:
                    dst.write(tvdi_nodata, 1)

                tvdi_clip = None
                if aoi_geometry is not None:
                    tvdi_clip_file = WorkspaceManager.unique_path(env_results_dir / f"TVDI_{scene.metadata.scene_id}_AOI_CLIP.tif")
                    PolygonClipEngine.clip_raster_file(
                        src_raster_path=tvdi_file, dst_raster_path=tvdi_clip_file, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs, crop=True, nodata=-9999.0
                    )
                    tvdi_clip = str(tvdi_clip_file)

                valid_tvdi = tvdi_arr[~np.isnan(tvdi_arr)]
                stats_tvdi = {
                    "min": float(np.min(valid_tvdi)) if len(valid_tvdi) > 0 else 0.0,
                    "max": float(np.max(valid_tvdi)) if len(valid_tvdi) > 0 else 0.0,
                    "mean": float(np.mean(valid_tvdi)) if len(valid_tvdi) > 0 else 0.0,
                    "std": float(np.std(valid_tvdi)) if len(valid_tvdi) > 0 else 0.0,
                }

                executed_products.append({
                    "product_name": "TVDI",
                    "full_path": str(tvdi_file),
                    "clipped_path": tvdi_clip,
                    "statistics": stats_tvdi,
                    "valid_pixels": int(len(valid_tvdi)),
                })

        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=scene.metadata.scene_id,
            tool_name="04_Environmental_Drought_Analysis",
            parameters={
                "calculate_albedo": calculate_albedo,
                "calculate_tvdi": calculate_tvdi,
                "apply_qa_mask": apply_qa_mask,
                "has_aoi": aoi_geometry is not None,
            },
            output_products=executed_products,
            qa_summary={"executed_products_count": len(executed_products)},
        )

        return {
            "scene_id": scene.metadata.scene_id,
            "results_dir": str(env_results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
        }
