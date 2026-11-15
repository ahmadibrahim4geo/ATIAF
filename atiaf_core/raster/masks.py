"""Pixel-level Quality Assessment (QA) masking for satellite imagery."""

from typing import Optional, Set
import numpy as np


class QualityMaskEngine:
    """Interprets and applies sensor QA bitmasks and categorical masks (Landsat C2 QA_PIXEL, Sentinel-2 SCL)."""

    # USGS Landsat Collection 2 QA_PIXEL Bit Definitions
    LANDSAT_BIT_FILL = 0
    LANDSAT_BIT_DILATED_CLOUD = 1
    LANDSAT_BIT_CIRRUS = 2
    LANDSAT_BIT_CLOUD = 3
    LANDSAT_BIT_CLOUD_SHADOW = 4
    LANDSAT_BIT_SNOW = 5
    LANDSAT_BIT_CLEAR = 6
    LANDSAT_BIT_WATER = 7

    # Copernicus Sentinel-2 SCL (Scene Classification Layer) Class Codes
    S2_SCL_NODATA = 0
    S2_SCL_SATURATED = 1
    S2_SCL_DARK_AREA = 2
    S2_SCL_CLOUD_SHADOW = 3
    S2_SCL_VEGETATION = 4
    S2_SCL_BARE_SOIL = 5
    S2_SCL_WATER = 6
    S2_SCL_UNCLASSIFIED = 7
    S2_SCL_CLOUD_MEDIUM_PROB = 8
    S2_SCL_CLOUD_HIGH_PROB = 9
    S2_SCL_THIN_CIRRUS = 10
    S2_SCL_SNOW = 11

    @classmethod
    def get_landsat_c2_clear_mask(
        cls,
        qa_array: np.ndarray,
        mask_dilated_cloud: bool = True,
        mask_cirrus: bool = True,
        mask_cloud: bool = True,
        mask_shadow: bool = True,
        mask_snow: bool = True,
    ) -> np.ndarray:
        """Returns boolean mask where True = clear/valid pixel, False = masked out.
        qa_array is uint16 array of Landsat Collection 2 QA_PIXEL.
        """
        # Pixel is invalid if fill bit is set
        is_fill = (qa_array & (1 << cls.LANDSAT_BIT_FILL)) > 0
        invalid_mask = is_fill.copy()

        if mask_dilated_cloud:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_DILATED_CLOUD)) > 0
        if mask_cirrus:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CIRRUS)) > 0
        if mask_cloud:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CLOUD)) > 0
        if mask_shadow:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CLOUD_SHADOW)) > 0
        if mask_snow:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_SNOW)) > 0

        # Valid pixels are NOT invalid
        return ~invalid_mask

    @classmethod
    def get_sentinel2_scl_clear_mask(
        cls,
        scl_array: np.ndarray,
        mask_cloud_shadow: bool = True,
        mask_clouds: bool = True,
        mask_cirrus: bool = True,
        mask_snow: bool = True,
        mask_saturated: bool = True,
        custom_invalid_classes: Optional[Set[int]] = None,
    ) -> np.ndarray:
        """Returns boolean mask where True = clear/valid pixel, False = masked out.
        scl_array is uint8 array of Sentinel-2 Scene Classification Layer (SCL).
        """
        invalid_classes = {cls.S2_SCL_NODATA}
        if mask_saturated:
            invalid_classes.add(cls.S2_SCL_SATURATED)
        if mask_cloud_shadow:
            invalid_classes.add(cls.S2_SCL_CLOUD_SHADOW)
        if mask_clouds:
            invalid_classes.add(cls.S2_SCL_CLOUD_MEDIUM_PROB)
            invalid_classes.add(cls.S2_SCL_CLOUD_HIGH_PROB)
        if mask_cirrus:
            invalid_classes.add(cls.S2_SCL_THIN_CIRRUS)
        if mask_snow:
            invalid_classes.add(cls.S2_SCL_SNOW)

        if custom_invalid_classes:
            invalid_classes.update(custom_invalid_classes)

        # Vectorized isin
        is_invalid = np.isin(scl_array, list(invalid_classes))
        return ~is_invalid

    @classmethod
    def apply_valid_range_and_nodata(
        cls,
        data: np.ndarray,
        valid_min: Optional[float] = None,
        valid_max: Optional[float] = None,
        nodata: Optional[float] = None,
        external_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Applies valid min/max ranges, NoData, and optional external QA mask.
        Returns a float array with masked/invalid pixels set to np.nan.
        """
        float_data = data.astype(np.float32, copy=True)

        if nodata is not None and not np.isnan(nodata):
            float_data[data == nodata] = np.nan

        if valid_min is not None:
            float_data[float_data < valid_min] = np.nan

        if valid_max is not None:
            float_data[float_data > valid_max] = np.nan

        if external_mask is not None:
            # external_mask is True for valid, False for invalid
            float_data[~external_mask] = np.nan

        return float_data
