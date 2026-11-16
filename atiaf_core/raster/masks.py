"""Pixel-level Quality Assessment (QA) masking and data integrity for satellite imagery."""

from typing import Optional, Set
import numpy as np
from atiaf_core.execution_context import RUN_OPTIONS


class QualityMaskEngine:
    """Interprets and applies sensor QA bitmasks and categorical masks (Landsat C2 QA_PIXEL, Sentinel-2 SCL)
    with support for intelligent granular modes (Arid / Cloud Only, Full Strict, Water Protected, None).
    """

    LEGACY_SCHEMAS = ('BQA_PRECOLLECTION', 'BQA_C1_L8', 'BQA_C1_TM', 'PIXEL_QA_C1_L8', 'PIXEL_QA_C1_TM')

    # Standard QA Modes
    MODE_CLOUD_ONLY_ARID = 'Cloud_Only_Arid'
    MODE_FULL_STRICT = 'Full_Strict'
    MODE_WATER_PROTECTED = 'Water_Protected'
    MODE_NONE = 'None'

    @classmethod
    def resolve_mode(cls, explicit_mode: Optional[str] = None) -> Optional[str]:
        """Resolves active QA mask mode from explicit argument or RUN_OPTIONS context.
        Returns None if no mode was set and RUN_OPTIONS is empty (standard strict unit test behavior).
        """
        if explicit_mode is not None:
            return explicit_mode
        opts = RUN_OPTIONS.get() or {}
        user_opts = opts.get('user_options') or {}
        mode = opts.get('qa_mask_mode') or user_opts.get('qa_mask_mode')
        if not mode and opts.get('quality_masks') is not None and len(opts.get('quality_masks', {})) == 0:
            return cls.MODE_NONE
        return mode

    @classmethod
    def clear_for_schema(cls, qa, schema, mode: Optional[str] = None):
        """Explicit generation-bound QA; never decode a BQA by filename alone."""
        resolved_mode = cls.resolve_mode(mode)
        if resolved_mode in (cls.MODE_NONE, 'none'):
            q = np.asarray(qa, dtype='uint16')
            return (q & 1) == 0 if schema.startswith(('QA_', 'BQA_', 'PIXEL_QA_')) else q != 0

        q = np.asarray(qa, dtype='uint16')
        if schema == 'QA_PIXEL':
            return cls.get_landsat_c2_clear_mask(q, mode=resolved_mode)
        if schema == 'SCL':
            return cls.get_sentinel2_scl_clear_mask(q, mode=resolved_mode)
        if schema == 'QA_RADSAT':
            return q == 0
        if schema == 'BQA_PRECOLLECTION':
            clear = (q & 7) == 0
            if resolved_mode not in (cls.MODE_CLOUD_ONLY_ARID, 'arid', 'cloud_only'):
                for shift in (10, 12, 14):
                    clear &= ((q >> shift) & 3) < 2
            return clear
        if schema in ('BQA_C1_L8', 'BQA_C1_TM'):
            clear = (q & 31) == 0  # fill, dropped/terrain, saturation pair and cloud flag
            if resolved_mode not in (cls.MODE_CLOUD_ONLY_ARID, 'arid', 'cloud_only'):
                for shift in ((5, 7, 9, 11) if schema.endswith('L8') else (5, 7, 9)):
                    clear &= ((q >> shift) & 3) < 2
            return clear
        if schema in ('PIXEL_QA_C1_L8', 'PIXEL_QA_C1_TM'):
            clear = (q & ((1 << 0) | (1 << 3) | (1 << 4) | (1 << 5))) == 0
            if resolved_mode not in (cls.MODE_CLOUD_ONLY_ARID, 'arid', 'cloud_only'):
                clear &= ((q >> 6) & 3) < 2
                if schema.endswith('L8'):
                    clear &= ((q >> 8) & 3) < 2
            return clear
        raise ValueError('Unknown quality mask schema: ' + schema)

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
        mode: Optional[str] = None,
        mask_dilated_cloud: Optional[bool] = None,
        mask_cirrus: Optional[bool] = None,
        mask_cloud: Optional[bool] = None,
        mask_shadow: Optional[bool] = None,
        mask_snow: Optional[bool] = None,
    ) -> np.ndarray:
        """Returns boolean mask where True = clear/valid pixel, False = masked out.
        qa_array is uint16 array of Landsat Collection 2 QA_PIXEL.
        In Cloud_Only_Arid mode, cirrus, terrain shadows, and dilation false-positives
        are bypassed to protect desert mountains and river water bodies.
        """
        resolved_mode = cls.resolve_mode(mode)

        # Base fill bit check
        is_fill = (qa_array & (1 << cls.LANDSAT_BIT_FILL)) > 0
        if resolved_mode in (cls.MODE_NONE, 'none'):
            return ~is_fill

        # Determine defaults based on mode
        if resolved_mode in (cls.MODE_CLOUD_ONLY_ARID, 'arid', 'cloud_only'):
            m_dilated = False if mask_dilated_cloud is None else mask_dilated_cloud
            m_cirrus = False if mask_cirrus is None else mask_cirrus
            m_cloud = True if mask_cloud is None else mask_cloud
            m_shadow = False if mask_shadow is None else mask_shadow
            m_snow = True if mask_snow is None else mask_snow
        elif resolved_mode in (cls.MODE_WATER_PROTECTED, 'water_protected'):
            m_dilated = True if mask_dilated_cloud is None else mask_dilated_cloud
            m_cirrus = False if mask_cirrus is None else mask_cirrus
            m_cloud = True if mask_cloud is None else mask_cloud
            m_shadow = True if mask_shadow is None else mask_shadow
            m_snow = True if mask_snow is None else mask_snow
        else:  # Strict default when mode is Full_Strict or None (unspecified test default)
            m_dilated = True if mask_dilated_cloud is None else mask_dilated_cloud
            m_cirrus = True if mask_cirrus is None else mask_cirrus
            m_cloud = True if mask_cloud is None else mask_cloud
            m_shadow = True if mask_shadow is None else mask_shadow
            m_snow = True if mask_snow is None else mask_snow

        invalid_mask = is_fill.copy()
        if m_dilated:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_DILATED_CLOUD)) > 0
        if m_cirrus:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CIRRUS)) > 0
        if m_cloud:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CLOUD)) > 0
        if m_shadow:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_CLOUD_SHADOW)) > 0
        if m_snow:
            invalid_mask |= (qa_array & (1 << cls.LANDSAT_BIT_SNOW)) > 0

        # In water protected mode, unmask water pixels that are NOT real clouds
        if resolved_mode in (cls.MODE_WATER_PROTECTED, 'water_protected'):
            is_water = (qa_array & (1 << cls.LANDSAT_BIT_WATER)) > 0
            is_cloud = (qa_array & (1 << cls.LANDSAT_BIT_CLOUD)) > 0
            invalid_mask &= ~(is_water & ~is_cloud)

        return ~invalid_mask

    @classmethod
    def get_sentinel2_scl_clear_mask(
        cls,
        scl_array: np.ndarray,
        mode: Optional[str] = None,
        mask_cloud_shadow: Optional[bool] = None,
        mask_clouds: Optional[bool] = None,
        mask_cirrus: Optional[bool] = None,
        mask_snow: Optional[bool] = None,
        mask_saturated: Optional[bool] = None,
        custom_invalid_classes: Optional[Set[int]] = None,
    ) -> np.ndarray:
        """Returns boolean mask where True = clear/valid pixel, False = masked out.
        scl_array is uint8 array of Sentinel-2 Scene Classification Layer (SCL).
        """
        resolved_mode = cls.resolve_mode(mode)
        if resolved_mode in (cls.MODE_NONE, 'none'):
            return scl_array != cls.S2_SCL_NODATA

        if resolved_mode in (cls.MODE_CLOUD_ONLY_ARID, 'arid', 'cloud_only'):
            m_shadow = False if mask_cloud_shadow is None else mask_cloud_shadow
            m_clouds = True if mask_clouds is None else mask_clouds
            m_cirrus = False if mask_cirrus is None else mask_cirrus
            m_snow = True if mask_snow is None else mask_snow
            m_sat = True if mask_saturated is None else mask_saturated
        elif resolved_mode in (cls.MODE_WATER_PROTECTED, 'water_protected'):
            m_shadow = False if mask_cloud_shadow is None else mask_cloud_shadow
            m_clouds = True if mask_clouds is None else mask_clouds
            m_cirrus = False if mask_cirrus is None else mask_cirrus
            m_snow = True if mask_snow is None else mask_snow
            m_sat = True if mask_saturated is None else mask_saturated
        else:  # Full strict default
            m_shadow = True if mask_cloud_shadow is None else mask_cloud_shadow
            m_clouds = True if mask_clouds is None else mask_clouds
            m_cirrus = True if mask_cirrus is None else mask_cirrus
            m_snow = True if mask_snow is None else mask_snow
            m_sat = True if mask_saturated is None else mask_saturated

        invalid_classes = {cls.S2_SCL_NODATA}
        if m_sat:
            invalid_classes.add(cls.S2_SCL_SATURATED)
        if m_shadow:
            invalid_classes.add(cls.S2_SCL_CLOUD_SHADOW)
        if m_clouds:
            invalid_classes.add(cls.S2_SCL_CLOUD_MEDIUM_PROB)
            invalid_classes.add(cls.S2_SCL_CLOUD_HIGH_PROB)
        if m_cirrus:
            invalid_classes.add(cls.S2_SCL_THIN_CIRRUS)
        if m_snow:
            invalid_classes.add(cls.S2_SCL_SNOW)

        if custom_invalid_classes:
            invalid_classes.update(custom_invalid_classes)

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
        clamp_negative: bool = True,
        min_positive_epsilon: float = 0.0001,
    ) -> np.ndarray:
        """Applies valid min/max ranges, NoData, external QA mask, and safe negative reflectance clamping.
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
            float_data[~external_mask] = np.nan

        if clamp_negative:
            valid = np.isfinite(float_data)
            float_data[valid & (float_data < min_positive_epsilon)] = min_positive_epsilon

        return float_data
