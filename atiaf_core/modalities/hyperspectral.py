# -*- coding: utf-8 -*-
"""Hyperspectral Modality Engine, Cube Gating & Mineral Analysis.

Provides Spectral Angle Mapper (SAM), continuum-removed diagnostic absorption
feature depth analysis, and Level-2 surface reflectance cube gating.
References:
- Kruse, F. A., et al. (1993). The Spectral Image Processing System (SIPS). Remote Sensing of Environment.
- Clark, R. N., & Roush, T. L. (1984). Reflectance Spectroscopy: Quantitative Analysis Techniques. JGR.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from atiaf_core.modalities.models import (
    HyperspectralCubeMetadata,
    ModalityCapabilityError,
    SensorModality,
)


class HyperspectralEngine:
    """Scientific processor for contiguous spaceborne hyperspectral datacubes (EnMAP, PRISMA, EMIT)."""

    # Diagnostic mineral absorption wavelength regions (center_nm, left_shoulder_nm, right_shoulder_nm)
    DIAGNOSTIC_FEATURES: Dict[str, Tuple[float, float, float]] = {
        "AL_OH_2200": (2205.0, 2160.0, 2240.0),    # Kaolinite, Illite, Alunite, Muscovite
        "MG_OH_2350": (2345.0, 2300.0, 2385.0),    # Chlorite, Talc, Epidote, Calcite/Dolomite
        "FE3_900": (900.0, 750.0, 1050.0),         # Iron oxides (Goethite, Hematite)
        "WATER_1400": (1400.0, 1340.0, 1460.0),    # Clay bound water / OH
        "CELLULOSE_2100": (2100.0, 2050.0, 2150.0) # Non-photosynthetic vegetation / dry cellulose
    }

    @staticmethod
    def assert_l2_surface_reflectance(
        scene_id: str,
        instrument: str,
        product_level: str,
        requested_tool: str = "Geological_Analysis",
    ) -> None:
        """Enforces that hyperspectral mineral/spectral library analysis only operates
        on calibrated Level-2 Surface Reflectance datacubes (e.g., EnMAP L2A, PRISMA L2D).
        
        Rejects Top-of-Atmosphere (TOA) L1 data with explicit scientific rationale.
        """
        is_l2 = any(l2_tag in product_level.upper() for l2_tag in ["L2", "L2A", "L2D", "SURFACE", "BOA"])
        if not is_l2:
            reason_en = (
                f"Hyperspectral sensor '{instrument}' product is '{product_level}'. "
                "Mineral spectral unmixing and absorption feature analysis strictly require Level-2 "
                "surface reflectance (BOA) cubes. Uncalibrated TOA radiance or TOA reflectance "
                "is contaminated by atmospheric water vapor and aerosols, invalidating spectral library matching."
            )
            reason_ar = (
                f"المستشعر الفائق الطيفية '{instrument}' يقدم منتج بمستوى '{product_level}'. "
                "تحليل المعادن ومطابقة المكتبات الطيفية يتطلب حصراً مكعبات انعكاسية سطحية مصححة جوياً (Level-2 BOA). "
                "بيانات قمة الغلاف الجوي (TOA) غير المصححة تشوه معالم الامتصاص الطيفي بفعل بخار الماء والغازات الجوية."
            )
            raise ModalityCapabilityError(
                scene_id=scene_id,
                detected_modality=SensorModality.HYPERSPECTRAL,
                requested_tool=requested_tool,
                reason_en=reason_en,
                reason_ar=reason_ar,
            )

    @staticmethod
    def spectral_angle_mapper(
        cube_pixels: np.ndarray,
        reference_spectrum: np.ndarray,
        eps: float = 1e-8,
    ) -> np.ndarray:
        """Calculates Spectral Angle Mapper (SAM) angle between image pixels and a reference library spectrum.
        
        Args:
            cube_pixels: Array of shape (bands, height, width) or (bands, N_pixels).
            reference_spectrum: Array of shape (bands,).
        
        Returns:
            Angle in radians (0 to pi). Smaller angles indicate higher spectral similarity.
            
            alpha = arccos( (t . r) / (||t|| * ||r||) )
        """
        ref = np.asarray(reference_spectrum, dtype=np.float64)
        ref_norm = np.linalg.norm(ref)
        if ref_norm < eps:
            raise ValueError("Reference spectrum norm is effectively zero.")

        orig_shape = cube_pixels.shape
        if cube_pixels.ndim == 3:
            bands, h, w = orig_shape
            flat_pixels = cube_pixels.reshape(bands, -1).astype(np.float64)
        else:
            bands, n = orig_shape
            h, w = 1, n
            flat_pixels = cube_pixels.astype(np.float64)

        # Dot product: sum(t_i * r_i) along band axis in float64 for numerical precision
        dot_product = np.dot(ref, flat_pixels)

        # Norm of each pixel vector: sqrt(sum(t_i^2))
        pixel_norm = np.linalg.norm(flat_pixels, axis=0)
        denom = pixel_norm * ref_norm

        valid = denom > eps
        cos_alpha = np.full_like(dot_product, np.nan, dtype=np.float64)
        np.divide(dot_product, denom, out=cos_alpha, where=valid)
        np.clip(cos_alpha, -1.0, 1.0, out=cos_alpha, where=valid)

        angles_rad = np.arccos(cos_alpha).astype(np.float32)
        if cube_pixels.ndim == 3:
            return angles_rad.reshape(h, w)
        return angles_rad

    @staticmethod
    def absorption_feature_depth(
        cube: np.ndarray,
        wavelengths_nm: List[float],
        feature_name: str = "AL_OH_2200",
        custom_triplet: Optional[Tuple[float, float, float]] = None,
    ) -> np.ndarray:
        """Calculates continuum-removed absorption feature depth:
        
            Depth = 1 - (R_center / R_continuum)
        
        Args:
            cube: Array of shape (bands, height, width).
            wavelengths_nm: List of band center wavelengths in nanometers.
            feature_name: Diagnostic feature identifier from DIAGNOSTIC_FEATURES.
            custom_triplet: Optional (center_nm, left_nm, right_nm) override.
        """
        if custom_triplet is not None:
            c_nm, l_nm, r_nm = custom_triplet
        elif feature_name in HyperspectralEngine.DIAGNOSTIC_FEATURES:
            c_nm, l_nm, r_nm = HyperspectralEngine.DIAGNOSTIC_FEATURES[feature_name]
        else:
            raise ValueError(f"Unknown diagnostic absorption feature: '{feature_name}'")

        meta = HyperspectralCubeMetadata(num_bands=len(wavelengths_nm), wavelengths_nm=wavelengths_nm)
        idx_c = meta.find_closest_band_index(c_nm, max_delta_nm=30.0)
        idx_l = meta.find_closest_band_index(l_nm, max_delta_nm=40.0)
        idx_r = meta.find_closest_band_index(r_nm, max_delta_nm=40.0)

        if idx_c is None or idx_l is None or idx_r is None:
            raise ValueError(
                f"Cube wavelengths do not cover feature '{feature_name}' "
                f"({l_nm}nm - {c_nm}nm - {r_nm}nm). Available range: "
                f"[{min(wavelengths_nm):.1f}nm, {max(wavelengths_nm):.1f}nm]"
            )

        wl_c = wavelengths_nm[idx_c]
        wl_l = wavelengths_nm[idx_l]
        wl_r = wavelengths_nm[idx_r]

        r_c = cube[idx_c].astype(np.float32)
        r_l = cube[idx_l].astype(np.float32)
        r_r = cube[idx_r].astype(np.float32)

        # Linear continuum: R_cont = R_l + (wl_c - wl_l) / (wl_r - wl_l) * (R_r - R_l)
        slope = (r_r - r_l) / max(1e-6, (wl_r - wl_l))
        r_cont = r_l + slope * (wl_c - wl_l)

        valid = ~np.isnan(r_c) & ~np.isnan(r_cont) & (r_cont > 1e-6)
        depth = np.full_like(r_c, np.nan, dtype=np.float32)

        # Depth = 1 - (R_center / R_continuum)
        ratio = np.divide(r_c, r_cont, out=np.ones_like(r_c), where=valid)
        depth = np.where(valid, np.clip(1.0 - ratio, 0.0, 1.0), np.nan)
        return depth
