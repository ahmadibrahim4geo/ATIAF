"""Windowed block-by-block raster processing engine for large satellite imagery."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.vrt import WarpedVRT
from rasterio.warp import calculate_default_transform
from rasterio.enums import Resampling
from contextlib import ExitStack
import uuid
from atiaf_core.execution_context import RUN_OPTIONS


class WindowedRasterEngine:
    """Processes large raster datasets block-by-block with bounded memory consumption,
    handling NoData values, applying atomic writes, and computing streaming statistics.
    """

    DEFAULT_BLOCK_SIZE = 512

    @classmethod
    def process_bands(
        cls,
        band_paths: Dict[str, Path],
        output_path: Path,
        compute_fn: Callable[[Dict[str, np.ndarray]], np.ndarray],
        output_nodata: float = -9999.0,
        output_dtype: str = "float32",
        block_size: int = DEFAULT_BLOCK_SIZE,
        compress: str = "lzw",
        predictor: int = 3,
    ) -> Dict[str, Any]:
        """Executes a block-by-block computation across aligned input bands.
        
        Args:
            band_paths: Mapping of band identifier (e.g. 'red', 'nir') to file path.
            output_path: Destination path for output GeoTIFF.
            compute_fn: Function that receives {id: 2D numpy array} and returns 2D numpy array.
            output_nodata: Numeric value for masked/nodata output pixels.
            output_dtype: Numpy dtype string for output raster.
            block_size: Window dimension in pixels.
            compress: GeoTIFF compression method (e.g. 'lzw', 'deflate').
            predictor: GeoTIFF predictor (3 for floating point).
        """
        if not band_paths:
            raise ValueError("No input bands provided for computation.")
        band_paths = dict(band_paths)
        run_options = RUN_OPTIONS.get()
        for key, asset in run_options.get('quality_masks', {}).items():
            if key in ('QA_PIXEL', 'SCL', 'QA_RADSAT'):
                band_paths[f'__WORKFLOW_{key}'] = asset.file_path

        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Open reference dataset for grid metadata
        first_key = next(iter(band_paths))
        first_path = band_paths[first_key]

        with rasterio.open(first_path) as ref_ds:
            profile = ref_ds.profile.copy()
            width = ref_ds.width
            height = ref_ds.height
            crs = ref_ds.crs
            transform = ref_ds.transform
            requested_crs = RUN_OPTIONS.get().get('output_crs')
            if requested_crs and crs != rasterio.crs.CRS.from_user_input(requested_crs):
                transform, width, height = calculate_default_transform(
                    crs, requested_crs, width, height, *ref_ds.bounds)
                crs = rasterio.crs.CRS.from_user_input(requested_crs)
            profile.update(crs=crs, transform=transform, width=width, height=height)

        # Update profile for output
        profile.update(
            {
                "driver": "GTiff",
                "count": 1,
                "dtype": output_dtype,
                "nodata": output_nodata,
                "compress": compress,
                "predictor": predictor if "float" in output_dtype else 2,
                "tiled": True,
                "blockxsize": min(block_size, 512),
                "blockysize": min(block_size, 512),
            }
        )

        # Atomic write to temporary file first
        if output_path.exists():
            raise FileExistsError(f'Preserving existing raster: {output_path}')
        tmp_output_path = output_path.parent / f".tmp_{uuid.uuid4().hex}_{output_path.name}"

        # Initialize streaming statistics
        valid_count = 0
        nodata_count = 0
        min_val = float("inf")
        max_val = float("-inf")
        sum_val = 0.0
        sum_sq_val = 0.0

        # Open all input datasets simultaneously
        stack = ExitStack()
        handles = {}

        try:
            for k, p in band_paths.items():
                source = stack.enter_context(rasterio.open(p))
                if not source.crs:
                    raise ValueError(f'Source CRS is unknown: {p}')
                if (source.crs != crs or source.transform != transform or
                        source.width != width or source.height != height):
                    source = stack.enter_context(WarpedVRT(
                        source, crs=crs, transform=transform, width=width, height=height,
                        resampling=Resampling.nearest))
                handles[k] = source
            with rasterio.open(tmp_output_path, "w", **profile) as out_ds:
                # Generate block windows
                for y in range(0, height, block_size):
                    h_win = min(block_size, height - y)
                    for x in range(0, width, block_size):
                        if run_options.get('canceled', lambda: False)():
                            raise InterruptedError('ATIAF run canceled; prior outputs preserved')
                        w_win = min(block_size, width - x)
                        win = Window(x, y, w_win, h_win)

                        # Read window for each band
                        blocks = {}
                        input_invalid = np.zeros((h_win, w_win), dtype=bool)
                        for k, ds in handles.items():
                            data = ds.read(1, window=win)
                            blocks[k] = data
                            if not k.startswith('__'):
                                input_invalid |= ds.read_masks(1, window=win) == 0

                        # Run computation function on the block dictionary
                        result_block = compute_fn(blocks)
                        from atiaf_core.raster.masks import QualityMaskEngine
                        if '__WORKFLOW_QA_PIXEL' in blocks:
                            input_invalid |= ~QualityMaskEngine.get_landsat_c2_clear_mask(blocks['__WORKFLOW_QA_PIXEL'])
                        if '__WORKFLOW_SCL' in blocks:
                            input_invalid |= ~QualityMaskEngine.get_sentinel2_scl_clear_mask(blocks['__WORKFLOW_SCL'])
                        if '__WORKFLOW_QA_RADSAT' in blocks:
                            input_invalid |= blocks['__WORKFLOW_QA_RADSAT'] != 0

                        # Ensure output shape matches window
                        if result_block.shape != (h_win, w_win):
                            raise ValueError(
                                f"compute_fn returned shape {result_block.shape}, expected {(h_win, w_win)}"
                            )

                        # Handle NaNs and infinite values -> set to output_nodata
                        invalid_mask = np.isnan(result_block) | np.isinf(result_block) | input_invalid
                        result_block_clean = np.where(invalid_mask, output_nodata, result_block).astype(output_dtype)

                        # Accumulate streaming statistics
                        valid_pixels = result_block_clean[~invalid_mask]
                        valid_count += int(valid_pixels.size)
                        nodata_count += int(np.count_nonzero(invalid_mask))

                        if valid_pixels.size > 0:
                            b_min = float(np.min(valid_pixels))
                            b_max = float(np.max(valid_pixels))
                            if b_min < min_val:
                                min_val = b_min
                            if b_max > max_val:
                                max_val = b_max
                            sum_val += float(np.sum(valid_pixels))
                            sum_sq_val += float(np.sum(valid_pixels.astype(np.float64) ** 2))

                        # Write block to output raster
                        out_ds.write(result_block_clean, 1, window=win)

        except Exception as e:
            # Clean up temporary file on failure
            if tmp_output_path.exists():
                try:
                    tmp_output_path.unlink()
                except Exception:
                    pass
            raise e
        finally:
            stack.close()
            # Close all open handles
            for ds in handles.values():
                try:
                    ds.close()
                except Exception:
                    pass

        # Atomic swap
        if tmp_output_path.exists():
            tmp_output_path.replace(output_path)

        mean_val = (sum_val / valid_count) if valid_count > 0 else None
        variance = (sum_sq_val / valid_count - (mean_val ** 2)) if valid_count > 0 and mean_val is not None else None
        std_val = float(np.sqrt(max(0.0, variance))) if variance is not None else None

        return {
            "output_path": str(output_path),
            "width": width,
            "height": height,
            "crs": crs.to_string() if crs else None,
            "nodata": output_nodata,
            "valid_pixels": valid_count,
            "nodata_pixels": nodata_count,
            "statistics": {
                "min": min_val if valid_count > 0 else None,
                "max": max_val if valid_count > 0 else None,
                "mean": mean_val,
                "std": std_val,
            },
        }
