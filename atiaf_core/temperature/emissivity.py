"""Land Surface Emissivity (LSE) estimation models based on NDVI thresholds."""

from typing import Tuple
import numpy as np


class EmissivityEngine:
    """Computes Land Surface Emissivity (LSE / epsilon) and Fractional Vegetation Cover (Pv)
    using the validated NDVI Thresholds Method (Sobrino et al., 2004).
    """

    DEFAULT_NDVI_SOIL = 0.20
    DEFAULT_NDVI_VEG = 0.50
    DEFAULT_EMISSIVITY_SOIL = 0.970
    DEFAULT_EMISSIVITY_VEG = 0.985
    DEFAULT_EMISSIVITY_WATER = 0.992
    DEFAULT_CAVITY_TERM = 0.005

    @classmethod
    def calc_fractional_vegetation_cover(
        cls,
        ndvi: np.ndarray,
        ndvi_soil: float = DEFAULT_NDVI_SOIL,
        ndvi_veg: float = DEFAULT_NDVI_VEG,
    ) -> np.ndarray:
        """Calculates Fractional Vegetation Cover (Pv):
        Pv = ((NDVI - NDVI_soil) / (NDVI_veg - NDVI_soil)) ** 2, clamped to [0.0, 1.0].
        """
        denom = ndvi_veg - ndvi_soil
        if denom == 0:
            denom = 0.0001

        ratio = (ndvi - ndvi_soil) / denom
        ratio_clamped = np.clip(ratio, 0.0, 1.0)
        pv = ratio_clamped ** 2
        return np.where(np.isnan(ndvi), np.nan, pv)

    @classmethod
    def calc_land_surface_emissivity(
        cls,
        ndvi: np.ndarray,
        ndvi_soil: float = DEFAULT_NDVI_SOIL,
        ndvi_veg: float = DEFAULT_NDVI_VEG,
        emiss_soil: float = DEFAULT_EMISSIVITY_SOIL,
        emiss_veg: float = DEFAULT_EMISSIVITY_VEG,
        emiss_water: float = DEFAULT_EMISSIVITY_WATER,
        cavity: float = DEFAULT_CAVITY_TERM,
    ) -> np.ndarray:
        """Calculates Land Surface Emissivity (LSE) from NDVI array:
        - Water (NDVI < 0): epsilon = emiss_water (0.992)
        - Pure soil (NDVI < ndvi_soil): epsilon = emiss_soil (0.970)
        - Pure vegetation (NDVI > ndvi_veg): epsilon = emiss_veg (0.985)
        - Mixed pixels (ndvi_soil <= NDVI <= ndvi_veg): epsilon = emiss_veg * Pv + emiss_soil * (1 - Pv) + cavity
        """
        pv = cls.calc_fractional_vegetation_cover(ndvi, ndvi_soil, ndvi_veg)
        emiss = np.full_like(ndvi, np.nan, dtype=np.float32)

        # Valid mask
        valid = ~np.isnan(ndvi)

        # Water
        water_mask = valid & (ndvi < 0.0)
        emiss[water_mask] = emiss_water

        # Pure Soil
        soil_mask = valid & (ndvi >= 0.0) & (ndvi < ndvi_soil)
        emiss[soil_mask] = emiss_soil

        # Pure Vegetation
        veg_mask = valid & (ndvi > ndvi_veg)
        emiss[veg_mask] = emiss_veg

        # Mixed Pixels
        mixed_mask = valid & (ndvi >= ndvi_soil) & (ndvi <= ndvi_veg)
        emiss[mixed_mask] = (
            emiss_veg * pv[mixed_mask]
            + emiss_soil * (1.0 - pv[mixed_mask])
            + cavity
        )

        return emiss
