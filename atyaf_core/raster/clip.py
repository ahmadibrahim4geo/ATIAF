"""True polygon Area-of-Interest (AOI) clipping and geometry alignment."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pyproj
import rasterio
from rasterio.crs import CRS
from rasterio.mask import mask
from shapely.geometry import mapping, shape
from shapely.ops import transform
import shapely.validation


class PolygonClipEngine:
    """Performs true polygon AOI geometry clipping (not bounding-box envelope)
    on raster datasets, with automatic vector-to-raster CRS transformation.
    """

    @classmethod
    def load_geometry(cls, aoi_input: Any) -> Any:
        """Parses various geometry representations into a Shapely geometry."""
        if hasattr(aoi_input, "__geo_interface__"):
            geom = shape(aoi_input.__geo_interface__)
        elif isinstance(aoi_input, dict):
            geom = shape(aoi_input)
        elif hasattr(aoi_input, "geom_type"):
            geom = aoi_input
        else:
            raise ValueError(f"Unsupported geometry type: {type(aoi_input)}")

        if not geom.is_valid:
            geom = shapely.validation.make_valid(geom)
        return geom

    @classmethod
    def reproject_geometry(
        cls, geom: Any, src_crs_input: Any, dst_crs_input: Any
    ) -> Any:
        """Reprojects a Shapely geometry from source CRS to destination CRS."""
        if src_crs_input is None or dst_crs_input is None:
            return geom

        src_crs = pyproj.CRS.from_user_input(src_crs_input)
        dst_crs = pyproj.CRS.from_user_input(dst_crs_input)

        if src_crs == dst_crs:
            return geom

        transformer = pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)
        return transform(transformer.transform, geom)

    @classmethod
    def clip_raster_file(
        cls,
        src_raster_path: Path,
        dst_raster_path: Path,
        aoi_geometry: Any,
        aoi_crs: Optional[Any] = None,
        crop: bool = True,
        nodata: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Clips a raster GeoTIFF on disk using a true polygon geometry.
        Automatically reprojects the geometry to the raster CRS if needed,
        crops the bounding extent, and updates the affine geotransform.
        """
        src_raster_path = Path(src_raster_path).resolve()
        dst_raster_path = Path(dst_raster_path).resolve()
        dst_raster_path.parent.mkdir(parents=True, exist_ok=True)

        geom = cls.load_geometry(aoi_geometry)

        with rasterio.open(src_raster_path) as src:
            target_crs = src.crs

            # Transform geometry if AOI CRS is specified and different
            if aoi_crs is not None:
                geom = cls.reproject_geometry(geom, aoi_crs, target_crs)

            geo_shapes = [mapping(geom)]
            out_nodata = nodata if nodata is not None else (src.nodata if src.nodata is not None else np.nan)

            out_image, out_transform = mask(
                src,
                geo_shapes,
                crop=crop,
                nodata=out_nodata,
                filled=True,
            )
            out_meta = src.meta.copy()

            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                    "nodata": out_nodata,
                }
            )

            # Atomic write via temporary file
            tmp_path = dst_raster_path.parent / f".tmp_{dst_raster_path.name}"
            with rasterio.open(tmp_path, "w", **out_meta) as dst:
                dst.write(out_image)

            if tmp_path.exists():
                tmp_path.replace(dst_raster_path)

            return {
                "output_path": str(dst_raster_path),
                "width": out_image.shape[2],
                "height": out_image.shape[1],
                "crs": target_crs.to_string() if target_crs else None,
                "nodata": out_nodata,
                "bounds": [
                    out_transform[2],
                    out_transform[5] + out_transform[4] * out_image.shape[1],
                    out_transform[2] + out_transform[0] * out_image.shape[2],
                    out_transform[5],
                ],
            }
