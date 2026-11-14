"""Spectral index execution engine coordinating discovery, windowed calculation, and workspace management."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from atyaf_core.discovery.models import BandRole, SceneInfo
from atyaf_core.indices.registry import INDEX_CATALOG, SpectralIndexDefinition
from atyaf_core.raster.clip import PolygonClipEngine
from atyaf_core.raster.masks import QualityMaskEngine
from atyaf_core.raster.windowed import WindowedRasterEngine
from atyaf_core.raster.workspace import WorkspaceManager


class SpectralIndicesEngine:
    """Coordinates the end-to-end execution of spectral index calculations for a scene."""

    @classmethod
    def get_supported_indices_for_scene(cls, scene: SceneInfo) -> List[SpectralIndexDefinition]:
        """Returns all spectral indices that can be computed from the available bands of this scene."""
        supported = []
        for index_def in INDEX_CATALOG.values():
            if all(scene.has_role(r) for r in index_def.required_roles):
                supported.append(index_def)
        return supported

    @classmethod
    def run_scene_indices(
        cls,
        scene: SceneInfo,
        selected_index_ids: List[str],
        custom_destination: Optional[Path] = None,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
        apply_qa_mask: bool = True,
        block_size: int = 512,
        custom_constants: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Executes selected spectral indices on an identified scene.
        
        Returns a dictionary containing executed products, skipped indices,
        and run manifest details.
        """
        custom_constants = custom_constants or {}

        # Gating: Enforce sensor modality compatibility (never route SAR to optical)
        from atyaf_core.modalities import ModalityRouter
        ModalityRouter.validate_tool_compatibility(scene.metadata, "Spectral_Indices")

        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            scene_path=scene.scene_path,
            custom_destination=custom_destination,
        )

        executed_products: List[Dict[str, Any]] = []
        skipped_indices: List[Dict[str, str]] = []
        log_messages: List[str] = [
            f"Starting ATIAF Spectral Indices processing for scene: {scene.metadata.scene_id}",
            f"Sensor: {scene.metadata.platform} ({scene.metadata.instrument}), Level: {scene.metadata.product_level.value}",
        ]

        # Check for QA mask asset
        qa_mask_asset = None
        is_landsat = "LANDSAT" in scene.metadata.sensor_family.value.upper()
        is_sentinel2 = "SENTINEL" in scene.metadata.sensor_family.value.upper()

        if apply_qa_mask:
            if is_landsat and "QA_PIXEL" in scene.quality_masks:
                qa_mask_asset = scene.quality_masks["QA_PIXEL"]
            elif is_sentinel2 and "SCL" in scene.quality_masks:
                qa_mask_asset = scene.quality_masks["SCL"]

        for idx_id in selected_index_ids:
            if idx_id not in INDEX_CATALOG:
                skipped_indices.append({"id": idx_id, "reason": "Index ID not recognized in scientific catalog."})
                continue

            index_def = INDEX_CATALOG[idx_id]

            # Verify all required band roles are present in the scene
            missing_roles = [r.value for r in index_def.required_roles if not scene.has_role(r)]
            if missing_roles:
                reason = f"Scene lacks required physical band(s): {', '.join(missing_roles)}"
                skipped_indices.append({"id": idx_id, "reason": reason})
                log_messages.append(f"Skipped {idx_id}: {reason}")
                continue

            # Determine output paths
            full_output_path = WorkspaceManager.get_output_raster_path(
                results_dir=results_dir,
                category=index_def.category,
                method_name=index_def.acronym,
                scene_id=scene.metadata.scene_id,
                is_clip=False,
            )

            # Check cache fingerprint
            band_paths_for_hash = [scene.bands[r].file_path for r in index_def.required_roles]
            if qa_mask_asset:
                band_paths_for_hash.append(qa_mask_asset.file_path)

            fingerprint = WorkspaceManager.compute_cache_fingerprint(
                source_paths=band_paths_for_hash,
                method_name=idx_id,
                parameters={"apply_qa_mask": apply_qa_mask, "constants": custom_constants},
            )

            # Map inputs for windowed processor
            band_inputs: Dict[str, Path] = {
                r.value: scene.bands[r].file_path for r in index_def.required_roles
            }
            if qa_mask_asset:
                band_inputs["__QA__"] = qa_mask_asset.file_path

            # Define per-block mathematical callback
            def block_computation(blocks: Dict[str, np.ndarray]) -> np.ndarray:
                # 1. Scale inputs to reflectance float32
                scaled_bands: Dict[BandRole, np.ndarray] = {}
                for r in index_def.required_roles:
                    asset = scene.bands[r]
                    raw = blocks[r.value].astype(np.float32)
                    scaled = raw * asset.scale_factor + asset.offset
                    # Check nodata
                    if asset.nodata is not None:
                        scaled[raw == asset.nodata] = np.nan
                    scaled_bands[r] = scaled

                # 2. Compute clear mask if QA is enabled
                clear_mask = None
                if "__QA__" in blocks:
                    qa_block = blocks["__QA__"]
                    if is_landsat:
                        clear_mask = QualityMaskEngine.get_landsat_c2_clear_mask(qa_block)
                    elif is_sentinel2:
                        clear_mask = QualityMaskEngine.get_sentinel2_scl_clear_mask(qa_block)

                # 3. Calculate index
                res = index_def.compute_fn(scaled_bands, **custom_constants)

                # 4. Apply QA mask and valid range
                if clear_mask is not None:
                    res[~clear_mask] = np.nan

                # Restrict to theoretical valid range e.g. -1.0 to 1.0
                v_min, v_max = index_def.valid_range
                res[(res < v_min) | (res > v_max)] = np.nan
                return res

            log_messages.append(f"Calculating {index_def.acronym} ({index_def.formula_text})...")
            calc_meta = WindowedRasterEngine.process_bands(
                band_paths=band_inputs,
                output_path=full_output_path,
                compute_fn=block_computation,
                output_nodata=-9999.0,
                block_size=block_size,
            )

            product_record = {
                "index_id": idx_id,
                "acronym": index_def.acronym,
                "category": index_def.category,
                "full_path": str(full_output_path),
                "clipped_path": None,
                "statistics": calc_meta["statistics"],
                "valid_pixels": calc_meta["valid_pixels"],
                "nodata_pixels": calc_meta["nodata_pixels"],
                "fingerprint": fingerprint,
            }

            # Optional Polygon Clipping
            if aoi_geometry is not None:
                clip_output_path = WorkspaceManager.get_output_raster_path(
                    results_dir=results_dir,
                    category=index_def.category,
                    method_name=index_def.acronym,
                    scene_id=scene.metadata.scene_id,
                    is_clip=True,
                    aoi_slug="AOI",
                )
                log_messages.append(f"Clipping {index_def.acronym} with study area polygon...")
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

        # Write run manifest
        qa_summary = {
            "total_indices_requested": len(selected_index_ids),
            "executed_count": len(executed_products),
            "skipped_count": len(skipped_indices),
        }
        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id=scene.metadata.scene_id,
            tool_name="01_Spectral_Indices",
            parameters={
                "selected_indices": selected_index_ids,
                "apply_qa_mask": apply_qa_mask,
                "has_aoi": aoi_geometry is not None,
                "custom_constants": custom_constants,
            },
            output_products=executed_products,
            qa_summary=qa_summary,
            log_messages=log_messages,
        )

        return {
            "scene_id": scene.metadata.scene_id,
            "results_dir": str(results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
            "skipped_indices": skipped_indices,
            "log": log_messages,
        }
