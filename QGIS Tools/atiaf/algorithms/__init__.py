# -*- coding: utf-8 -*-
"""ATIAF QGIS Processing Algorithms package."""

from .spectral_indices import SpectralIndicesAlgorithm
from .surface_temperature import SurfaceTemperatureAlgorithm
from .thermal_urban import ThermalUrbanAlgorithm
from .environmental_drought import EnvironmentalDroughtAlgorithm
from .geological_analysis import GeologicalAnalysisAlgorithm
from .temporal_change import TemporalChangeAlgorithm
from .geological_composites import GeologicalCompositesAlgorithm

__all__ = [
    "SpectralIndicesAlgorithm",
    "SurfaceTemperatureAlgorithm",
    "ThermalUrbanAlgorithm",
    "EnvironmentalDroughtAlgorithm",
    "GeologicalAnalysisAlgorithm",
    "TemporalChangeAlgorithm",
    "GeologicalCompositesAlgorithm",
]
