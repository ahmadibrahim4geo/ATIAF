"""Coordinate Reference System (CRS) validation, projection intelligence, and reprojection."""

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Union
import pyproj
from rasterio.crs import CRS
from rasterio.warp import calculate_default_transform, reproject, Resampling


@dataclass
class CRSValidationResult:
    is_valid_projected_metre: bool
    is_geographic: bool
    is_projected: bool
    linear_unit_name: Optional[str]
    linear_unit_factor: Optional[float]
    epsg: Optional[int]
    wkt: str
    message: str


class CRSManager:
    """Manages and validates coordinate reference systems per ATIAF Decision D-007:
    enforces projected metre-based coordinate systems, rejects unprojected geographic degrees,
    and supports native host coordinate reference systems without fixed EPSG defaults.
    """

    METRE_UNITS = {"metre", "meter", "m", "international metre", "linear_unit_meters"}

    @classmethod
    def parse_crs(cls, crs_input: Union[str, int, CRS, pyproj.CRS]) -> pyproj.CRS:
        """Parses any standard CRS representation into a pyproj.CRS object."""
        if isinstance(crs_input, pyproj.CRS):
            return crs_input
        if isinstance(crs_input, CRS):
            return pyproj.CRS.from_user_input(crs_input.to_string())
        if isinstance(crs_input, int):
            return pyproj.CRS.from_epsg(crs_input)
        if isinstance(crs_input, str):
            crs_input = crs_input.strip()
            if crs_input.isdigit():
                return pyproj.CRS.from_epsg(int(crs_input))
            return pyproj.CRS.from_user_input(crs_input)
        raise ValueError(f"Unsupported CRS input type: {type(crs_input)}")

    @classmethod
    def validate_projected_metre(cls, crs_input: Union[str, int, CRS, pyproj.CRS]) -> CRSValidationResult:
        """Validates that the given CRS is projected and has linear units in metres.
        Per Decision D-007, geographic (degree) CRSs (such as EPSG:4326) are rejected
        for analysis rasters to prevent distorted metric calculations.
        """
        try:
            crs = cls.parse_crs(crs_input)
        except Exception as e:
            return CRSValidationResult(
                is_valid_projected_metre=False,
                is_geographic=False,
                is_projected=False,
                linear_unit_name=None,
                linear_unit_factor=None,
                epsg=None,
                wkt="",
                message=f"Invalid or unparseable coordinate reference system: {e}",
            )

        is_geo = crs.is_geographic
        is_proj = crs.is_projected
        epsg = crs.to_epsg()
        wkt = crs.to_wkt()

        unit_name = None
        unit_factor = None

        if is_proj and crs.axis_info:
            try:
                axis_0 = crs.axis_info[0]
                unit_name = getattr(axis_0, "unit_name", None)
                unit_factor = getattr(axis_0, "unit_conversion_factor", None)
            except Exception:
                pass

        if is_geo:
            return CRSValidationResult(
                is_valid_projected_metre=False,
                is_geographic=True,
                is_projected=False,
                linear_unit_name=unit_name or "degree",
                linear_unit_factor=unit_factor,
                epsg=epsg,
                wkt=wkt,
                message=(
                    f"Geographic coordinate system rejected ({crs.name}, EPSG:{epsg or 'custom'}). "
                    "Analysis requires a projected coordinate reference system with metre units (e.g., UTM or national projection)."
                ),
            )

        if not is_proj:
            return CRSValidationResult(
                is_valid_projected_metre=False,
                is_geographic=False,
                is_projected=False,
                linear_unit_name=unit_name,
                linear_unit_factor=unit_factor,
                epsg=epsg,
                wkt=wkt,
                message=f"Coordinate system is not projected ({crs.name}).",
            )

        # Check linear unit is in metres
        unit_name_lower = (unit_name or "").lower()
        is_metre = any(m in unit_name_lower for m in cls.METRE_UNITS) or (unit_factor == 1.0)

        if not is_metre:
            return CRSValidationResult(
                is_valid_projected_metre=False,
                is_geographic=False,
                is_projected=True,
                linear_unit_name=unit_name,
                linear_unit_factor=unit_factor,
                epsg=epsg,
                wkt=wkt,
                message=(
                    f"Projected coordinate system has non-metric units ({unit_name or 'unknown'}). "
                    "Analysis requires metre linear units."
                ),
            )

        return CRSValidationResult(
            is_valid_projected_metre=True,
            is_geographic=False,
            is_projected=True,
            linear_unit_name=unit_name or "metre",
            linear_unit_factor=unit_factor or 1.0,
            epsg=epsg,
            wkt=wkt,
            message=f"Valid projected coordinate reference system in metres: {crs.name} (EPSG:{epsg or 'custom'}).",
        )
