# -*- coding: utf-8 -*-
"""ATIAF QGIS Processing Provider."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from qgis.core import QgsProcessingProvider
except ImportError:
    QgsProcessingProvider = object

from .algorithms.spectral_indices import SpectralIndicesAlgorithm
from .algorithms.surface_temperature import SurfaceTemperatureAlgorithm
from .algorithms.thermal_urban import ThermalUrbanAlgorithm
from .algorithms.environmental_drought import EnvironmentalDroughtAlgorithm
from .algorithms.geological_analysis import GeologicalAnalysisAlgorithm
from .algorithms.temporal_change import TemporalChangeAlgorithm


class ATIAFProcessingProvider(QgsProcessingProvider):
    """QGIS Processing provider for ATIAF scientific algorithms."""

    def id(self):
        return "atyaf"

    def name(self):
        return "ATIAF | أطياف"

    def longName(self):
        return "ATIAF — Advanced Thematic Imagery Analysis Framework (أطياف)"

    def loadAlgorithms(self):
        self.addAlgorithm(SpectralIndicesAlgorithm())
        self.addAlgorithm(SurfaceTemperatureAlgorithm())
        self.addAlgorithm(ThermalUrbanAlgorithm())
        self.addAlgorithm(EnvironmentalDroughtAlgorithm())
        self.addAlgorithm(GeologicalAnalysisAlgorithm())
        self.addAlgorithm(TemporalChangeAlgorithm())
