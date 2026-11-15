"""Geological & Mineral Analysis execution engine with historical sensor degradation gating."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from atiaf_core.discovery.models import BandRole, SceneInfo
from atiaf_core.geology.registry import GEOLOGICAL_CATALOG, GeologicalIndexDefinition
from atiaf_core.raster.clip import PolygonClipEngine
from atiaf_core.raster.masks import QualityMaskEngine
from atiaf_core.raster.windowed import WindowedRasterEngine
from atiaf_core.raster.workspace import WorkspaceManager


class GeologicalAnalysisEngine:
    """Coordinates geological band ratio and thermal mineral index calculations,
    enforcing historical sensor restrictions (e.g., ASTER post-April 2008 SWIR degradation).
    """

    SCIENTIFIC_DISCLAIMER = (
        "Scientific Disclaimer: Geological spectral ratios and thermal indices provide "
        "diagnostic/probabilistic surface alteration indications and do not constitute confirmed mineral assays."
    )

    @classmethod
    def get_supported_indices_for_scene(cls, scene: SceneInfo) -> List[GeologicalIndexDefinition]:
        """Returns all geological indices supported by the scene's available bands and date."""
        supported = []
        is_aster_swir_degraded = "ASTER_SWIR_INVALID_POST_2008" in scene.metadata.restrictions

        for g_def in GEOLOGICAL_CATALOG.values():
            if g_def.requires_swir and is_aster_swir_degraded:
                continue
            if all(scene.has_role(r) for r in g_def.required_roles):
                supported.append(g_def)
        return supported

    @classmethod
    def run_geological_analysis(
        cls,
        scene: SceneInfo,
        selected_index_ids: List[str],
        custom_destination: Optional[Path] = None,
        aoi_geometry: Optional[Any] = None,
        aoi_crs: Optional[Any] = None,
        apply_qa_mask: bool = True,
        block_size: int = 512,
    ) -> Dict[str, Any]:
        """Executes selected geological and mineral indices on an identified scene."""
        from atiaf_core.modalities import ModalityRouter
        ModalityRouter.validate_tool_compatibility(scene.metadata, "Geological_Analysis")

        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            scene_path=scene.scene_path,
            custom_destination=custom_destination,
        )

        executed_products: List[Dict[str, Any]] = []
        skipped_indices: List[Dict[str, str]] = []
        log_messages: List[str] = [
            f"Starting ATIAF Geological & Mineral Analysis for scene: {scene.metadata.scene_id}",
            f"Platform: {scene.metadata.platform}, Sensor: {scene.metadata.instrument}",
            cls.SCIENTIFIC_DISCLAIMER,
        ]

        # Check ASTER SWIR degradation constraint
        is_aster_swir_degraded = "ASTER_SWIR_INVALID_POST_2008" in scene.metadata.restrictions
        if is_aster_swir_degraded:
            log_messages.append(
                "Notice: ASTER scene acquired after April 2008. SWIR bands are degraded; SWIR mineral indices are gated."
            )

        # Check QA mask
        qa_mask_asset = None
        is_landsat = "LANDSAT" in scene.metadata.sensor_family.value.upper()
        if apply_qa_mask and is_landsat and "QA_PIXEL" in scene.quality_masks:
            qa_mask_asset = scene.quality_masks["QA_PIXEL"]

        for g_id in selected_index_ids:
            if g_id not in GEOLOGICAL_CATALOG:
                skipped_indices.append({"id": g_id, "reason": "Index ID not recognized in geological catalog."})
                continue

            g_def = GEOLOGICAL_CATALOG[g_id]

            # Enforce ASTER SWIR gate
            if g_def.requires_swir and is_aster_swir_degraded:
                reason = "ASTER SWIR subsystem degraded after April 2008. Index disabled for scientific validity."
                skipped_indices.append({"id": g_id, "reason": reason})
                log_messages.append(f"Skipped {g_id}: {reason}")
                continue

            # Verify all required bands exist
            missing_roles = [r.value for r in g_def.required_roles if not scene.has_role(r)]
            if missing_roles:
                reason = f"Scene lacks required band(s): {', '.join(missing_roles)}"
                skipped_indices.append({"id": g_id, "reason": reason})
                log_messages.append(f"Skipped {g_id}: {reason}")
                continue

            # Output paths
            full_output_path = WorkspaceManager.get_output_raster_path(
                results_dir=results_dir,
                category="Geological_Analysis",
                method_name=g_def.acronym,
                scene_id=scene.metadata.scene_id,
                is_clip=False,
            )

            # Map band inputs
            band_inputs = {r.value: scene.bands[r].file_path for r in g_def.required_roles}
            if qa_mask_asset:
                band_inputs["__QA__"] = qa_mask_asset.file_path

            def block_calc(blocks: Dict[str, np.ndarray]) -> np.ndarray:
                scaled_bands: Dict[BandRole, np.ndarray] = {}
                for r in g_def.required_roles:
                    asset = scene.bands[r]
                    raw = blocks[r.value].astype(np.float32)
                    scaled = raw * asset.scale_factor + asset.offset
                    if asset.nodata is not None:
                        scaled[raw == asset.nodata] = np.nan
                    if asset.valid_min is not None:
                        scaled[raw < asset.valid_min] = np.nan
                    if asset.valid_max is not None:
                        scaled[raw > asset.valid_max] = np.nan
                    scaled_bands[r] = scaled

                clear_mask = None
                if "__QA__" in blocks and is_landsat:
                    clear_mask = QualityMaskEngine.get_landsat_c2_clear_mask(blocks["__QA__"])

                ratio_result = g_def.compute_fn(scaled_bands)

                if clear_mask is not None:
                    ratio_result[~clear_mask] = np.nan

                # Clean up infinite and NaN values
                ratio_result[np.isinf(ratio_result)] = np.nan
                return ratio_result

            log_messages.append(f"Calculating geological ratio {g_def.acronym} ({g_def.formula_text})...")
            calc_meta = WindowedRasterEngine.process_bands(
                band_paths=band_inputs,
                output_path=full_output_path,
                compute_fn=block_calc,
                output_nodata=-9999.0,
                block_size=block_size,
            )

            product_record = {
                "product_name": g_def.acronym,
                "category": "Geological_Analysis",
                "target_mineral": g_def.target_mineral,
                "formula": g_def.formula_text,
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
                    category="Geological_Analysis",
                    method_name=g_def.acronym,
                    scene_id=scene.metadata.scene_id,
                    is_clip=True,
                    aoi_slug="AOI",
                )
                log_messages.append(f"Clipping {g_def.acronym} with study area polygon...")
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
            tool_name="05_Geological_Analysis",
            parameters={
                "selected_indices": selected_index_ids,
                "apply_qa_mask": apply_qa_mask,
                "has_aoi": aoi_geometry is not None,
            },
            output_products=executed_products,
            qa_summary={
                "requested_count": len(selected_index_ids),
                "executed_count": len(executed_products),
                "skipped_count": len(skipped_indices),
            },
            log_messages=log_messages,
            extra_metadata={"scientific_disclaimer": cls.SCIENTIFIC_DISCLAIMER},
        )

        return {
            "scene_id": scene.metadata.scene_id,
            "results_dir": str(results_dir),
            "run_dir": str(run_dir),
            "executed_products": executed_products,
            "skipped_indices": skipped_indices,
            "log": log_messages,
        }
