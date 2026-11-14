# -*- coding: utf-8 -*-
"""Modality Router and Tool Capability Enforcement.

Prevents invalid cross-modality tool execution (e.g. running optical equations on SAR
or calculating surface temperature from thermal-free sensors like Sentinel-2).
"""

from typing import Optional
from atyaf_core.discovery.models import SceneMetadata, SensorFamily
from atyaf_core.modalities.models import (
    ModalityCapabilityError,
    SensorModality,
)
from atyaf_core.modalities.sar import SAREngine
from atyaf_core.modalities.hyperspectral import HyperspectralEngine


class ModalityRouter:
    """Classifies scene modality and enforces scientific tool boundaries."""

    SAR_FAMILIES = {SensorFamily.SENTINEL_1, SensorFamily.ALOS_PALSAR}
    HYPERSPECTRAL_FAMILIES = {SensorFamily.ENMAP, SensorFamily.PRISMA, SensorFamily.EMIT}

    @classmethod
    def classify_modality(cls, metadata: SceneMetadata) -> SensorModality:
        """Determines the physical sensor modality from metadata."""
        family = metadata.sensor_family
        inst_upper = (metadata.instrument or "").upper()
        platform_upper = (metadata.platform or "").upper()

        if family in cls.SAR_FAMILIES or "SAR" in inst_upper or "C-SAR" in inst_upper:
            return SensorModality.SAR_RADAR

        if family in cls.HYPERSPECTRAL_FAMILIES or "HYPER" in inst_upper or "ENMAP" in platform_upper:
            return SensorModality.HYPERSPECTRAL

        if "ECOSTRESS" in platform_upper or "TIRS_ONLY" in inst_upper:
            return SensorModality.THERMAL

        return SensorModality.MULTISPECTRAL

    @classmethod
    def validate_tool_compatibility(
        cls,
        metadata: SceneMetadata,
        tool_name: str,
    ) -> SensorModality:
        """Validates that the requested tool is physically and scientifically applicable to the scene.
        
        Raises:
            ModalityCapabilityError: If the sensor modality is strictly incompatible with the tool.
        """
        modality = cls.classify_modality(metadata)
        norm_tool = tool_name.lower()

        # 1. SAR Modality Boundary: Never route SAR to optical or thermal tools
        if modality == SensorModality.SAR_RADAR:
            optical_or_thermal_tools = [
                "spectral_indices",
                "surface_temperature",
                "thermal_urban",
                "environmental_drought",
                "geological_analysis",
            ]
            if any(t in norm_tool for t in optical_or_thermal_tools):
                SAREngine.assert_optical_compatibility(
                    scene_id=metadata.scene_id,
                    instrument=metadata.instrument,
                    requested_tool=tool_name,
                )

        # 2. Thermal Absence Boundary: Sentinel-2 has no thermal channels
        if metadata.sensor_family == SensorFamily.SENTINEL_2:
            if "temperature" in norm_tool or "thermal" in norm_tool:
                reason_en = (
                    f"Sentinel-2 MSI lacks thermal infrared bands. Tool '{tool_name}' requires thermal measurements (Specification Section 2, 5)."
                )
                reason_ar = (
                    f"مستشعر Sentinel-2 MSI يفتقر إلى النطاقات الحرارية. الأداة '{tool_name}' تتطلب قياسات حرارية فعلية (البند 2 و5)."
                )
                raise ModalityCapabilityError(
                    scene_id=metadata.scene_id,
                    detected_modality=modality,
                    requested_tool=tool_name,
                    reason_en=reason_en,
                    reason_ar=reason_ar,
                )

        # 3. Hyperspectral L2 Gating for Geological / Mineral Unmixing
        if modality == SensorModality.HYPERSPECTRAL and "geological" in norm_tool:
            HyperspectralEngine.assert_l2_surface_reflectance(
                scene_id=metadata.scene_id,
                instrument=metadata.instrument,
                product_level=metadata.product_level.value,
                requested_tool=tool_name,
            )

        return modality
