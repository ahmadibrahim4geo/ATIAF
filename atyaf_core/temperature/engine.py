"""Surface Temperature execution engine coordinating LST extraction, emissivity, and QA masking."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from atyaf_core.discovery.models import BandRole, SceneInfo
from atyaf_core.raster.clip import PolygonClipEngine
from atyaf_core.raster.masks import QualityMaskEngine
from atyaf_core.raster.windowed import WindowedRasterEngine
from atyaf_core.raster.workspace import WorkspaceManager
from atyaf_core.temperature.emissivity import EmissivityEngine


class SurfaceTemperatureEngine:
    """Computes Land Surface Temperature (LST), Brightness Temperature (BT), and
    Surface Emissivity (LSE) with physical unit verification (Kelvin/Celsius).
    """

    KELVIN_TO_CELSIUS = 273.15

    @classmethod
    def run_surface_temperature(
        cls,
        scene: SceneInfo,
        method: str = "Official_L2_ST",  # 'Official_L2_ST', 'Brightness_Temperature', 'Emissivity_NDVI'
        output_unit: str = "Celsius",     # 'Celsius' or 'Kelvin'
        custom_destination: Optional[Path] = None,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
        apply_qa_mask: bool = True,
        block_size: int = 512,
    ) -> Dict[str, Any]:
        """Calculates Surface Temperature or Emissivity for an identified scene."""
        # 1. Strict Physics Gating: Sentinel-2 and Landsat MSS have NO thermal bands!
        if not scene.has_thermal():
            raise ValueError(
                f"Scene '{scene.metadata.scene_id}' ({scene.metadata.platform}) lacks thermal infrared measurement bands. "
                "Surface Temperature cannot be computed (Sentinel-2 MSI has no thermal bands)."
            )

        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            scene_path=scene.scene_path,
            custom_destination=custom_destination,
        )

        executed_products: List[Dict[str, Any]] = []
        log_messages: List[str] = [
            f"Starting ATIAF Surface Temperature processing for scene: {scene.metadata.scene_id}",
            f"Platform: {scene.metadata.platform}, Sensor: {scene.metadata.instrument}",
            f"Method: {method}, Target Unit: {output_unit}",
        ]

        # Locate thermal band asset
        therm_asset = scene.get_band(BandRole.THERMAL_1) or scene.get_band(BandRole.THERMAL_2)
        if not therm_asset:
            raise ValueError("Could not locate thermal infrared raster band asset in scene.")

        # Check QA mask
        qa_mask_asset = None
        is_landsat = "LANDSAT" in scene.metadata.sensor_family.value.upper()
        if apply_qa_mask and is_landsat and "QA_PIXEL" in scene.quality_masks:
            qa_mask_asset = scene.quality_masks["QA_PIXEL"]

        # Output raster path
        product_slug = f"LST_{output_unit.upper()}" if method == "Official_L2_ST" else method.upper()
        full_output_path = WorkspaceManager.get_output_raster_path(
            results_dir=results_dir,
            category="Surface_Temperature",
            method_name=product_slug,
            scene_id=scene.metadata.scene_id,
            is_clip=False,
        )

        band_inputs = {"therm": therm_asset.file_path}
        if qa_mask_asset:
            band_inputs["__QA__"] = qa_mask_asset.file_path

        # If Emissivity from NDVI is requested, also include Red and NIR bands
        if method == "Emissivity_NDVI":
            if not (scene.has_role(BandRole.RED) and scene.has_role(BandRole.NIR)):
                raise ValueError("Emissivity calculation requires Red and NIR bands for NDVI.")
            band_inputs["red"] = scene.bands[BandRole.RED].file_path
            band_inputs["nir"] = scene.bands[BandRole.NIR].file_path

        def block_calc(blocks: Dict[str, np.ndarray]) -> np.ndarray:
            raw_therm = blocks["therm"].astype(np.float32)

            # Preprocessing: convert raw DN to Kelvin
            st_k = raw_therm * therm_asset.scale_factor + therm_asset.offset

            # Nodata handling
            if therm_asset.nodata is not None:
                st_k[raw_therm == therm_asset.nodata] = np.nan
            if therm_asset.valid_min is not None:
                st_k[raw_therm < therm_asset.valid_min] = np.nan
            if therm_asset.valid_max is not None:
                st_k[raw_therm > therm_asset.valid_max] = np.nan

            # QA mask
            clear_mask = None
            if "__QA__" in blocks and is_landsat:
                clear_mask = QualityMaskEngine.get_landsat_c2_clear_mask(blocks["__QA__"])
                st_k[~clear_mask] = np.nan

            if method == "Emissivity_NDVI":
                raw_red = blocks["red"].astype(np.float32)
                raw_nir = blocks["nir"].astype(np.float32)
                red_scaled = raw_red * scene.bands[BandRole.RED].scale_factor + scene.bands[BandRole.RED].offset
                nir_scaled = raw_nir * scene.bands[BandRole.NIR].scale_factor + scene.bands[BandRole.NIR].offset
                with np.errstate(divide="ignore", invalid="ignore"):
                    denom = nir_scaled + red_scaled
                    ndvi = np.where(denom == 0, np.nan, (nir_scaled - red_scaled) / denom)
                if clear_mask is not None:
                    ndvi[~clear_mask] = np.nan
                return EmissivityEngine.calc_land_surface_emissivity(ndvi)

            # Surface Temperature
            if output_unit == "Celsius":
                return st_k - cls.KELVIN_TO_CELSIUS
            return st_k

        calc_meta = WindowedRasterEngine.process_bands(
            band_paths=band_inputs,
            output_path=full_output_path,
            compute_fn=block_calc,
            output_nodata=-9999.0,
            block_size=block_size,
        )

        product_record = {
            "product_name": product_slug,
            "category": "Surface_Temperature",
            "method": method,
            "unit": output_unit if method != "Emissivity_NDVI" else "dimensionless",
            "full_path": str(full_output_path),
            "clipped_path": None,
            "statistics": calc_meta["statistics"],
            "valid_pixels": calc_meta["valid_pixels"],
            "nodata_pixels": calc_meta["nodata_pixels"],
        }

        # Optional Polygon Clipping
        if aoi_geometry is not None:
            clip_output_path = WorkspaceManager.get_output_raster_path(
                results_dir=results_dir,
                category="Surface_Temperature",
                method_name=product_slug,
                scene_id=scene.metadata.scene_id,
                is_clip=True,
                aoi_slug="AOI",
            )
            log_messages.append("Clipping thermal product with study area polygon...")
            PolygonClipEngine.clip_raster_file(
                src_raster_path=full_output_path,
                dst_raster_path=clip_output_path,
                aoi_geometry=aoi_geometry,
                aoi_crs=aoi_crs,
                crop=True,
                nodata=-9999.0,
            )
            product_record["clipped_path"] = str(clip_output_path)

        executed_products.append(product_record)

        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=scene.metadata.scene_id,
            tool_name="02_Surface_Temperature",
            parameters={
                "method": method,
                "output_unit": output_unit,
                "apply_qa_mask": apply_qa_mask,
                "has_aoi": aoi_geometry is not None,
            },
            output_products=executed_products,
            qa_summary={"executed_count": len(executed_products)},
            log_messages=log_messages,
        )

        return {
            "scene_id": scene.metadata.scene_id,
            "results_dir": str(results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
            "log": log_messages,
        }
