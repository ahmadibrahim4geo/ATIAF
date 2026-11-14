# -*- coding: utf-8 -*-
"""Data models, modality types, and exception classes for advanced sensor modalities."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SensorModality(str, Enum):
    """Core sensor modality classification per Specification Section 2 and 5."""
    MULTISPECTRAL = "multispectral"
    THERMAL = "thermal"
    HYPERSPECTRAL = "hyperspectral"
    SAR_RADAR = "sar_radar"


class PolarizationRole(str, Enum):
    """SAR polarimetric channel roles."""
    VV = "VV"
    VH = "VH"
    HH = "HH"
    HV = "HV"


class SARCalibrationType(str, Enum):
    """Radar radiometric calibration reference targets."""
    SIGMA0 = "sigma0"  # Ground area backscatter (σ°)
    GAMMA0 = "gamma0"  # Illuminated area backscatter (γ°)
    BETA0 = "beta0"    # Slant range backscatter (β°)


class ModalityCapabilityError(ValueError):
    """Exception raised when an algorithm or tool is applied to an incompatible sensor modality.
    
    Strictly prevents cross-modality misuse, such as routing SAR through optical reflectance
    or calculating surface temperature from sensors without calibrated thermal measurements.
    """

    def __init__(
        self,
        scene_id: str,
        detected_modality: SensorModality,
        requested_tool: str,
        reason_en: str,
        reason_ar: str,
    ):
        self.scene_id = scene_id
        self.detected_modality = detected_modality
        self.requested_tool = requested_tool
        self.reason_en = reason_en
        self.reason_ar = reason_ar
        super().__init__(f"[{detected_modality.value.upper()}_INCOMPATIBLE] {scene_id} -> {requested_tool}: {reason_en}")


@dataclass
class HyperspectralCubeMetadata:
    """Metadata describing a contiguous hyperspectral datacube."""
    num_bands: int
    wavelengths_nm: List[float]
    fwhm_nm: Optional[List[float]] = None
    units: str = "nanometers"
    bad_bands_mask: Optional[List[bool]] = field(default_factory=list)

    def __post_init__(self):
        if not self.bad_bands_mask:
            self.bad_bands_mask = self.detect_water_vapor_absorption_bands(self.wavelengths_nm)

    @staticmethod
    def detect_water_vapor_absorption_bands(wavelengths_nm: List[float]) -> List[bool]:
        """Flags atmospheric water vapor absorption windows:
        - 1350 nm to 1450 nm
        - 1800 nm to 1950 nm
        - > 2450 nm
        """
        mask = []
        for wl in wavelengths_nm:
            is_bad = (1350.0 <= wl <= 1450.0) or (1800.0 <= wl <= 1950.0) or (wl >= 2450.0)
            mask.append(is_bad)
        return mask

    def find_closest_band_index(self, target_wavelength_nm: float, max_delta_nm: float = 15.0) -> Optional[int]:
        """Finds the band index closest to target wavelength within tolerance."""
        if not self.wavelengths_nm:
            return None
        closest_idx = min(range(len(self.wavelengths_nm)), key=lambda i: abs(self.wavelengths_nm[i] - target_wavelength_nm))
        delta = abs(self.wavelengths_nm[closest_idx] - target_wavelength_nm)
        if delta <= max_delta_nm:
            return closest_idx
        return None
