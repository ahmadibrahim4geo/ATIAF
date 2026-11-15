# -*- coding: utf-8 -*-
"""SAR (Synthetic Aperture Radar) Modality Engine, Gating & Calibration.

Enforces Specification Section 2: 'Never route SAR through optical equations'.
Provides SAR calibration, polarimetric ratios (cross-polarization ratio, RVI),
linear-to-decibel scaling, and speckle reduction specifications.
"""

from typing import Optional
import numpy as np

from atiaf_core.modalities.models import (
    ModalityCapabilityError,
    PolarizationRole,
    SARCalibrationType,
    SensorModality,
)


class SAREngine:
    """Scientific processor and gating engine for SAR radar imagery."""

    @staticmethod
    def assert_optical_compatibility(
        scene_id: str,
        instrument: str,
        requested_tool: str = "Spectral_Indices",
    ) -> None:
        """Strictly blocks routing SAR products through optical or thermal equations.
        
        Per Specification Section 2:
        'Never route SAR through optical equations. Dedicated SAR calibration/coherence/backscatter
        workflow; never route SAR to optical equations.'
        """
        reason_en = (
            f"Sensor '{instrument}' is a Synthetic Aperture Radar (SAR) measuring microwave backscatter "
            f"(sigma-naught/gamma-naught). Tool '{requested_tool}' requires optical surface reflectance "
            "or thermal radiance. Routing SAR into optical spectral equations is scientifically invalid (Specification Section 2)."
        )
        reason_ar = (
            f"المستشعر '{instrument}' هو رادار فتحة اصطناعية (SAR) يقيس التشتت الراداري المرتد (Backscatter). "
            f"الأداة المطلوبة '{requested_tool}' تتطلب انعكاسية بصرية سطحية أو إشعاعية حرارية. "
            "تطبيق معادلات المؤشرات البصرية على بيانات الرادار غير علمي ومحظور تماماً (البند 2 من المواصفات)."
        )
        raise ModalityCapabilityError(
            scene_id=scene_id,
            detected_modality=SensorModality.SAR_RADAR,
            requested_tool=requested_tool,
            reason_en=reason_en,
            reason_ar=reason_ar,
        )

    @staticmethod
    def linear_to_db(
        arr: np.ndarray,
        eps: float = 1e-7,
        min_db: float = -40.0,
        max_db: float = 15.0,
    ) -> np.ndarray:
        """Converts linear radar backscatter power (intensity) to decibels (dB):
        
            dB = 10 * log10(max(arr, eps))
        
        Clips to realistic dynamic range [-40 dB, +15 dB] and preserves NaNs.
        """
        out = np.full_like(arr, np.nan, dtype=np.float32)
        valid = ~np.isnan(arr) & (arr > 0)
        if np.any(valid):
            linear_clamped = np.maximum(arr[valid], eps)
            db_vals = 10.0 * np.log10(linear_clamped)
            out[valid] = np.clip(db_vals, min_db, max_db)
        return out

    @staticmethod
    def db_to_linear(arr: np.ndarray) -> np.ndarray:
        """Converts backscatter decibels (dB) back to linear power:
        
            linear = 10^(dB / 10)
        """
        out = np.full_like(arr, np.nan, dtype=np.float32)
        valid = ~np.isnan(arr)
        if np.any(valid):
            out[valid] = np.power(10.0, arr[valid] / 10.0)
        return out

    @staticmethod
    def cross_polarization_ratio(
        vh: np.ndarray,
        vv: np.ndarray,
        in_db: bool = False,
        eps: float = 1e-7,
    ) -> np.ndarray:
        """Calculates cross-polarization ratio (VH / VV).
        
        Useful for forest biomass, soil moisture decoupling, and structural roughness.
        If in_db=True, computes (VH_dB - VV_dB).
        If in_db=False, computes (VH_linear / VV_linear).
        """
        if in_db:
            return np.where(~np.isnan(vh) & ~np.isnan(vv), vh - vv, np.nan)

        denom = np.where(np.abs(vv) < eps, np.nan, vv)
        ratio = np.divide(vh, denom, out=np.full_like(vh, np.nan, dtype=np.float32), where=~np.isnan(denom))
        return ratio

    @staticmethod
    def radar_vegetation_index(
        vh_linear: np.ndarray,
        vv_linear: np.ndarray,
        eps: float = 1e-7,
    ) -> np.ndarray:
        """Computes dual-pol Radar Vegetation Index (RVI) for Sentinel-1:
        
            RVI = (4 * VH) / (VV + VH)
        
        Reference: Kim, Y., & van Zyl, J. J. (2009). A Time-Series Approach to Estimate Soil
        Moisture Using Polarimetric Radar Data. IEEE TGRS.
        RVI ranges between 0 (smooth bare soil / calm water) and ~1 (dense vegetation canopy).
        """
        denom = vv_linear + vh_linear
        valid = ~np.isnan(denom) & (denom > eps)

        rvi = np.full_like(vh_linear, np.nan, dtype=np.float32)
        np.divide(4.0 * vh_linear, denom, out=rvi, where=valid)
        np.clip(rvi, 0.0, 1.2, out=rvi, where=valid)
        return rvi

    @staticmethod
    def apply_lee_filter(
        arr: np.ndarray,
        window_size: int = 5,
        num_looks: int = 1,
    ) -> np.ndarray:
        """Applies spatial Lee speckle filter to an intensity image.
        
        Reference: Lee, J. S. (1980). Digital image enhancement and noise filtering
        by use of local statistics. IEEE PAMI.
        """
        def _uniform(img: np.ndarray, s: int) -> np.ndarray:
            try:
                from scipy.ndimage import uniform_filter
                return uniform_filter(img, size=s)
            except ImportError:
                pad = s // 2
                padded = np.pad(img, pad_width=pad, mode="reflect")
                integral = np.pad(padded.cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)), mode="constant")
                y2, x2 = img.shape
                sum_box = (
                    integral[s : s + y2, s : s + x2]
                    - integral[0:y2, s : s + x2]
                    - integral[s : s + y2, 0:x2]
                    + integral[0:y2, 0:x2]
                )
                return (sum_box / (s * s)).astype(np.float32)

        valid_mask = ~np.isnan(arr) & (arr > 0)
        filled = np.where(valid_mask, arr, 0.0)

        # Local mean
        local_mean = _uniform(filled, window_size)
        # Local variance = mean(x^2) - mean(x)^2
        local_sq_mean = _uniform(filled ** 2, window_size)
        local_var = np.maximum(0.0, local_sq_mean - local_mean ** 2)

        # Theoretical noise variance for multi-look intensity: sigma_v^2 = 1 / num_looks
        noise_var = 1.0 / max(1, num_looks)

        # Weight W = max(0, (var - mean^2 * noise_var) / (var * (1 + noise_var)))
        denom = local_var * (1.0 + noise_var)
        w = np.zeros_like(arr, dtype=np.float32)
        calc_w = (local_var - (local_mean ** 2) * noise_var) / np.maximum(denom, 1e-8)
        w = np.clip(calc_w, 0.0, 1.0)

        # Filtered pixel = local_mean + W * (arr - local_mean)
        filtered = local_mean + w * (arr - local_mean)
        return np.where(valid_mask, filtered, np.nan)
